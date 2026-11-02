#!/usr/bin/env python3
"""Credential-safe, read-only inspection for Alibaba Cloud PAI."""

from __future__ import annotations

import argparse
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


class InspectionError(RuntimeError):
    """A sanitized error suitable for display."""


def emit(value: Any) -> None:
    json.dump(value, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def run_json(command: list[str], timeout: int = 45) -> Any:
    env = os.environ.copy()
    env["ALIBABA_CLOUD_CLI_AI_MODE"] = "1"
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        raise InspectionError("The read-only request timed out.") from exc
    if completed.returncode != 0:
        raise InspectionError(
            f"{command[1]} query failed without a usable response; verify the "
            "selected profile, region, and permissions."
        )
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise InspectionError(
            f"{command[1]} returned non-JSON output; run the official CLI "
            "directly for diagnostics."
        ) from exc
    if isinstance(result, dict) and (
        result.get("Success") is False
        or (result.get("Code") not in (None, 200, "200"))
    ):
        raise InspectionError(
            f"{command[1]} was denied or failed; check the region and read "
            "permissions for this resource."
        )
    return result


class Client:
    def __init__(self, args: argparse.Namespace) -> None:
        self.profile = args.profile
        self.region = args.region
        self.config_path = Path(args.config_path).expanduser()
        self.aliyun = shutil.which("aliyun")
        self.pai = shutil.which("pai")

    def api(self, product: str, action: str, arguments: list[str]) -> Any:
        if not self.aliyun:
            raise InspectionError("The official `aliyun` CLI is not installed.")
        return run_json(
            [
                self.aliyun,
                product,
                action,
                *arguments,
                "--profile",
                self.profile,
                "--region",
                self.region,
            ]
        )

    def profile_values(self) -> dict[str, Any]:
        try:
            config = json.loads(self.config_path.read_text())
        except FileNotFoundError as exc:
            raise InspectionError(
                "The Alibaba Cloud CLI configuration file is absent; configure "
                "the selected profile first."
            ) from exc
        except (OSError, json.JSONDecodeError) as exc:
            raise InspectionError(
                "The Alibaba Cloud CLI configuration could not be read safely."
            ) from exc

        for profile in config.get("profiles", []):
            if profile.get("name") == self.profile:
                return profile
        raise InspectionError(
            "The selected Alibaba Cloud CLI profile is not configured."
        )

    def pai_environment(self) -> dict[str, str]:
        env = os.environ.copy()
        profile = self.profile_values()
        access_key_id = profile.get("access_key_id")
        access_key_secret = profile.get("access_key_secret")
        if not access_key_id or not access_key_secret:
            raise InspectionError(
                "The selected Alibaba Cloud CLI profile has no usable static "
                "credential for PAI CLI execution."
            )
        env["PAI_ACCESS_KEY_ID"] = access_key_id
        env["PAI_ACCESS_KEY_SECRET"] = access_key_secret
        security_token = profile.get("sts_token")
        if security_token:
            env["PAI_SECURITY_TOKEN"] = security_token
        env["PAI_REGION"] = self.region
        return env

    def require_running(self, kind: str, target_id: str, pod: str | None) -> None:
        if kind == "dsw" and pod:
            raise InspectionError(
                "`--pod` applies only to DLC job execution; omit it for DSW."
            )
        if kind == "dlc":
            result = self.api(
                "pai-dlc",
                "get-job",
                [
                    "--job-id",
                    target_id,
                    "--cli-query",
                    "{Status:Status,Pods:Pods[].{PodId:PodId,Status:Status}}",
                ],
            )
        else:
            result = self.api(
                "pai-dsw",
                "get-instance",
                [
                    "--instance-id",
                    target_id,
                    "--cli-query",
                    "{Status:Status}",
                ],
            )
        status = result.get("Status")
        if status != "Running":
            raise InspectionError(
                f"The selected {kind.upper()} target is {status or 'not available'}; "
                "live filesystem inspection requires a running target."
            )
        if pod:
            running_pods = {
                item.get("PodId")
                for item in result.get("Pods", [])
                if item.get("Status") == "Running"
            }
            if pod not in running_pods:
                raise InspectionError(
                    "The selected pod is not running; choose a running pod from "
                    "the DLC job details."
                )

    def remote_python(
        self,
        kind: str,
        target_id: str,
        pod: str | None,
        code: str,
        arguments: list[str],
        timeout: int,
    ) -> Any:
        if not self.pai:
            raise InspectionError("The official `pai` CLI is not installed.")
        with tempfile.TemporaryDirectory(prefix="aliyun-pai-") as config_dir:
            command = [
                self.pai,
                "--config-dir",
                config_dir,
                "--region",
                self.region,
                kind,
            ]
            if kind == "dlc":
                command.extend(["job", "exec", target_id])
                if pod:
                    command.extend(["--pod", pod])
            else:
                command.extend(["instance", "exec", target_id])
            command.extend(
                [
                    "--timeout",
                    str(timeout),
                    "--",
                    "python3",
                    "-c",
                    code,
                    *arguments,
                ]
            )
            try:
                completed = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=timeout + 10,
                    env=self.pai_environment(),
                )
            except subprocess.TimeoutExpired as exc:
                raise InspectionError(
                    "The read-only command in the running PAI target timed out."
                ) from exc

        clean = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", completed.stdout)
        marker = "PAI_INSPECT_RESULT="
        for line in clean.splitlines():
            if line.startswith(marker):
                try:
                    return json.loads(line[len(marker) :])
                except json.JSONDecodeError as exc:
                    raise InspectionError(
                        "The running target returned malformed inspection data."
                    ) from exc
        raise InspectionError(
            "The running target did not return structured inspection data; "
            "verify the target is running and accessible."
        )


MOUNT_CODE = r"""
import json
mounts = []
with open("/proc/self/mountinfo") as stream:
    for line in stream:
        left, right = line.rstrip().split(" - ", 1)
        fields = left.split()
        kind, source = right.split()[:2]
        if (
            kind.startswith(("fuse.", "nfs", "lustre", "gpfs"))
            or "cpfs" in source.lower()
            or "nas" in source.lower()
        ):
            mounts.append({"path": fields[4], "type": kind})
print("PAI_INSPECT_RESULT=" + json.dumps({"mounts": mounts}))
"""


LS_CODE = r"""
import json
import os
import sys

mount_root = os.path.normpath(sys.argv[1])
requested = os.path.normpath(sys.argv[2])
limit = int(sys.argv[3])
if not os.path.isabs(requested):
    raise SystemExit("path must be absolute")
real_root = os.path.realpath(mount_root)
real_requested = os.path.realpath(requested)
if os.path.commonpath([real_root, real_requested]) != real_root:
    raise SystemExit("path escapes the configured mount root")

entries = []
truncated = False
with os.scandir(requested) as stream:
    for entry in stream:
        if len(entries) >= limit:
            truncated = True
            break
        if entry.is_symlink():
            kind = "symlink"
        elif entry.is_dir(follow_symlinks=False):
            kind = "directory"
        elif entry.is_file(follow_symlinks=False):
            kind = "file"
        else:
            kind = "other"
        item = {"name": entry.name, "type": kind}
        try:
            stat = entry.stat(follow_symlinks=False)
            item["size_bytes"] = stat.st_size
            item["mtime_epoch"] = stat.st_mtime
        except OSError:
            pass
        entries.append(item)
entries.sort(key=lambda item: (item["type"] != "directory", item["name"]))
print(
    "PAI_INSPECT_RESULT="
    + json.dumps(
        {
            "path": requested,
            "entries": entries,
            "truncated": truncated,
        }
    )
)
"""


STAT_CODE = r"""
import json
import os
import sys

mount_root = os.path.normpath(sys.argv[1])
requested = os.path.normpath(sys.argv[2])
if not os.path.isabs(requested):
    raise SystemExit("path must be absolute")
real_root = os.path.realpath(mount_root)
real_requested = os.path.realpath(requested)
if os.path.commonpath([real_root, real_requested]) != real_root:
    raise SystemExit("path escapes the configured mount root")

stat = os.statvfs(requested)
total = stat.f_frsize * stat.f_blocks
used = stat.f_frsize * (stat.f_blocks - stat.f_bfree)
available = stat.f_frsize * stat.f_bavail
print(
    "PAI_INSPECT_RESULT="
    + json.dumps(
        {
            "path": requested,
            "total_bytes": total,
            "used_bytes": used,
            "available_bytes": available,
            "used_percent": round((used / total) * 100, 3) if total else None,
        }
    )
)
"""


def validate_mount_root(value: str) -> str:
    root = posixpath.normpath(value)
    if not root.startswith("/") or root == ".." or "\x00" in root:
        raise InspectionError("The mount root must be an absolute POSIX path.")
    return root


def command_identity(client: Client, _: argparse.Namespace) -> None:
    result = client.api(
        "sts",
        "get-caller-identity",
        ["--cli-query", "IdentityType"],
    )
    emit({"authenticated": True, "identity_type": result})


def command_jobs(client: Client, args: argparse.Namespace) -> None:
    if not args.workspace_id:
        raise InspectionError("A workspace ID is required.")
    projection = (
        "{TotalCount:TotalCount,Jobs:Jobs[].{JobId:JobId,"
        "DisplayName:DisplayName,Status:Status,JobType:JobType,"
        "GmtCreateTime:GmtCreateTime,RequestGPU:RequestGPU,"
        "WorkspaceId:WorkspaceId}}"
    )
    emit(
        client.api(
            "pai-dlc",
            "list-jobs",
            [
                "--workspace-id",
                args.workspace_id,
                "--page-number",
                "1",
                "--page-size",
                str(args.limit),
                "--cli-query",
                projection,
            ],
        )
    )


def command_job(client: Client, args: argparse.Namespace) -> None:
    projection = (
        "{JobId:JobId,DisplayName:DisplayName,Status:Status,"
        "SubStatus:SubStatus,JobType:JobType,WorkspaceId:WorkspaceId,"
        "WorkspaceName:WorkspaceName,GmtCreateTime:GmtCreateTime,"
        "GmtRunningTime:GmtRunningTime,GmtFinishTime:GmtFinishTime,"
        "RequestCPU:RequestCPU,RequestGPU:RequestGPU,"
        "RequestMemory:RequestMemory,ResourceId:ResourceId,"
        "JobSpecs:JobSpecs[].{Type:Type,PodCount:PodCount,"
        "EcsSpec:EcsSpec,ResourceConfig:ResourceConfig,"
        "SystemDisk:SystemDisk,LocalMountSpecs:LocalMountSpecs},"
        "DataSources:DataSources[].{DataSourceId:DataSourceId,"
        "MountPath:MountPath,Uri:Uri},"
        "Pods:Pods[].{PodId:PodId,Status:Status,NodeName:NodeName}}"
    )
    emit(
        client.api(
            "pai-dlc",
            "get-job",
            ["--job-id", args.job_id, "--cli-query", projection],
        )
    )


def command_dsw_instances(client: Client, args: argparse.Namespace) -> None:
    if not args.workspace_id:
        raise InspectionError("A workspace ID is required.")
    projection = (
        "{TotalCount:TotalCount,Instances:Instances[].{"
        "InstanceId:InstanceId,InstanceName:InstanceName,Status:Status,"
        "EcsSpec:EcsSpec,ResourceId:ResourceId,"
        "CloudDisks:CloudDisks,Datasets:Datasets}}"
    )
    emit(
        client.api(
            "pai-dsw",
            "list-instances",
            [
                "--workspace-id",
                args.workspace_id,
                "--page-number",
                "1",
                "--page-size",
                str(args.limit),
                "--cli-query",
                projection,
            ],
        )
    )


def command_filesystems(client: Client, _: argparse.Namespace) -> None:
    projection = (
        "{TotalCount:TotalCount,"
        "FileSystems:FileSystems.FileSystem[].{"
        "FileSystemId:FileSystemId,Description:Description,"
        "FileSystemType:FileSystemType,ProtocolType:ProtocolType,"
        "StorageType:StorageType,Status:Status,Capacity:Capacity,"
        "MeteredSize:MeteredSize,RegionId:RegionId,ZoneId:ZoneId,"
        "MountTargets:MountTargets.MountTarget[].{"
        "MountTargetDomain:MountTargetDomain,Status:Status}}}"
    )
    emit(
        client.api(
            "nas",
            "describe-file-systems",
            [
                "--page-number",
                "1",
                "--page-size",
                "100",
                "--cli-query",
                projection,
            ],
        )
    )


def remote_target(args: argparse.Namespace) -> tuple[str, str | None]:
    return args.target_id, getattr(args, "pod", None)


def command_mounts(client: Client, args: argparse.Namespace) -> None:
    target_id, pod = remote_target(args)
    client.require_running(args.kind, target_id, pod)
    emit(
        client.remote_python(
            args.kind,
            target_id,
            pod,
            MOUNT_CODE,
            [],
            args.timeout,
        )
    )


def remote_path_args(args: argparse.Namespace) -> tuple[str, list[str]]:
    root = validate_mount_root(args.mount_root)
    remote_path = posixpath.normpath(args.path)
    if not remote_path.startswith("/") or "\x00" in remote_path:
        raise InspectionError("The remote path must be absolute.")
    if posixpath.commonpath([root, remote_path]) != root:
        raise InspectionError("The remote path escapes the configured mount root.")
    return root, [root, remote_path]


def command_ls(client: Client, args: argparse.Namespace) -> None:
    root, remote_arguments = remote_path_args(args)
    target_id, pod = remote_target(args)
    client.require_running(args.kind, target_id, pod)
    result = client.remote_python(
        args.kind,
        target_id,
        pod,
        LS_CODE,
        [*remote_arguments, str(args.limit)],
        args.timeout,
    )
    result["mount_root"] = root
    emit(result)


def command_stat(client: Client, args: argparse.Namespace) -> None:
    root, remote_arguments = remote_path_args(args)
    target_id, pod = remote_target(args)
    client.require_running(args.kind, target_id, pod)
    result = client.remote_python(
        args.kind,
        target_id,
        pod,
        STAT_CODE,
        remote_arguments,
        args.timeout,
    )
    result["mount_root"] = root
    emit(result)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only Alibaba Cloud PAI and mounted storage inspection. "
            "Credentials are loaded from an existing Alibaba Cloud CLI profile."
        )
    )
    parser.add_argument(
        "--profile",
        default=os.environ.get("ALIBABA_CLOUD_PROFILE", "pai-readonly"),
    )
    parser.add_argument(
        "--region",
        default=(
            os.environ.get("PAI_REGION")
            or os.environ.get("ALIBABA_CLOUD_REGION_ID")
            or "cn-hangzhou"
        ),
    )
    parser.add_argument(
        "--config-path",
        default=os.environ.get("ALIBABA_CLOUD_CONFIG_PATH", "~/.aliyun/config.json"),
    )
    parser.add_argument(
        "--workspace-id",
        default=os.environ.get("PAI_WORKSPACE_ID"),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    identity = subparsers.add_parser("identity", help="Verify the configured identity")
    identity.set_defaults(handler=command_identity)

    jobs = subparsers.add_parser("jobs", help="List DLC jobs")
    jobs.add_argument(
        "--workspace-id",
        default=argparse.SUPPRESS,
        help="Override the workspace ID set before the subcommand",
    )
    jobs.add_argument("--limit", type=int, choices=range(1, 101), default=20)
    jobs.set_defaults(handler=command_jobs)

    job = subparsers.add_parser("job", help="Show one DLC job")
    job.add_argument("job_id")
    job.set_defaults(handler=command_job)

    dsw = subparsers.add_parser("dsw-instances", help="List DSW instances")
    dsw.add_argument(
        "--workspace-id",
        default=argparse.SUPPRESS,
        help="Override the workspace ID set before the subcommand",
    )
    dsw.add_argument("--limit", type=int, choices=range(1, 101), default=100)
    dsw.set_defaults(handler=command_dsw_instances)

    filesystems = subparsers.add_parser(
        "filesystems", help="List NAS and CPFS file systems"
    )
    filesystems.set_defaults(handler=command_filesystems)

    mounts = subparsers.add_parser(
        "mounts", help="Show storage mounted in a running DLC or DSW target"
    )
    mounts.add_argument("target_id")
    mounts.add_argument("--kind", choices=("dlc", "dsw"), default="dlc")
    mounts.add_argument("--pod")
    mounts.add_argument("--timeout", type=int, default=30)
    mounts.set_defaults(handler=command_mounts)

    ls = subparsers.add_parser(
        "ls", help="List one directory in a mounted file system"
    )
    ls.add_argument("target_id")
    ls.add_argument("path")
    ls.add_argument("--kind", choices=("dlc", "dsw"), default="dlc")
    ls.add_argument("--pod")
    ls.add_argument(
        "--mount-root",
        default=os.environ.get("PAI_STORAGE_MOUNT", "/cpfs01"),
    )
    ls.add_argument("--limit", type=int, choices=range(1, 1001), default=200)
    ls.add_argument("--timeout", type=int, default=30)
    ls.set_defaults(handler=command_ls)

    stat = subparsers.add_parser(
        "stat", help="Read live capacity from a mounted file system"
    )
    stat.add_argument("target_id")
    stat.add_argument("path")
    stat.add_argument("--kind", choices=("dlc", "dsw"), default="dlc")
    stat.add_argument("--pod")
    stat.add_argument(
        "--mount-root",
        default=os.environ.get("PAI_STORAGE_MOUNT", "/cpfs01"),
    )
    stat.add_argument("--timeout", type=int, default=30)
    stat.set_defaults(handler=command_stat)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    client = Client(args)
    try:
        args.handler(client, args)
    except InspectionError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

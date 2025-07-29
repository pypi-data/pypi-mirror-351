# Copyright 2025 © BeeAI a Series of LF Projects, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import sys
import shutil
import time
from typing import Optional
import base64
import typing
import importlib.resources

from beeai_cli.api import wait_for_api
import typer
import kr8s.asyncio
import kr8s.asyncio.objects
import yaml

from beeai_cli import Configuration
from beeai_cli.console import console
from beeai_cli.async_typer import AsyncTyper
from beeai_cli.utils import VMDriver, run_command

app = AsyncTyper()

configuration = Configuration()

HelmChart = kr8s.asyncio.objects.new_class(
    kind="HelmChart",
    version="helm.cattle.io/v1",
    namespaced=True,
)


def _lima_yaml(k3s_port: int = 16443, beeai_port: int = 8333, phoenix_port: int = 6006) -> str:
    return f"""minimumLimaVersion: 1.1.0

base: template://_images/ubuntu-lts

mounts:
- location: "~/.beeai"
  mountPoint: "/beeai"

containerd:
  system: false
  user: false

provision:
- mode: system
  script: |
    #!/bin/sh
    if [ ! -d /var/lib/rancher/k3s ]; then
      curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server --write-kubeconfig-mode 644 --https-listen-port={k3s_port}" sh -
    fi
- mode: system
  script: |
    #!/bin/sh
    until kubectl get configmap coredns -n kube-system >/dev/null 2>&1; do
      sleep 2
    done
    TMP=$(mktemp -d)
    HOST_IP=$(dig +noall +short host.lima.internal)
    kubectl get configmap coredns -n kube-system -o yaml >$TMP/coredns.yaml
    if ! grep -q "host.docker.internal" $TMP/coredns.yaml; then
      awk -v ip="$HOST_IP" '/^  NodeHosts: \|/{{print; print "    " ip " host.docker.internal"; next}}1' $TMP/coredns.yaml >$TMP/coredns-patched.yaml
      kubectl apply -f $TMP/coredns-patched.yaml
      kubectl -n kube-system rollout restart deployment coredns
    fi

probes:
- script: |
    #!/bin/bash
    set -eux -o pipefail
    if ! timeout 30s bash -c "until test -f /etc/rancher/k3s/k3s.yaml; do sleep 3; done"; then
      echo >&2 "k3s is not running yet"
      exit 1
    fi

copyToHost:
- guest: "/etc/rancher/k3s/k3s.yaml"
  host: "{{{{.Dir}}}}/copied-from-guest/kubeconfig.yaml"
  deleteOnStop: true

portForwards:
  - guestPort: 31833
    hostPort: {beeai_port}
  - guestPort: 31606
    hostPort: {phoenix_port}"""


def _validate_driver(vm_driver: VMDriver | None) -> VMDriver:
    match vm_driver:
        case None:
            if shutil.which("limactl"):
                vm_driver = VMDriver.lima
            elif shutil.which("docker"):
                vm_driver = VMDriver.docker
            else:
                console.print("[red]Error: Neither limactl nor docker found. Please install one of them.[/red]")
                sys.exit(1)
        case VMDriver.lima:
            if not shutil.which("limactl"):
                console.print("[red]Error: limactl not found. Please install Lima.[/red]")
                sys.exit(1)
        case VMDriver.docker:
            if not shutil.which("docker"):
                console.print("[red]Error: docker not found. Please install Docker.[/red]")
                sys.exit(1)
    return vm_driver


def _get_platform_status(vm_driver: VMDriver, vm_name: str) -> str | None:
    try:
        match vm_driver:
            case VMDriver.lima:
                result = run_command(
                    ["limactl", "--tty=false", "list", "--format=json"],
                    "Looking for existing BeeAI platform",
                    env={"LIMA_HOME": str(configuration.lima_home)},
                )
                return next(
                    (
                        status["status"].lower() if "status" in status else None
                        for line in result.stdout.split("\n")
                        if line
                        if (status := json.loads(line))
                        if status.get("name") == vm_name
                    ),
                    None,
                )
            case VMDriver.docker:
                result = run_command(
                    ["docker", "inspect", vm_name],
                    "Looking for existing BeeAI platform",
                    check=False,
                )
                return json.loads(result.stdout)[0]["State"]["Status"].lower()
    except Exception:
        return None


@app.command("start")
async def start(
    set_values_list: typing.Annotated[
        list[str],
        typer.Option(
            "--set",
            help="Set Helm chart values using <key>=<value> syntax, like: --set image.tag=local",
            default_factory=list,
        ),
    ],
    vm_name: typing.Annotated[str, typer.Option(hidden=True)] = "beeai-platform",
    import_images: typing.Annotated[
        list[str],
        typer.Option(
            "--import",
            help="Import an image from a local Docker CLI into BeeAI platform",
        ),
    ] = [],
    telemetry_sharing: bool = typer.Option(True, help="Control the sharing of telemetry data with the BeeAI team"),
    vm_driver: typing.Annotated[
        Optional[VMDriver], typer.Option(hidden=True, help="Platform driver: lima (VM) or docker (container)")
    ] = None,
    k3s_port: typing.Annotated[int, typer.Option(hidden=True)] = 16443,
    beeai_port: typing.Annotated[int, typer.Option(hidden=True)] = 8333,
    phoenix_port: typing.Annotated[int, typer.Option(hidden=True)] = 6006,
):
    """Start BeeAI platform."""
    vm_driver = _validate_driver(vm_driver)

    # Stage 0: Clean up legacy Brew services
    run_command(
        ["brew", "services", "stop", "beeai"],
        "Cleaning up legacy BeeAI service",
        check=False,
        ignore_missing=True,
    )
    run_command(
        ["brew", "services", "stop", "arize-phoenix"],
        "Cleaning up legacy Arize Phoenix service",
        check=False,
        ignore_missing=True,
    )

    # Stage 1: Start VM
    configuration.home.mkdir(exist_ok=True)
    status = _get_platform_status(vm_driver, vm_name)
    if not status:
        templates_dir = configuration.lima_home / "_templates"
        if vm_driver == VMDriver.lima:
            templates_dir.mkdir(parents=True, exist_ok=True)
            templates_dir.joinpath(f"{vm_name}.yaml").write_text(
                _lima_yaml(k3s_port=k3s_port, beeai_port=beeai_port, phoenix_port=phoenix_port)
            )
        run_command(
            {
                VMDriver.lima: [
                    "limactl",
                    "--tty=false",
                    "start",
                    templates_dir / f"{vm_name}.yaml",
                    f"--name={vm_name}",
                ],
                VMDriver.docker: [
                    "docker",
                    "run",
                    "--privileged",
                    f"--name={vm_name}",
                    f"--hostname={vm_name}",
                    "-p",
                    f"{k3s_port}:{k3s_port}",
                    "-p",
                    f"{beeai_port}:31833",
                    "-p",
                    f"{phoenix_port}:31606",
                    "-v",
                    f"{configuration.home}:/beeai",
                    "-d",
                    "rancher/k3s:v1.33.0-k3s1",
                    "--",
                    "server",
                    "--write-kubeconfig-mode=644",
                    f"--https-listen-port={k3s_port}",
                ],
            }[vm_driver],
            "Creating BeeAI platform",
            env={"LIMA_HOME": str(configuration.lima_home)},
        )
    elif status != "running":
        run_command(
            {
                VMDriver.lima: ["limactl", "--tty=false", "start", vm_name],
                VMDriver.docker: ["docker", "start", vm_name],
            }[vm_driver],
            "Starting BeeAI platform",
            env={"LIMA_HOME": str(configuration.lima_home)},
        )
    else:
        console.print("Updating an existing BeeAI platform instance.")

    if vm_driver == VMDriver.lima:
        run_command(
            ["limactl", "--tty=false", "start-at-login", vm_name],
            "Configuring BeeAI platform",
            env={"LIMA_HOME": str(configuration.lima_home)},
        )

    if vm_driver == VMDriver.docker:
        for _ in range(10):
            with console.status("Waiting for k3s to start...", spinner="dots"):
                time.sleep(2)
            status = _get_platform_status(vm_driver, vm_name)
            if status != "running":
                console.print("[red]Error: k3s crashed when starting up.[/red]")
                sys.exit(1)

            if (
                run_command(
                    ["docker", "exec", vm_name, "test", "-f", "/etc/rancher/k3s/k3s.yaml"],
                    message="Checking if k3s is running",
                    check=False,
                ).returncode
                == 0
            ):
                break
        else:
            console.print("[red]Error: Timed out waiting for kubeconfig: k3s probably failed to start.[/red]")
            sys.exit(1)
        kubeconfig = configuration.get_kubeconfig(vm_driver=vm_driver, vm_name=vm_name)
        kubeconfig.parent.mkdir(parents=True, exist_ok=True)
        run_command(
            ["docker", "cp", f"{vm_name}:/etc/rancher/k3s/k3s.yaml", str(kubeconfig)],
            "Copying Kubernetes configuration",
        )

    # Stage 2: Import images
    for image in import_images:
        await import_image(image, vm_name=vm_name, vm_driver=vm_driver)

    # Stage 3: Deploy HelmChart
    try:
        with console.status("Applying HelmChart to Kubernetes...", spinner="dots"):
            helm_chart = HelmChart(
                {
                    "metadata": {
                        "name": "beeai",
                        "namespace": "default",
                    },
                    "spec": {
                        "chartContent": base64.b64encode(
                            (importlib.resources.files("beeai_cli") / "data" / "helm-chart.tgz").read_bytes()
                        ).decode(),
                        "targetNamespace": "beeai",
                        "createNamespace": True,
                        "valuesContent": yaml.dump(
                            {
                                "externalRegistries": {
                                    "public_github": "https://github.com/i-am-bee/beeai-platform@release-v0.2.0#path=agent-registry.yaml"
                                },
                                "encryptionKey": "Ovx8qImylfooq4-HNwOzKKDcXLZCB3c_m0JlB9eJBxc=",  # Dummy key for local use
                                "features": {"uiNavigation": True},
                                "auth": {"enabled": False},
                                "telemetry": {"sharing": telemetry_sharing},
                            }
                        ),
                        "set": {key: value for key, value in (value.split("=", 1) for value in set_values_list)},
                    },
                },
                api=await kr8s.asyncio.api(
                    kubeconfig=configuration.get_kubeconfig(vm_driver=vm_driver, vm_name=vm_name)
                ),
            )
            if await helm_chart.exists():
                await helm_chart.patch(helm_chart.raw)
            else:
                await helm_chart.create()
    except Exception as e:
        import traceback

        traceback.print_exc()
        console.print(f"[red]Error applying HelmChart: {e}[/red]")
        sys.exit(1)

    with console.status("Waiting for BeeAI platform to be ready...", spinner="dots"):
        await wait_for_api()

    console.print("[green]BeeAI platform started successfully![/green]")


@app.command("stop")
async def stop(
    vm_name: typing.Annotated[str, typer.Option(hidden=True)] = "beeai-platform",
    vm_driver: typing.Annotated[
        Optional[VMDriver], typer.Option(hidden=True, help="Platform driver: lima (VM) or docker (container)")
    ] = None,
):
    """Stop BeeAI platform."""
    vm_driver = _validate_driver(vm_driver)
    status = _get_platform_status(vm_driver, vm_name)
    if not status:
        console.print("BeeAI platform not found. Nothing to stop.")
        return
    if status != "running":
        console.print("BeeAI platform is not running. Nothing to stop.")
        return
    run_command(
        {
            VMDriver.lima: ["limactl", "--tty=false", "stop", vm_name],
            VMDriver.docker: ["docker", "stop", vm_name],
        }[vm_driver],
        "Stopping BeeAI VM",
        env={"LIMA_HOME": str(configuration.lima_home)},
    )
    console.print("[green]BeeAI platform stopped successfully.[/green]")


@app.command("delete")
async def delete(
    vm_name: typing.Annotated[str, typer.Option(hidden=True)] = "beeai-platform",
    vm_driver: typing.Annotated[
        Optional[VMDriver], typer.Option(hidden=True, help="Platform driver: lima (VM) or docker (container)")
    ] = None,
):
    """Delete BeeAI platform."""
    vm_driver = _validate_driver(vm_driver)
    status = _get_platform_status(vm_driver, vm_name)
    if not status:
        console.print("BeeAI VM not found. Nothing to delete.")
        return
    run_command(
        {
            VMDriver.lima: ["limactl", "--tty=false", "delete", "--force", vm_name],
            VMDriver.docker: ["docker", "rm", "--force", vm_name],
        }[vm_driver],
        "Deleting BeeAI platform",
        env={"LIMA_HOME": str(configuration.lima_home)},
    )
    console.print("[green]BeeAI platform deleted successfully.[/green]")


@app.command("import")
async def import_image(
    tag: typing.Annotated[str, typer.Argument(help="Docker image tag to import")],
    vm_name: typing.Annotated[str, typer.Option(hidden=True)] = "beeai-platform",
    vm_driver: typing.Annotated[
        Optional[VMDriver], typer.Option(hidden=True, help="Platform driver: lima (VM) or docker (container)")
    ] = None,
):
    """Import a local docker image into the BeeAI platform."""
    driver = _validate_driver(vm_driver)
    run_command(["bash", "-c", "rm -f ~/.beeai/images/*"], "Removing temporary files")
    image_path = Configuration().home / "images" / (tag.replace("/", "_") + ".tar")
    image_path.parent.mkdir(parents=True, exist_ok=True)
    run_command(
        ["docker", "image", "save", "-o", str(image_path), tag],
        "Exporting images from Docker",
    )
    run_command(
        {
            VMDriver.lima: ["limactl", "--tty=false", "shell", vm_name, "--"],
            VMDriver.docker: ["docker", "exec", vm_name],
        }[driver]
        + [
            "/bin/sh",
            "-c",
            f'for img in /beeai/images/*; do {"sudo" if vm_driver == VMDriver.lima else ""} ctr images import "$img"; done',
        ],
        "Importing images into BeeAI platform",
        env={"LIMA_HOME": str(Configuration().lima_home)},
        cwd="/",
    )
    run_command(["/bin/sh", "-c", "rm -f ~/.beeai/images/*"], "Removing temporary files")

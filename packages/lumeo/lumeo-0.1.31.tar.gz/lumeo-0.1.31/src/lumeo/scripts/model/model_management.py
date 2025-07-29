"""
# Connects to all gateways in the JSON file over SSH.
# Runs the specified command inside the gateway container for each combination of gateway and model in the config.
# MODEL_ID argument is replaced with the actual model ID from the config file.
#
# Examples:
# $ pipx run --spec . --no-cache lumeo-model-management config.json engine-cache list --model-id MODEL_ID
# $ pipx run --spec . --no-cache lumeo-model-management config.json engine-cache create --model-id MODEL_ID
# $ pipx run --spec . --no-cache lumeo-model-management config.json engine-cache create --model-id MODEL_ID --force
#
# JSON format:
# {
#   "gateways": [
#     {
#       "ssh": "root@gateway_host",
#       "container_name": "lumeo-gateway-container"
#     }
#   ],
#   "models": [
#     {
#       "id": "00000000-0000-0000-0000-000000000000"
#     }
#   ]
# }
"""

import argparse
import getpass
import json
import requests
import subprocess
import concurrent.futures
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.live import Live
from queue import Queue, Empty

# Status emoji constants
STATUS_IN_PROGRESS = "⏳"
STATUS_SUCCESS = "✓"
STATUS_ERROR = "✗"

# Create two separate consoles - one for the live table and one for error messages
table_console = Console()
error_console = Console()


@dataclass
class TaskStatus:
    gateway_ssh: str
    model_id: str
    log_file: str
    status: str = STATUS_IN_PROGRESS
    result: Optional[str] = None
    error: Optional[str] = None

    def update_status(
        self, status: str, result: Optional[str] = None, error: Optional[str] = None
    ):
        self.status = status
        self.result = result
        self.error = error


class TaskTable:
    def __init__(self, tasks: List[TaskStatus], update_queue: Queue):
        self.tasks = tasks
        self.update_queue = update_queue
        self.table = Table(show_header=True, header_style="bold")
        self.table.add_column("Status", justify="center", width=8)
        self.table.add_column("Gateway", width=30)
        self.table.add_column("Model ID", width=36)
        self.table.add_column("Log File")
        self.live = Live(self.table, refresh_per_second=4, console=table_console)
        self.live.start()
        self._update_table()
        self._stop = False

    def _update_table(self):
        new_table = Table(show_header=True, header_style="bold")
        new_table.add_column("Status", justify="center", width=8)
        new_table.add_column("Gateway", width=30)
        new_table.add_column("Model ID", width=36)
        new_table.add_column("Log File")

        status_colors = {
            STATUS_IN_PROGRESS: "yellow",
            STATUS_SUCCESS: "green",
            STATUS_ERROR: "red",
        }

        for task in self.tasks:
            new_table.add_row(
                f"[{status_colors.get(task.status, 'white')}]{task.status}[/]",
                task.gateway_ssh,
                task.model_id,
                f"less -R {task.log_file}",
            )

        self.table = new_table
        self.live.update(self.table)

    def update(self):
        self._update_table()

    def stop(self):
        self._stop = True
        self._update_table()
        self.live.stop()


def get_log_file_path(gateway_ssh: str, model_id: str) -> str:
    """Generate a log file path for a specific gateway and model combination."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    gateway_name = (
        "local"
        if gateway_ssh == "local"
        else gateway_ssh.split("@")[1].replace(".", "_")
    )
    log_dir = "model_management_logs"
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, f"{gateway_name}_{model_id}_{timestamp}.log")


def log_to_file(log_file: str, message: str) -> None:
    """Write a message to the log file."""
    with open(log_file, "a") as f:
        f.write(f"{message}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="JSON file with gateways and models")
    parser.add_argument("command", help="Command to execute (e.g., engine-cache)")
    parser.add_argument(
        "args", nargs=argparse.REMAINDER, help="Additional arguments for the command"
    )
    args = parser.parse_args()

    try:
        with open(args.config) as f:
            config = json.load(f)

        environment, api_token = login()
        if not environment or not api_token:
            return

        # Create task status objects and log files dictionary in one pass
        tasks = []
        model_log_files = {}
        for gateway in config["gateways"]:
            for model in config["models"]:
                log_file = get_log_file_path(gateway["ssh"], model["id"])
                tasks.append(TaskStatus(gateway["ssh"], model["id"], log_file))
                model_log_files[(gateway["ssh"], model["id"])] = log_file

        update_queue = Queue()
        task_table = TaskTable(tasks, update_queue)

        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(
                        process_gateway,
                        gateway,
                        config["models"],
                        environment,
                        api_token,
                        [args.command] + args.args,
                        update_queue,
                        model_log_files,
                    )
                    for gateway in config["gateways"]
                ]

                while futures:
                    try:
                        gateway_ssh, model_id, status = update_queue.get(timeout=0.5)
                        task = next(
                            t
                            for t in tasks
                            if t.gateway_ssh == gateway_ssh and t.model_id == model_id
                        )
                        task.update_status(status)
                        task_table.update()
                    except Empty:
                        futures = [f for f in futures if not f.done()]

        except KeyboardInterrupt:
            print("\nInterrupted by user. Shutting down gracefully...")
            # Cancel all running futures
            for future in futures:
                future.cancel()
            # Wait for all futures to complete
            concurrent.futures.wait(futures)
            # Update all in-progress tasks to error status
            for task in tasks:
                if task.status == STATUS_IN_PROGRESS:
                    task.update_status(
                        STATUS_ERROR, error="Operation interrupted by user"
                    )
                    log_to_file(task.log_file, "Operation interrupted by user")
            task_table.update()

        finally:
            update_queue.put(None)
            task_table.stop()

            # Print logs only for failed tasks
            failed_tasks = [task for task in tasks if task.status == STATUS_ERROR]
            if failed_tasks:
                print("\n=== Failed Tasks Logs ===\n")
                for task in failed_tasks:
                    print(f"\n{'='*80}")
                    print(f"Log for Gateway: {task.gateway_ssh}")
                    print(f"Model ID: {task.model_id}")
                    print(f"Log file: {task.log_file}")
                    print(f"{'='*80}\n")
                    try:
                        with open(task.log_file, "r") as f:
                            print(f.read())
                    except Exception as e:
                        print(f"Error reading log file: {e}")
                    print("\n")

    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        return 1

    return 0


def process_gateway(
    gateway: Dict[str, str],
    models: List[Dict[str, str]],
    environment: str,
    api_token: str,
    command: List[str],
    update_queue: Queue,
    model_log_files: Dict[Tuple[str, str], str],
) -> None:
    """Process a single gateway with all its models."""
    docker_base = [
        "docker",
        "exec",
        "--env",
        f"LUMEO_ENVIRONMENT={environment}",
        "--env",
        f"LUMEO_API_KEY={api_token}",
        "--env",
        "RUST_LOG=info",
        gateway["container_name"],
        "lumeod",
    ]

    if gateway["ssh"] != "local":
        docker_base = ["ssh", gateway["ssh"]] + docker_base

    for model in models:
        log_file = model_log_files[(gateway["ssh"], model["id"])]
        log_to_file(
            log_file,
            f"###\n### Running command on {gateway['ssh']}. Model ID: {model['id']}\n###",
        )

        try:
            # Print lumeod version
            version_cmd = docker_base + ["--version"]
            result = subprocess.run(
                version_cmd, check=True, capture_output=True, text=True
            )
            log_to_file(log_file, result.stdout)

            # Run the model command
            model_cmd = (
                docker_base
                + ["model"]
                + [model["id"] if arg == "MODEL_ID" else arg for arg in command]
            )
            result = subprocess.run(
                model_cmd, check=True, capture_output=True, text=True
            )
            log_to_file(log_file, result.stdout)
            update_queue.put((gateway["ssh"], model["id"], STATUS_SUCCESS))

        except subprocess.CalledProcessError as e:
            log_to_file(log_file, f"Error: {e}\nstdout: {e.stdout}\nstderr: {e.stderr}")
            update_queue.put((gateway["ssh"], model["id"], STATUS_ERROR))
        except Exception as e:
            log_to_file(log_file, f"Unexpected error: {e}")
            update_queue.put((gateway["ssh"], model["id"], STATUS_ERROR))


def login() -> Tuple[Optional[str], Optional[str]]:
    try:
        environment = input("Lumeo environment (d/s/p): ").lower()

        environments = {
            "d": "development",
            "s": "staging",
            "p": "production",
        }

        if environment not in environments:
            print(f"Invalid environment: {environment}")
            return None, None

        environment = environments[environment]
        base_url = {
            "development": "https://api-dev.lumeo.com",
            "staging": "https://api-staging.lumeo.com",
            "production": "https://api.lumeo.com",
        }[environment]

        email = input("Email: ")
        password = getpass.getpass("Password: ")

        response = requests.post(
            f"{base_url}/v1/internal/auth/login",
            json={"email": email, "password": password},
        )

        if response.status_code != 200:
            print(f"Error: {response.status_code} {response.reason}")
            return None, None

        return environment, response.json()["token"]

    except KeyboardInterrupt:
        print("\nLogin interrupted by user.")
        return None, None
    except Exception as e:
        print(f"\nLogin error: {e}")
        return None, None


if __name__ == "__main__":
    exit(main())

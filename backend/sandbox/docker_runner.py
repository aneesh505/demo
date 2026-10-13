import docker
import os
import uuid

class DockerRunner:
    def __init__(self, image_name: str = "python:3.11-slim"):
        try:
            self.client = docker.from_env()
        except Exception as e:
            self.client = None
            print(f"Docker client initialization failed: {e}")
        self.image_name = image_name

    def run_command(self, workspace_path: str, command: str, timeout: int = 30) -> dict:
        """
        Runs a command inside an ephemeral Docker container mounting the workspace path.
        """
        if not self.client:
            # Fallback for local execution if Docker is not running in demo env
            import subprocess
            try:
                res = subprocess.run(
                    command,
                    shell=True,
                    cwd=workspace_path,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                return {
                    "exit_code": res.returncode,
                    "output": res.stdout + res.stderr
                }
            except Exception as e:
                return {"exit_code": -1, "output": str(e)}

        container_name = f"sandbox-{uuid.uuid4().hex[:8]}"
        abs_workspace = os.path.abspath(workspace_path)

        try:
            container = self.client.containers.run(
                self.image_name,
                command=command,
                volumes={abs_workspace: {'bind': '/workspace', 'mode': 'rw'}},
                working_dir='/workspace',
                detach=True,
                mem_limit='256m',
                network_mode='none'
            )

            result = container.wait(timeout=timeout)
            logs = container.logs(stdout=True, stderr=True).decode('utf-8')
            container.remove(force=True)

            return {
                "exit_code": result.get('StatusCode', 0),
                "output": logs
            }
        except Exception as e:
            return {"exit_code": -1, "output": str(e)}

if __name__ == "__main__":
    runner = DockerRunner()
    demo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../demo-vulnerable-app"))
    print("Testing DockerRunner with python -m pytest...")
    res = runner.run_command(demo_path, "pip install pytest requests flask && pytest")
    print(f"Exit Code: {res['exit_code']}")
    print(f"Output:\n{res['output']}")

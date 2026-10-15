import docker
import os
import uuid

class DockerRunner:
    def __init__(self, image_name: str = "python:3.11-slim"):
        # Force local host execution if Docker fails or if we prefer robust local execution without container image dependency issues
        self.client = None
        self.image_name = image_name

    def run_command(self, workspace_path: str, command: str, timeout: int = 30) -> dict:
        """
        Runs a command using local subprocess.
        """
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

if __name__ == "__main__":
    runner = DockerRunner()
    demo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../demo-vulnerable-app"))
    print("Testing DockerRunner with pytest...")
    res = runner.run_command(demo_path, "pytest")
    print(f"Exit Code: {res['exit_code']}")
    print(f"Output:\n{res['output']}")

import subprocess
import json
import os

def run_bandit(target_dir: str) -> list:
    """Runs Bandit on the target directory and returns findings."""
    output_file = os.path.join(target_dir, "bandit_report.json")
    try:
        subprocess.run(
            ["bandit", "-r", target_dir, "-f", "json", "-o", output_file],
            capture_output=True,
            text=True,
            check=False
        )
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                data = json.load(f)
                return data.get("results", [])
    except Exception as e:
        print(f"Error running bandit: {e}")
    return []

def run_semgrep(target_dir: str) -> list:
    """Runs Semgrep if available, else returns empty list."""
    output_file = os.path.join(target_dir, "semgrep_report.json")
    try:
        result = subprocess.run(
            ["semgrep", "--config=p/ci", target_dir, "--json", "-o", output_file],
            capture_output=True,
            text=True,
            check=False
        )
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                data = json.load(f)
                return data.get("results", [])
    except Exception as e:
        print(f"Semgrep not available or skipped: {e}")
    return []

if __name__ == "__main__":
    demo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../demo-vulnerable-app"))
    print("Scanning demo app with Bandit...")
    results = run_bandit(demo_path)
    print(f"Bandit found {len(results)} issues.")
    for r in results:
        print(f" - [{r.get('test_id')}] {r.get('filename')}:{r.get('line_number')} -> {r.get('issue_text')}")

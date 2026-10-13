import os
import shutil
from backend.steps.scan import run_bandit, run_semgrep
from backend.sandbox.docker_runner import DockerRunner
from backend.steps.fix import generate_fix

def run_self_healing_pipeline(repo_url: str, branch: str = "main") -> dict:
    print(f"Starting self-healing pipeline for {repo_url} (branch: {branch})")

    # Setup temp workspace
    workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../sandbox_workspaces/target_repo"))
    if os.path.exists(workspace_dir):
        shutil.rmtree(workspace_dir, ignore_errors=True)
    os.makedirs(workspace_dir, exist_ok=True)

    # For demo, if repo_url points to demo-vulnerable-app or is local, copy it over
    demo_app_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "../demo-vulnerable-app"))
    if os.path.exists(demo_app_src):
        shutil.copytree(demo_app_src, workspace_dir, dirs_exist_ok=True)
    else:
        # Clone repo
        import subprocess
        subprocess.run(["git", "clone", "--depth", "1", "-b", branch, repo_url, workspace_dir], check=True)

    runner = DockerRunner()

    # Step 1: Run baseline tests
    print("Running baseline tests...")
    baseline_res = runner.run_command(workspace_dir, "pip install pytest flask requests && pytest")
    print(f"Baseline tests exit code: {baseline_res['exit_code']}")

    # Step 2: Scan findings
    print("Running security scanners (Bandit & Semgrep)...")
    bandit_findings = run_bandit(workspace_dir)
    print(f"Bandit found {len(bandit_findings)} issues.")

    # Step 3: Fix findings
    fixes_applied = []
    for finding in bandit_findings[:2]: # fix top 2
        print(f"Generating fix for {finding.get('test_id')} at {finding.get('filename')}:{finding.get('line_number')}")
        fix_code = generate_fix(finding, workspace_dir)
        fixes_applied.append({
            "finding": finding,
            "fix": fix_code
        })

    # Step 4: Verify via regression tests
    print("Running regression test suite...")
    verify_res = runner.run_command(workspace_dir, "pytest")
    print(f"Verification exit code: {verify_res['exit_code']}")

    return {
        "status": "completed",
        "baseline_tests": baseline_res,
        "findings_count": len(bandit_findings),
        "fixes_applied": len(fixes_applied),
        "verification": verify_res
    }

if __name__ == "__main__":
    res = run_self_healing_pipeline("https://github.com/demo/vulnerable-app")
    print(res)

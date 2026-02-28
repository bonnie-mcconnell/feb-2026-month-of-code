import subprocess
import shutil

def verify_docker_build() -> None:
    if not shutil.which("docker"):
        print("Docker not found; skipping Docker build verification.")
        return

    result = subprocess.run(
        ["docker", "build", "."],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise SystemExit("Docker build failed.")
    print("Docker build succeeded.")
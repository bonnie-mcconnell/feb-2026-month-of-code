import subprocess


def verify_docker_build() -> None:
    result = subprocess.run(
        ["docker", "build", "."],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise SystemExit("Docker build failed.")
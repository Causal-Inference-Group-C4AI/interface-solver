import docker
from pathlib import Path

from utils._enums import FilePaths, DockerImages


def run_docker_task(image_name, script, args=None):
    client = docker.from_env()
    command = ["python3", script]
    if args:
        command.extend(args)
    
    try:
        client.containers.run(
            image=image_name,
            command=command,
            volumes={str(Path.cwd()): {"bind": "/app", "mode": "rw"}},
            working_dir="/app",
            remove=True,
        )
    except docker.errors.ContainerError as e:
        print(f"Error running container: {e}")
        raise
    except docker.errors.ImageNotFound as e:
        print(f"Image not found: {image_name}")
        raise
    except docker.errors.APIError as e:
        print(f"API error: {e}")
        raise


def process_input(file_path, output_path):
    run_docker_task(
        DockerImages.INPUT_PROCESSOR_DOCKER_IMAGE.value,
        FilePaths.INPUT_PROCESSOR_SCRIPT.value,
        args=["--output", output_path, "--input", file_path]
    )

# Other functions remain the same, reusing `run_docker_task` where needed.

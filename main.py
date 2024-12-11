import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from utils._enums import DirectoryPaths, FilePaths, Solvers
from utils.data_cleaner import DataCleaner
from utils.general_utilities import (configure_environment,
                                     input_parse_arguments, log_solver_error)
from utils.output_writer import OutputWriterOverview
from utils.validator import Validator
from utils.general_utilities import configure_environment, input_parse_arguments, log_solver_error, get_common_data
from utils.solver_error import TimedOutError

def run_task(script, env_path=None, args=None, time_limit=None):
    """Run a Python script in a specific virtual environment."""
    python_executable = f"{env_path}/bin/python3" if env_path else "python3"
    command = [python_executable, script, *args]
    if args:
        command.extend(args)
    try:
        subprocess.run(command, cwd="./", check=True, timeout=time_limit)
    except subprocess.TimeoutExpired as e:
        raise TimedOutError(time_limit)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error running task {script}: {e}")


def process_input(file_path, output_path):
    run_task(
        FilePaths.INPUT_PROCESSOR_SCRIPT.value,
        env_path=FilePaths.INPUT_PROCESSOR_VENV.value,
        args=["--output", output_path, "--input", file_path]
    )


def execute_solvers(command_line_args, data, common_data_path):
    solvers = {
        Solvers.LCN.value: [
            FilePaths.LCN_SOLVER.value, FilePaths.LCN_VENV.value
        ],
        Solvers.DOWHY.value: [
            FilePaths.DOWHY_SOLVER.value, FilePaths.DOWHY_VENV.value
        ],
        Solvers.BCAUSE.value: [
            FilePaths.BCAUSE_SOLVER.value, FilePaths.BCAUSE_VENV.value
        ],
        Solvers.AUTOBOUNDS.value: [
            FilePaths.AUTOBOUNDS_SOLVER.value, FilePaths.AUTOBOUNDS_VENV.value
        ],
    }

    for solver_name, [script_path, venv_path] in solvers.items():
        if solver_name in data["solvers"]:
            try:
                logging.info(f"Executing solver: {solver_name}")

                task_args = ["--common_data", common_data_path]
                if command_line_args.verbose:
                    task_args.append("--verbose")
                if command_line_args.fast:
                    task_args.append("--fast")

                run_task(
                    script_path,
                    env_path=venv_path,
                    args=task_args,
                    time_limit=data["time_limit"]
                )
            except Exception as e:
                print(e)
                log_solver_error(e, solver_name, data['test_name'])


def main(args):
    try:
        configure_environment(args.verbose)

        Validator().get_valid_path(args.file_path)

        common_data_path = FilePaths.SHARED_DATA.value
        process_input(args.file_path, common_data_path)

        data = get_common_data(common_data_path)

        output_folder = Path(
            f"{DirectoryPaths.OUTPUTS.value}/{data['test_name']}")
        output_folder.mkdir(parents=True, exist_ok=True)
        logging.info(f"Created output directory for test: {data['test_name']}")

        overview_file_path = (
            f"{DirectoryPaths.OUTPUTS.value}/{data['test_name']}/overview.txt"
        )
        writer = OutputWriterOverview(overview_file_path, reset=args.reset)
        writer.write_test_header(data['test_name'])

        logging.info(
            f"Test '{data['test_name']}' on "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        execute_solvers(args, data, common_data_path)

        DataCleaner().general_cleanup(common_data_path)

    except FileNotFoundError as e:
        logging.error(e)
    except Exception as e:
        logging.exception(f"{type(e).__module__}.{type(e).__name__}: {e}")


if __name__ == "__main__":
    main(input_parse_arguments())

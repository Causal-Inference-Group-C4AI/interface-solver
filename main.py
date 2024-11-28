import argparse
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from utils._enums import DirectoryPaths, FilePaths, Solvers
from utils.data_cleaner import DataCleaner
from utils.get_common_data import get_common_data
from utils.output_writer import OutputWriter
from utils.suppress_warnings import supress_warnings


def run_task(script, env_path=None, args=None):
    """Run a Python script in a specific virtual environment."""
    python_executable = f"{env_path}/bin/python3" if env_path else "python3"
    command = [python_executable, script, *args]
    if args:
        command.extend(args)
    subprocess.run(command, cwd="./", check=True)


def main(args):
    common_data_path = FilePaths.SHARED_DATA.value
    try:
        if not args.verbose:
            supress_warnings()

        run_task(
            FilePaths.INPUT_PROCESSOR_SCRIPT.value,
            env_path=FilePaths.INPUT_PROCESSOR_VENV.value,
            args=["--output", common_data_path, "--input", args.file_path]
        )

        data = get_common_data(common_data_path)

        folder_name = Path(
            f"{DirectoryPaths.OUTPUTS.value}/{data['test_name']}")
        folder_name.mkdir(parents=True, exist_ok=True)
        print(f"Created output directory for test: {data['test_name']}")

        overview_file_path = (
            f"{DirectoryPaths.OUTPUTS.value}/{data['test_name']}/overview.txt"
        )
        writer = OutputWriter(overview_file_path)
        writer(f"Test '{data['test_name']}' on {date.today()}")
        writer("--------------------------------------------")

        print(f"Test '{data['test_name']}' on {date.today()}")

        if Solvers.DOWHY.value in data["solvers"]:
            task_args = ["--common_data", common_data_path]
            if args.verbose:
                task_args.append("--verbose")
            if args.fast:
                task_args.append("--fast")
            run_task(
                FilePaths.DOWHY_SOLVER.value,
                env_path=FilePaths.DOWHY_VENV.value,
                args=task_args
            )

        if Solvers.BCAUSE.value in data['solvers']:
            task_args = ["--common_data", common_data_path]
            if args.verbose:
                task_args.append("--verbose")
            run_task(
                FilePaths.BCAUSE_SOLVER.value,
                env_path=FilePaths.BCAUSE_VENV.value,
                args=task_args
            )

        if Solvers.LCN.value in data["solvers"]:
            task_args = ["--common_data", common_data_path]
            if args.verbose:
                task_args.append("--verbose")
            run_task(
                FilePaths.LCN_SOLVER.value,
                env_path=FilePaths.LCN_VENV.value,
                args=task_args
            )

        if Solvers.AUTOBOUNDS.value in data["solvers"]:
            task_args = ["--common_data", common_data_path]
            if args.verbose:
                task_args.append("--verbose")
            run_task(
                FilePaths.AUTOBOUNDS_SOLVER.value,
                env_path=FilePaths.AUTOBOUNDS_VENV.value,
                args=task_args
            )

        data_cleaner = DataCleaner()
        data_cleaner.cleanup_file(common_data_path)
        print("Shared data successfully deleted.")
        data_cleaner.cleanup_logs()
        print("Logs successfully deleted.")
        data_cleaner.cleanup_lcn()
        print(".LCN successfully deleted.")

    except Exception as e:
        print(f"{type(e).__module__}.{type(e).__name__}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Runs tests of Causal Effect under Partial-Observability."
    )
    parser.add_argument('file_path',
                        help='The path to the file you want to read'
                        )
    parser.add_argument('-v', '--verbose',
                        action='store_true', help="Show solver logs")
    parser.add_argument('-f', '--fast', action='store_true',
                        help="Run the script with fast settings")
    args = parser.parse_args()
    main(args)

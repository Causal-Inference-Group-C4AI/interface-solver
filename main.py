import argparse
from pathlib import Path
import logging
import os
import subprocess
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from utils._enums import Solvers
from utils.data_cleaner import DataCleaner
from utils.get_common_data import get_common_data


def run_task(script, env_path=None, args=None):
    """Run a Python script in a specific virtual environment."""
    python_executable = f"{env_path}/bin/python3" if env_path else "python3"
    command = [python_executable, script, *args]
    if args:
        command.extend(args)
    subprocess.run(command, cwd="./", check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Runs tests of Causal Effect under Partial-Observability."
    )
    parser.add_argument('file_path',
                        help='The path to the file you want to read'
    )
    parser.add_argument('-v', '--verbose', action='store_true', help="Show solver logs")
    args = parser.parse_args()

    common_data_path = "shared/common_data.json"

    try:
        if not args.verbose:
            logging.getLogger().setLevel(logging.CRITICAL)

        run_task(
            "utils/input_processor.py",
            # TODO: REVER O ENV DAQUI 
            env_path="venv_bcause",
            args=["--output", common_data_path, "--input", args.file_path]
        )

        data = get_common_data(common_data_path)

        folder_name = Path(f"outputs/{data['test_name']}")
        folder_name.mkdir(parents=True, exist_ok=True)

        if Solvers.DOWHY.value in data["solvers"]:
            run_task(
                "src/solvers/dowhy_solver.py",
                env_path="venv_dowhy",
                args=["--common_data", common_data_path]
            )

        if Solvers.BCAUSE.value in data['solvers']:
            run_task(
                "src/solvers/bcause_solver.py",
                env_path="venv_bcause",
                args=["--common_data", common_data_path]
            )


        if Solvers.LCN.value in data["solvers"]:
            run_task(
                "src/solvers/lcn_solver.py",
                env_path="venv_lcn",
                args=["--common_data", common_data_path]
            )

        if Solvers.AUTOBOUNDS.value in data["solvers"]:
            run_task(
                "src/solvers/autobounds_solver.py",
                env_path="venv_autobounds",
                args=["--common_data", common_data_path]
            )

    except Exception as e:
        print(f"{type(e).__module__}.{type(e).__name__}: {e}")
    
    data_cleaner = DataCleaner()
    data_cleaner.cleanup_file(common_data_path)
    print("Shared data successfully deleted.")
    data_cleaner.cleanup_logs()
    print("Logs successfully deleted.")
    data_cleaner.cleanup_lcn()
    print(".LCN successfully deleted.")

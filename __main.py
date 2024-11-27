import argparse
from pathlib import Path
import logging
import os
import subprocess
import sys
from datetime import date
from utils.output_writer import OutputWriter
from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from utils._enums import Solvers, FilePaths, DirectoryPaths
from utils.data_cleaner import DataCleaner
from utils.get_common_data import get_common_data


def run_task(script, env_path=None, args=None):
    python_executable = f"{env_path}/bin/python3" if env_path else "python3"
    command = [python_executable, script, *(args or [])]
    subprocess.run(command, cwd="./", check=True)

def process_input(file_path, output_path):
    run_task(
        FilePaths.INPUT_PROCESSOR_SCRIPT.value,
        env_path=FilePaths.INPUT_PROCESSOR_VENV.value,
        args=["--output", output_path, "--input", file_path]
    )

def execute_solvers(data, common_data_path):
    with ThreadPoolExecutor() as executor:
        solvers = {
            Solvers.DOWHY.value: FilePaths.DOWHY_SOLVER.value,
            Solvers.BCAUSE.value: FilePaths.BCAUSE_SOLVER.value,
            Solvers.AUTOBOUNDS.value: FilePaths.AUTOBOUNDS_SOLVER.value,
            Solvers.LCN.value: FilePaths.LCN_SOLVER.value
        }
        futures = []
        for solver_name, script_path in solvers.items():
            if solver_name in data["solvers"]:
                logging.info(f"Executing solver: {solver_name}")
                futures.append(executor.submit(
                    run_task, script_path, FilePaths[f"{solver_name}_VENV"].value,
                    args=["--common_data", common_data_path]
                ))
        for future in futures:
            future.result()

def main(args):
    logging.basicConfig(level=logging.INFO)
    try:
        if not args.verbose:
            logging.getLogger().setLevel(logging.CRITICAL)

        common_data_path = FilePaths.SHARED_DATA.value
        if not Path(args.file_path).exists():
            raise FileNotFoundError(f"Input file not found: {args.file_path}")

        process_input(args.file_path, common_data_path)
        data = get_common_data(common_data_path)

        output_folder = Path(f"{DirectoryPaths.OUTPUTS.value}/{data['test_name']}")
        output_folder.mkdir(parents=True, exist_ok=True)

        execute_solvers(data, common_data_path)

        DataCleaner().cleanup_file(common_data_path)

    except FileNotFoundError as e:
        logging.error(e)
    except Exception as e:
        logging.exception(f"Unexpected error: {e}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Runs tests of Causal Effect under Partial-Observability."
    )
    parser.add_argument('file_path',
                        help='The path to the file you want to read'
    )
    parser.add_argument('-v', '--verbose', action='store_true', help="Show solver logs")
    args = parser.parse_args()
    main(args)

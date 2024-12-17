from utils.solver_error import TimedOutError
from utils.general_utilities import configure_environment, input_parse_arguments, log_solver_error, get_common_data
from utils.validator import Validator
from utils.output_writer import OutputWriterOverview
from utils.general_utilities import (configure_environment,
                                     input_parse_arguments, log_solver_error)
from utils.data_cleaner import DataCleaner
from utils._enums import DirectoryPaths, FilePaths, SolversURL, Solvers
# TODO
# mudar do src para utils
from src.input_processor import InputProcessor, generate_shared_data
import logging
import os
import subprocess
import sys
import requests
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from requests.exceptions import ConnectionError

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)


@app.route('/')
def hello():
    return "Aujourd'hui, maman est morte. Ou peut-être hier, je ne sais pas."


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

def process_input(file_path: str, output_path: str):
    try:
        logging.info(f"Processing input file: {file_path}")

        input_processor = InputProcessor(file_path)

        generate_shared_data(output_path, input_processor.data_test)

        logging.info(f"Shared data generated at: {output_path}")
    except Exception as e:
        logging.error(f"Error processing input file: {e}")
        raise

def wait_for_solver(url, retries=10, delay=5):
    """Wait for the solver to be ready using a health check endpoint."""
    health_url = f"{url}/health"
    for attempt in range(retries):
        try:
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                logging.info(f"Solver ready at {health_url}")
                return True
        except requests.exceptions.ConnectionError:
            logging.info(f"Solver at {health_url} not ready, retrying... ({attempt + 1}/{retries})")
            time.sleep(delay)
    raise ConnectionError(f"Solver at {url} failed to start after {retries} attempts.")


def execute_solvers(command_line_args, data, common_data_path):
    
    solver_urls = {
        Solvers.LCN.value: SolversURL.LCN_URL.value,
        Solvers.DOWHY.value: SolversURL.DOWHY_URL.value,
        Solvers.BCAUSE.value: SolversURL.BCAUSE_URL.value,
        Solvers.AUTOBOUNDS.value: SolversURL.AUTOBOUNDS_URL.value
    }
    
    for solver_name in data["solvers"]:
        try:
            logging.info(f"Waiting for solver: {solver_name}")
            url = solver_urls[solver_name]
            wait_for_solver(url)

            logging.info(f"Executing solver: {solver_name}")
            payload = {
                "common_data": common_data_path,
                "verbose": command_line_args.verbose,
                "fast": command_line_args.fast
            }
            
            response = requests.post(f"{url}/solve", json=payload, timeout=data["time_limit"])
            if response.status_code == 200:
                # Success
                result = response.json()
                # Process result
            else:
                # Error
                error_info = response.json().get("error", "Unknown error")
                log_solver_error(error_info, solver_name, data['test_name'])
        except Exception as e:
            print(e)
            log_solver_error(e, solver_name, data['test_name'])


    # solvers = {
    #     Solvers.LCN.value: [
    #         FilePaths.LCN_SOLVER.value, FilePaths.LCN_VENV.value
    #     ],
    #     Solvers.DOWHY.value: [
    #         FilePaths.DOWHY_SOLVER.value, FilePaths.DOWHY_VENV.value
    #     ],
    #     Solvers.BCAUSE.value: [
    #         FilePaths.BCAUSE_SOLVER.value, FilePaths.BCAUSE_VENV.value
    #     ],
    #     Solvers.AUTOBOUNDS.value: [
    #         FilePaths.AUTOBOUNDS_SOLVER.value, FilePaths.AUTOBOUNDS_VENV.value
    #     ],
    # }

    # for solver_name, [script_path, venv_path] in solvers.items():
    #     if solver_name in data["solvers"]:
    #         try:
    #             logging.info(f"Executing solver: {solver_name}")

    #             task_args = ["--common_data", common_data_path]
    #             if command_line_args.verbose:
    #                 task_args.append("--verbose")
    #             if command_line_args.fast:
    #                 task_args.append("--fast")

    #             run_task(
    #                 script_path,
    #                 env_path=venv_path,
    #                 args=task_args,
    #                 time_limit=data["time_limit"]
    #             )
    #         except Exception as e:
    #             print(e)
    #             log_solver_error(e, solver_name, data['test_name'])


def main(args):
    logging.info("Main function started.")
    try:
        logging.info("Configuring environment...")
        configure_environment(args.verbose)

        logging.info(f"Validating file path: {args.file_path}")
        Validator().get_valid_path(args.file_path)

        logging.info("Setting up shared data path.")
        common_data_path = FilePaths.SHARED_DATA.value
        logging.info(f"Processing input file: {args.file_path}")
        process_input(args.file_path, common_data_path)

        logging.info(f"Getting common data from: {common_data_path}")
        data = get_common_data(common_data_path)

        logging.info(f"Creating output directory for test: {data['test_name']}")
        output_folder = Path(
            f"{DirectoryPaths.OUTPUTS.value}/{data['test_name']}")
        output_folder.mkdir(parents=True, exist_ok=True)

        logging.info(f"Setting up overview file: {data['test_name']}/overview.txt")
        overview_file_path = (
            f"{DirectoryPaths.OUTPUTS.value}/{data['test_name']}/overview.txt"
        )
        writer = OutputWriterOverview(overview_file_path, reset=args.reset)
        writer.write_test_header(data['test_name'])

        logging.info(
            f"Test '{data['test_name']}' started at "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        logging.info("Executing solvers...")
        execute_solvers(args, data, common_data_path)

        logging.info("Cleaning up data...")
        DataCleaner().general_cleanup(common_data_path)

        logging.info("Main function finished.")

    except FileNotFoundError as e:
        logging.error(f"FileNotFoundError: {e}")
    except Exception as e:
        logging.exception(f"Unhandled exception: {type(e).__module__}.{type(e).__name__}: {e}")

    


if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=8080, debug=True)
    main(input_parse_arguments())

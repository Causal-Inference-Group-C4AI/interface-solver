from utils.solver_error import TimedOutError
from utils.general_utilities import configure_environment, input_parse_arguments, log_solver_error, get_common_data
from utils.validator import Validator
from utils.output_writer import OutputWriterOverview
from utils.general_utilities import (configure_environment,
                                     input_parse_arguments, log_solver_error)
from utils.data_cleaner import DataCleaner
from utils._enums import DirectoryPaths, FilePaths, SolversURL, Solvers
from utils.file_generators.input_processor import InputProcessor, generate_shared_data
import logging
import os
import subprocess
import sys
import requests
import time
from datetime import datetime
from pathlib import Path
from requests.exceptions import ConnectionError, ReadTimeout

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def process_input(file_path: str, output_path: str):
    try:
        print("Running Input Processor...")

        input_processor = InputProcessor(file_path)

        generate_shared_data(output_path, input_processor.data_test)

        print("Input processor done!")
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

            print(f"{solver_name} solver running...")
            payload = {
                "common_data": common_data_path,
                "verbose": command_line_args.verbose,
                "fast": command_line_args.fast
            }
            
            response = requests.post(f"{url}/solve", json=payload, timeout=data["time_limit"])
            if response.status_code == 200:
                result = response.json()
                print(f"Time taken by {solver_name}: {result['time_taken']:.6f} seconds.")
            else:
                error_info = response.json().get("error", "Unknown error")
                log_solver_error(error_info, solver_name, data['test_name'])
        except ReadTimeout:
            error_message = (
                f"Solver {solver_name} timed out after {data['time_limit']} seconds. "
            )
            print(error_message)
            log_solver_error(error_message, solver_name, data['test_name'])
        except Exception as e:
            error_message = f"An unexpected error occurred while communicating with solver {solver_name}: {str(e)}"
            print(error_message)
            log_solver_error(error_message, solver_name, data['test_name'])

def main(args):
    try:
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
    main(input_parse_arguments())

import logging
import os
import subprocess
import sys

from utils.general_utilities import log_solver_error

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def run_task(script, env_path=None, args=None, caller_name=None, test_name=None):
    if caller_name is None:
        run_input_task(script, env_path, args)
    else:
        run_solver_task(script, caller_name, test_name, env_path=env_path, args=args)


def run_input_task(script, env_path=None, args=None):
    """Run a Python script in a specific virtual environment."""
    python_executable = f"{env_path}/bin/python3" if env_path else "python3"
    command = [python_executable, script, *args]
    if args:
        command.extend(args)
    subprocess.run(command, cwd="./", check=True)
    

def run_solver_task(script, solver_name, test_name, env_path=None, args=None):
    """Run a Python script in a specific virtual environment."""
    python_executable = f"{env_path}/bin/python3" if env_path else "python3"
    command = [python_executable, script, *args]
    if args:
        command.extend(args)
    try:
        result = subprocess.run(command, cwd="./", 
            capture_output=True,
            text=True,
            check=True
        )
        print("Subprocess completed successfully!")
        print("Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Subprocess failed!")
        print("Error output:", e.stderr)
        if "Infeasible problem" in e.stderr:
            logging.error(f"Infeasible problem in solver {solver_name}: {e}")
            print(f"Infeasible problem encountered by {solver_name}.")
            log_solver_error(e, solver_name, test_name)
        elif "Solver error" in e.stderr:
            logging.error(f"Solver error in {solver_name}: {e}")
            print(f"Solver error encountered by {solver_name}. Check logs for details.")
            log_solver_error(e, solver_name, test_name)
    except Exception as e:
        logging.error(f"Unexpected error in {solver_name}: {e}")
        print(f"Unexpected error in solver {solver_name}. Check logs for details.")
        log_solver_error(e, solver_name, test_name)
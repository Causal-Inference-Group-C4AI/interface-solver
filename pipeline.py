import argparse
import logging
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
# from input_processor import InputProcessor
# from interface import interface


# def pipeline(input_path: str):
#     processed_input = InputProcessor(input_path)



# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(
#         description="Runs tests of Causal Effect under Partial-Observability."
#     )
#     parser.add_argument('file_path',
#                         help='The path to the file you want to read'
#     )
#     parser.add_argument('-v', '--verbose', action='store_true', help="Show solver logs")
#     args = parser.parse_args()
#     try:
#         if not args.verbose:
#             logging.getLogger().setLevel(logging.CRITICAL)
#         pipeline(args.file_path)
#     except Exception as e:
#         print(f"{type(e).__module__}.{type(e).__name__}: {e}")

import subprocess

def run_task(script, env_path=None, args=None):
    """Run a Python script in a specific virtual environment."""
    python_executable = f"{env_path}/bin/python3" if env_path else "python3"
    command = [python_executable, script, *args]
    if args:
        command.extend(args)
    subprocess.run(command, cwd="./")


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
    
        print("Running Input Processor...")
        run_task(
            "input_processor.py",
            env_path="venv_dowhy",
            args=["--output", common_data_path, "--input", args.file_path]
        )

        print("Running DoWhy Solver...")
        run_task(
            "src/solvers/dowhy_solver.py",
            env_path="venv_dowhy",
            args=["--common_data", common_data_path]
        )

        # print("Running Task 3...")
        # run_task(
        #     "src/solvers/_solver.py",
        #     "venv_task1",
        #     ["common_data", common_data_path]
        # )

    except Exception as e:
        print(f"{type(e).__module__}.{type(e).__name__}: {e}")
        

import os
import sys
import time
from typing import Tuple

import pandas as pd

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../')))

from bcause.inference.causal.multi import EMCC
from bcause.models.cmodel import StructuralCausalModel

from utils._enums import DirectoryPaths, Solvers
from utils.general_utilities import (configure_environment, get_common_data, log_solver_error)
from utils.output_writer import OutputWriterBcause
from utils.validator import Validator
from utils.solver_results import ATE, SolverResultsFactory
from flask import Flask, request, jsonify 

app = Flask(__name__)

def bcause_solver(
        test_name: str,
        uai_path: str,
        csv_path: str,
        treatment: str,
        outcome: str,
        mapping: dict) -> Tuple[float, float]:
    print("Bcause solver running...")
    model = StructuralCausalModel.read(uai_path)
    renamed_model = model.rename_vars(mapping)

    dataset = pd.read_csv(csv_path)
    inf = EMCC(renamed_model, dataset, max_iter=100, num_runs=20)

    p_do0 = inf.causal_query(outcome, do={treatment: 0})
    p_do1 = inf.causal_query(outcome, do={treatment: 1})

    lower_bound = p_do1.values[1] - p_do0.values[1]
    upper_bound = p_do1.values[3] - p_do0.values[3]

    output_file = (
        f"{DirectoryPaths.OUTPUTS.value}/{test_name}/"
        f"{Solvers.BCAUSE.value}_{test_name}.txt"
    )
    writer = OutputWriterBcause(output_file)

    writer("==============================================")
    writer(
        f'P({outcome}=1|do({treatment}=0)) = '
        f'{[p_do0.values[1], p_do0.values[3]]}')
    writer(
        f'P({outcome}=1|do({treatment}=1)) = '
        f'{[p_do1.values[1], p_do1.values[3]]}')
    writer(
        f"Causal effect lies in the interval [{lower_bound}, {upper_bound}]")
    writer("==============================================")
    print("Bcause solver Done.")
    return lower_bound, upper_bound


def run_bcause_solver(data):
    """Runs the Bcause solver."""
    return bcause_solver(
        test_name=data['test_name'],
        uai_path=data['uai_path'],
        csv_path=data['csv_path'],
        treatment=data['treatment'],
        outcome=data['outcome'],
        mapping=data['uai_mapping'],
    )

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/solve', methods=['POST'])
def solve_endpoint():

    json_input = request.get_json()

    configure_environment(json_input['verbose'])

    validator = Validator()
    data = get_common_data(validator.get_valid_path(json_input['common_data']))
    
    try:
        start_time = time.time()
        lower_bound, upper_bound = run_bcause_solver(data)
        time_taken = time.time() - start_time

        solver_result = SolverResultsFactory().get_solver_results_object(Solvers.BCAUSE.value, data['test_name'])
        solver_result.log_solver_results(ATE((lower_bound, upper_bound)), time_taken)

        return jsonify({
            "status": "success",
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "time_taken": time_taken
        }), 200
    except Exception as e:
        log_solver_error(e, "bcause", data['test_name'])
        return jsonify({"error": str(e), "error_code": "SOLVER_FAILED"}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5003)

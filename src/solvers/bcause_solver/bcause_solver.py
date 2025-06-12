import logging
import os
import sys
import time
from typing import Tuple

import networkx as nx
import pandas as pd
from bcause.inference.causal.multi import EMCC
from bcause.models.cmodel import StructuralCausalModel
from flask import Flask, jsonify, request

from utils._enums import DirectoryPaths, Solvers
from utils.general_utilities import (configure_environment, get_common_data,
                                     log_solver_error)
from utils.output_writer import OutputWriterBcause
from utils.solver_results import ATE, SolverResultsFactory
from utils.validator import Validator

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../')))


app = Flask(__name__)


def bcause_solver(
        test_name: str,
        uai_path: str,
        csv_path: str,
        treatment: str,
        outcome: str,
        mapping: dict) -> Tuple[float, float]:
    model = StructuralCausalModel.read(uai_path)
    renamed_model = model.rename_vars(mapping)

    dataset = pd.read_csv(csv_path)
    inf = EMCC(renamed_model, dataset, max_iter=100, num_runs=20)

    graph = renamed_model.graph
    logging.info(f"Graph: {graph}")
    all_nodes = list(nx.topological_sort(graph))
    logging.info(f"All nodes: {all_nodes}")
    outcome_index = all_nodes.index(outcome)
    logging.info(f"Outcome index: {outcome_index}")
    treatment_nodes = all_nodes[:outcome_index]
    logging.info(f"Treatment nodes: {treatment_nodes}")

    pn_dict = {}
    ps_dict = {}
    pns_dict = {}
    weak_pn = {}
    weak_ps = {}
    for treatment_var in treatment_nodes:
        if treatment_var not in renamed_model.endogenous:
            continue
        logging.info(f"Calculating for treatment variable: {treatment_var}")
        do0 = inf.causal_query(outcome, do={treatment_var: 0})
        do1 = inf.causal_query(outcome, do={treatment_var: 1})
        ps = [do1.values[1], do1.values[3]]
        pn = [do0.values[0], do0.values[2]]
        PN = inf.prob_necessity(treatment_var, outcome)
        PS = inf.prob_sufficiency(treatment_var, outcome)
        PNS = inf.prob_necessity_sufficiency(treatment_var, outcome)
        pn_dict[treatment_var] = PN
        ps_dict[treatment_var] = PS
        pns_dict[treatment_var] = PNS
        weak_pn[treatment_var] = pn
        weak_ps[treatment_var] = ps

    output_file = (
        f"{DirectoryPaths.OUTPUTS.value}/{test_name}/"
        f"{Solvers.BCAUSE.value}_{test_name}.txt"
    )
    writer = OutputWriterBcause(output_file)

    writer("==============================================")
    writer(f'PN = {pn_dict}')
    writer(f'PS = {ps_dict}')
    writer(f'PNS = {pns_dict}')
    writer(f'Weak PN = {weak_pn}')
    writer(f'Weak PS = {weak_ps}')
    writer("==============================================")

    lower_bound = do1.values[1] - do0.values[3]
    upper_bound = do1.values[3] - do0.values[1]
    writer("==============================================")
    writer(
        f'P({outcome}=1|do({treatment}=0)) = '
        f'{[do0.values[1], do0.values[3]]}')
    writer(
        f'P({outcome}=1|do({treatment}=1)) = '
        f'{[do1.values[1], do1.values[3]]}')
    writer(
        f"Causal effect lies in the interval [{lower_bound}, {upper_bound}]")
    writer("==============================================")
    logging.info("Bcause solver Done.")
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

        solver_result = SolverResultsFactory().get_solver_results_object(
            Solvers.BCAUSE.value, data['test_name'])
        solver_result.log_solver_results(
            ATE((lower_bound, upper_bound)), time_taken)

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

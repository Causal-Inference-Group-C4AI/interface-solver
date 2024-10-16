from dowhy import CausalModel


def dowhy_solver(self):
    # Step 1: Model
    model = CausalModel(
        data=self.data,
        treatment="X",
        outcome="Y",
        graph=self.graph
    )

    # Step 2: Identify
    identified_estimand = model.identify_effect()

    # Step 3: Estimate
    estimate = model.estimate_effect(
        identified_estimand,
        method_name="backdoor.linear_regression"
    )

    # Step 4: Refute
    refutation = model.refute_estimate(
        identified_estimand,
        estimate,
        method_name="random_common_cause"
    )

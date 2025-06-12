class SolverError(Exception):
    """Base class for all solver errors."""
    pass

class InfeasibleProblemError(SolverError):
    """Raised when a problem is infeasible."""
    def __init__(self, message="Problem is infeasible. Returning without solutions"):
        super().__init__(message)

class TimedOutError(SolverError):
    """Raised when a solver times out."""
    def __init__(self, time_limit: int):
        super().__init__(f"Solver timed out after {time_limit} seconds. Returning without solutions")
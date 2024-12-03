class SolverError(Exception):
    """Base class for all solver errors."""
    pass

class InfeasibleProblemError(SolverError):
    """Raised when a problem is infeasible."""
    def __init__(self, message="Problem is infeasible. Returning without solutions"):
        super().__init__(message)

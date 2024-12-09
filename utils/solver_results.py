from abc import ABC, abstractmethod
from typing import Dict, Tuple, Union, Optional
from utils._enums import Solvers, DirectoryPaths, EmptyValues
from utils.output_writer import OutputWriter


class ATE:
    def __init__(self, ATE: Union[Tuple[float, float], Dict[str, float]]) -> None:
        self.tuple_value, self.dict_value = self.get_ATE_values(ATE)

    def get_ATE_values(self, ATE: Union[Tuple[float, float], Dict[str, float]]) -> Tuple[Tuple[float, float], Dict[str, float]]:
        if isinstance(ATE, Tuple):
            return ATE, {"NONE":0.0}
        elif isinstance(ATE, Dict):
            return (-1.0, -1.0), ATE
        raise ValueError("Invalid type for ATE. Expected Tuple[float, float] or Dict[str, float].")


class SolverResult(ABC):
    def __init__(self, test_name: str, solver_name: str) -> None:
        self.test_name = test_name
        self.solver_name = solver_name
    
    @abstractmethod
    def log_solver_results(self, ate: ATE, time_taken):
        """Logs the results of the solver."""
        pass


class DoWhyResult(SolverResult):
    def __init__(self, test_name: str, solver_name: str) -> None:
        super().__init__(test_name, solver_name)

    def log_solver_results(self, ate: ATE, time_taken):
        print(f"Time taken by {self.solver_name}: {time_taken:.6f} seconds")

        overview_file_path = (
            f"{DirectoryPaths.OUTPUTS.value}/{self.test_name}/overview.txt"
        )
        writer = OutputWriter(overview_file_path, reset=False)

        writer(f"{self.solver_name}")
        writer(f"   Time taken by {self.solver_name}: {time_taken:.6f} seconds")

        if ate.dict_value is EmptyValues.DICT_ATE.value:
            raise ValueError("Invalid DoWhy ATE.")

        for method, ate in ate.dict_value.items(): # type: ignore
            writer(f"   Estimate method: {method}")
            writer(f"   ATE is: {ate}")
        writer("--------------------------------------------")


class BoundsResult(SolverResult):
    def __init__(self, test_name: str, solver_name: str) -> None:
        super().__init__(test_name, solver_name)

    def log_solver_results(self, ate: ATE, time_taken):
        print(f"Time taken by {self.solver_name}: {time_taken:.6f} seconds")

        overview_file_path = (
            f"{DirectoryPaths.OUTPUTS.value}/{self.test_name}/overview.txt"
        )
        writer = OutputWriter(overview_file_path, reset=False)

        writer(f"{self.solver_name}")
        writer(f"   Time taken by {self.solver_name}: {time_taken:.6f} seconds")

        lower_bound = ate.tuple_value[0]
        upper_bound = ate.tuple_value[1]
        writer(f"   ATE lies in the interval: [{lower_bound}, {upper_bound}]")
        writer("--------------------------------------------")


class SolverResultsFactory:
    def __init__(self) -> None:
        pass

    """ [INTERNAL COMMENT]
            DESGIN PATTERN: FACTORY METHOD (get_solver_results_object)
            Esse pattern abstrai em um método a escolha de uma classe espefícia para uma finalidade genérica.
            Finalidade Genérica: Lidar com os resultados dos solvers (SolverResult)
            Finalidade específica: Lidar com cada tipo de resultado. (DoWhyResult, BoundsResult)
                                O DoWhy tem como resultado uma série de valores e nomes dos estimadores.
                                Enquanto LCN, AUTOBOUNDS e BCAUSE é uma tupla.
            
            Benefícios: 
            - Extensibilidade: Se houver um outro solver que retorna um resultado bem diferente, 
            é só nós adicionarmos uma nova classe que lida com esse caso.

            Prejuízo:
            - Overengineering: Pode ser que toda essa lógica seja "além do necessário" para a nossa aplicação.
    """
    def get_solver_results_object(self, solver_name: str, test_name: str) -> SolverResult:
        if solver_name.lower() is Solvers.DOWHY.value:
            return DoWhyResult(test_name, solver_name)
        else:
            return BoundsResult(test_name, solver_name)

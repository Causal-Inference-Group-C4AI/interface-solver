import contextlib
import logging
from datetime import datetime

from utils._enums import DirectoryPaths, Solvers


class OutputWriter:
    """
    A utility class for managing output to both the console and a file.

    This class provides a simple mechanism for printing messages to the console
    and simultaneously writing them to a specified output file. The file is
    automatically cleared upon initialization to ensure a fresh output for each
    session.

    **Attributes**:
        output_path (str): The file path to which the output will be written.
            Defaults to "data/outputs/dowhy_output_NO_TEST_NAME.txt".

    **Methods**:
        __call__(output: str, end: str, new: bool):
            Prints a message to the console and appends it to the output file.
        reset():
            Resets the content of the output file by clearing it.
    """


    def __init__(self, output_path=f"{DirectoryPaths.OUTPUTS.value}/DEFAULT_OUTPUT.txt", reset: bool = True):
        """
        Initialize the OutputWriter with the given output path.

        Args:
            output_path (str, optional): The path to the output file. Defaults to "data/outputs/bcause_output_NO_TEST_NAME.txt".
        """
        
        self.output_path = output_path
        if reset:
            self.reset()


    def __call__(self, output, end: str = "\n", new=False):
        """
        Write the output to the file.

        Args:
            output (str): The output to write to the file.
            new (bool, optional): Whether to write a new file or append to an
                existing one. Defaults to False
        """
        mode = "w" if new else "a"
        if len(output) > 80 and output.count("\n") == 0:
            self.__call__(output[:80])
            self.__call__(output[80:], end=end)
        else:
            logging.getLogger().info(output)
            try:
                with open(self.output_path, mode) as file:
                    file.write(output + end)
            except IOError as e:
                raise IOError(f"Error writing to file {self.output_path}: {e}")


    def reset(self) -> None:
        """Resets the output file by clearing its content."""
        try:
            with open(self.output_path, 'w') as file:
                file.write("")
        except IOError as e:
            IOError(f"Error resetting file {self.output_path}: {e}")


    def silent_run(self, func, output_file=None, new=False):
        """Run a function and redirect output to a specified file.

        Args:
            func (function): The function to run.
            output_file (str, optional): The file path to redirect output to.
                Defaults to None.
            new (bool, optional): Whether to write a new file or append to an
                existing one. Defaults to False.
        """
        mode = "w" if new else "a"
        try:
            if output_file is None:
                with open(self.output_path, mode) as f:
                    with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
                        return func()

            else:
                with open(output_file, mode) as f:
                    with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
                        return func()
        except Exception as e:
            raise Exception(f"Error: {e}")


class OutputWriterOverview(OutputWriter):
    def __init__(self, output_path=f"{DirectoryPaths.OUTPUTS.value}/overview_output_NO_TEST_NAME.txt", reset=False):
        super().__init__(output_path, reset)

    def write_test_header(self, test_name: str):
        self("*"*90)
        self(f"Test '{test_name}' on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self("--------------------------------------------")

class OutputWriterBcause(OutputWriter):
    def __init__(self, output_path=f"{DirectoryPaths.OUTPUTS.value}/{Solvers.BCAUSE.value}_output_NO_TEST_NAME.txt"):
        super().__init__(output_path)


class OutputWriterAutobounds(OutputWriter):
    def __init__(self, output_path=f"{DirectoryPaths.OUTPUTS.value}/{Solvers.AUTOBOUNDS.value}_output_NO_TEST_NAME.txt"):
        super().__init__(output_path)


class OutputWriterLCN(OutputWriter):
    def __init__(self, output_path=f"{DirectoryPaths.OUTPUTS.value}/{Solvers.LCN.value}_output_NO_TEST_NAME.txt"):
        super().__init__(output_path)


class OutputWriterDoWhy(OutputWriter):
    def __init__(self, output_path: str = f"{DirectoryPaths.OUTPUTS.value}/{Solvers.DOWHY.value}_output_NO_TEST_NAME.txt") -> None:
        super().__init__(output_path)

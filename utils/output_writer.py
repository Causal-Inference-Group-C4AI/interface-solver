import contextlib
import logging


class OutputWriter:
    """
    A utility class for managing output to both the console and a file.

    This class provides a simple mechanism for printing messages to the console
    and simultaneously writing them to a specified output file. The file is
    automatically cleared upon initialization to ensure a fresh output for each
    session.

    **Attributes**:
        output_path (str): The file path to which the output will be written.
            Defaults to "outputs/dowhy_output_NO_TEST_NAME.txt".

    **Methods**:
        __call__(text: str, end: str):
            Prints a message to the console and appends it to the output file.
        reset():
            Resets the content of the output file by clearing it.
    """


    def __init__(self, output_path="outputs/DEFAULT_OUTPUT.txt"):
        """
        Initialize the OutputWriter with the given output path.

        Args:
            output_path (str, optional): The path to the output file. Defaults to "outputs/bcause_output_NO_TEST_NAME.txt".
        """
        
        self.output_path = output_path
        self.reset()


    def __call__(self, output, new=False):
        """
        Write the output to the file.

        Args:
            output (str): The output to write to the file.
            new (bool, optional): Whether to write a new file or append to an
                existing one. Defaults to False
        """
        mode = "w" if new else "a"
        try:
            with open(self.output_path, mode) as f:
                f.write(output + "\n")
        except Exception as e:
            raise Exception(f"Error while wirting in the file {self.output_path}. Error: {e}")


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


class OutputWriterBcause(OutputWriter):
    def __init__(self, output_path="outputs/bcause_output_NO_TEST_NAME.txt"):
        super().__init__(output_path)


class OutputWriterAutobounds(OutputWriter):
    def __init__(self, output_path="outputs/autobounds_output_NO_TEST_NAME.txt"):
        super().__init__(output_path)


class OutputWriterLCN(OutputWriter):
    def __init__(self, output_path="outputs/lcn_output_NO_TEST_NAME.txt"):
        super().__init__(output_path)


class OutputWriterDoWhy(OutputWriter):
    def __init__(self, output_path: str = "outputs/dowhy_output_NO_TEST_NAME.txt") -> None:
        super().__init__(output_path)

    def __call__(self, text: str = "", end: str = "\n") -> None:
        if len(text) > 80 and text.count("\n") == 0:
            self.__call__(text[:80])
            self.__call__(text[80:], end=end)
        else:
            logging.getLogger().info(text)
            try:
                with open(self.output_path, 'a') as file:
                    file.write(text + end)
            except IOError as e:
                raise IOError(f"Error writing to file {self.output_path}: {e}")

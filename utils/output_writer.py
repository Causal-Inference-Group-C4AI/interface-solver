from abc import abstractmethod


class OutputWriter:
    def __init__(self, output_path="outputs/DEFAULT_OUTPUT.txt"):
        self.output_path = output_path
        self.reset()


    def __call__(self, output, new=False):
        """
        Write the output to the file.

        Args:
            output (str): The output to write to the file.
            new (bool, optional): Whether to write a new file or append to an existing one. Defaults to False
        """
        mode = "w" if new else "a"
        with open(self.output_path, mode) as f:
            f.write(output + "\n")


    def reset(self) -> None:
        """Resets the output file by clearing its content."""
        try:
            with open(self.output_path, 'w') as file:
                file.write("")
        except IOError as e:
            print(f"Error resetting file {self.output_path}: {e}")


class OutputWriterBcause(OutputWriter):
    def __init__(self, output_path="outputs/bcause_output_NO_TEST_NAME.txt"):
        """
        Initialize the OutputWriter with the given output path.

        Args:
            output_path (str, optional): The path to the output file. Defaults to "outputs/bcause_output_NO_TEST_NAME.txt".
        """
        super().__init__(output_path)


class OutputWriterAutobounds(OutputWriter):
    def __init__(self, output_path="outputs/autobounds_output_NO_TEST_NAME.txt"):
        """
        Initialize the OutputWriter with the given output path.

        Args:
            output_path (str, optional): The path to the output file. Defaults to "outputs/autobounds_output_NO_TEST_NAME.txt".
        """
        super().__init__(output_path)

class OutputWriterLCN(OutputWriter):
    def __init__(self, output_path="outputs/lcn_output_NO_TEST_NAME.txt"):
        """
        Initialize the OutputWriter with the given output path.

        Args:
            output_path (str, optional): The path to the output file. Defaults to "outputs/lcn_output_NO_TEST_NAME.txt".
        """
        super().__init__(output_path)


class OutputWriterDoWhy(OutputWriter):
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

    def __init__(self, output_path: str = "outputs/dowhy_output_NO_TEST_NAME.txt") -> None:
        """Initializes the Output class and resets the file.

        Args:
            output_path (str, optional): The file to write output to.
                Defaults to "outputs/dowhy_output_NO_TEST_NAME.txt".
        """
        super().__init__(output_path)


    def __call__(self, text: str = "", end: str = "\n") -> None:
        """Prints a message and writes it to a file.

        Args:
            text (str, optional): Message to be outputted and written to the
                file. Defaults to "".
            end (str, optional): End of the message. Defaults to "\\n".
        """
        if len(text) > 80 and text.count("\n") == 0:
            self.__call__(text[:80])
            self.__call__(text[80:], end=end)
        else:
            print(text, end=end)
            try:
                with open(self.output_path, 'a') as file:
                    file.write(text + end)
            except IOError as e:
                print(f"Error writing to file {self.output_path}: {e}")

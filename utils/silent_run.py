import contextlib
import os

def silent_run(func, output_file=None, new=False):
    """Run a function and redirect output to a specified file.

    Args:
        func (function): The function to run.
        output_file (str, optional): The file path to redirect output to. Defaults to None.
        new (bool, optional): Whether to write a new file or append to an existing one. Defaults to False.
    """
    mode = "w" if new else "a"
    if output_file:
        with open(output_file, mode) as f:
            with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
                return func()
    else:
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull), contextlib.redirect_stderr(fnull):
                return func()
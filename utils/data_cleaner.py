import glob
import logging
import os


class DataCleaner:
    """Class to clean up data"""
    def __init__(self) -> None:
        pass

    def general_cleanup(self, file_path: str) -> None:
        """Delete shared data, .LCN and logs.

        Args:
            file_path (str): Path to the shared data file.
        """
        logging.basicConfig(level=logging.INFO)
        self.cleanup_file(file_path)
        logging.info("Shared data successfully deleted.")
        self.cleanup_lcn()
        logging.info(".LCN successfully deleted.")
        self.cleanup_logs()
        logging.info("Logs successfully deleted.")

    def cleanup_file(self, file_path: str) -> None:
        """Remove a specific file.

        Args:
            file_path (str): Path to the file to be deleted.
        """
        try:
            os.remove(file_path)
        except Exception as e:
            raise Exception(f"Error deleting {file_path}: {e}")

    def cleanup_extension(self, extension: str) -> None:
        """Remove all files with a specific extension.

        Args:
            extension (str): Extension of the files to be deleted.
        """
        files = glob.glob(f"*.{extension}")
        for file in files:
            self.cleanup_file(file)

    def cleanup_lcn(self) -> None:
        """Remove all .LCN files."""
        self.cleanup_extension("LCN")

    def cleanup_logs(self) -> None:
        """Remove all log files."""
        self.cleanup_extension("log")

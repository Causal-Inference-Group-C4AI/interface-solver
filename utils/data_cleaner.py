import glob
import logging
import os


class DataCleaner:
    def __init__(self):
        pass

    def general_cleanup(self, file_path: str):
        logging.basicConfig(level=logging.INFO)
        self.cleanup_file(file_path)
        logging.info("Shared data successfully deleted.")
        self.cleanup_lcn()
        logging.info("Logs successfully deleted.")
        self.cleanup_logs()
        logging.info(".LCN successfully deleted.")


    def cleanup_file(self, file_path: str):
        """Remove a specific file."""
        try:
            os.remove(file_path)
        except Exception as e:
            raise Exception(f"Error deleting {file_path}: {e}")

    def cleanup_extension(self, extension: str):
        files = glob.glob(f"*.{extension}")
        for file in files:
            self.cleanup_file(file)
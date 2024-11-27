import glob
import os
import logging


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


    def cleanup_lcn(self):
        """Remove all LCN files in the current directory."""
        lcn_files = glob.glob("*.lcn")
        for lcn_file in lcn_files:
            self.cleanup_file(lcn_file)


    def cleanup_logs(self):
        """Remove all log files in the current directory."""
        log_files = glob.glob(".*.log")
        for log_file in log_files:
            self.cleanup_file(log_file)

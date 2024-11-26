import glob
import os


class DataCleaner:
    def __init__(self):
        pass

    def cleanup_file(self, file_path: str):
        try:
            os.remove(file_path)
        except Exception as e:
            raise Exception(f"Error deleting {file_path}: {e}")

    def cleanup_extension(self, extension: str):
        files = glob.glob(f"*.{extension}")
        for file in files:
            self.cleanup_file(file)

    # def cleanup_lcn(self):
    #     """Remove all LCN files in the current directory."""
    #     lcn_files = glob.glob("*.lcn")
    #     for lcn_file in lcn_files:
    #         self.cleanup_file(lcn_file)


    # def cleanup_logs(self):
    #     """Remove all log files in the current directory."""
    #     log_files = glob.glob(".*.log")
    #     for log_file in log_files:
    #         self.cleanup_file(log_file)

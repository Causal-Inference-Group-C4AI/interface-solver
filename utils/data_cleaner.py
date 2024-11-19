import os
import glob

class DataCleaner:
    def __init__(self):
        pass

    def cleanup_file(self, file_path: str):
        try:
            os.remove(file_path)
        except Exception as e:
            raise Exception(f"Error deleting {file_path}: {e}")


    def cleanup_lcn(self):
        """Remove all LCN files in the current directory."""
        lcn_files = glob.glob("*.lcn")
        for lcn_file in lcn_files:
            try:
                os.remove(lcn_file)
            except Exception as e:
                print(f"Error deleting {lcn_file}: {e}")


    def cleanup_logs(self):
        """Remove all log files in the current directory."""
        log_files = glob.glob(".*.log")
        for log_file in log_files:
            try:
                os.remove(log_file)
            except Exception as e:
                raise Exception(f"Error deleting {log_file}: {e}")
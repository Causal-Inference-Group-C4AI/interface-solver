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
import argparse
import logging


from input_processor import InputProcessor
from interface import interface


def pipeline(input_path: str):
    input_processor = InputProcessor(input_path)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Runs tests of Causal Effect under Partial-Observability."
    )
    parser.add_argument('file_path',
                        help='The path to the file you want to read'
    )
    parser.add_argument('-v', '--verbose', action='store_true', help="Show solver logs")
    args = parser.parse_args()
    try:
        if not args.verbose:
            logging.getLogger().setLevel(logging.CRITICAL)
        pipeline(args.file_path)
    except Exception as e:
        print(f"{type(e).__module__}.{type(e).__name__}: {e}")
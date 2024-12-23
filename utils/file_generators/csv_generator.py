import csv
from typing import List, Tuple

import pandas as pd


from utils._enums import DirectoryPaths


ArrayType = List[Tuple[List[int], float]]


def probsHelper(
    header: str,
    probCombinations: ArrayType,
    test_name: str,
    csv_flag: bool = True
) -> str | pd.DataFrame:
    """
    Generate a dataset in the csv format which is consistent with the specified
    distribution. As input, it needs: a header row for the csv, the probability
    of each outcome of the variables and the csv filename.
    Returns:
        str: Path to the csv generated
    or
        DataFrame: DataFrame with the generated data
    """
    maxDecimals: int = 0
    for _sublist, val in probCombinations:
        probStr: str = str(val)
        if "." in probStr:
            maxDecimals = max(maxDecimals, len(probStr.split(".")[1]))

    if csv_flag:
        file_path = f"{DirectoryPaths.CSV.value}/{test_name}.csv"
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            for sublist, val in probCombinations:
                numberOfRows: int = (int)(val * pow(10, maxDecimals))
                for _ in range(numberOfRows):
                    writer.writerow(sublist)
        return file_path
    else:
        data: List[List[int]] = []
        for sublist, val in probCombinations:
            numberOfRows: int = (int)(val * pow(10, maxDecimals))
            for _ in range(numberOfRows):
                data.append(sublist)
        df = pd.DataFrame(data, columns=header)
        return df


if __name__ == "__main__":
    """
    Generate a dataset in the csv format which is consistent with the specified
    distribution. As input, it needs: a header row for the csv, the probability
    of each outcome of the variables and the csv filename.
    """
    probabilities: ArrayType = [
        [[0, 0, 0], 0.288],
        [[0, 0, 1], 0.036],
        [[0, 1, 0], 0.288],
        [[0, 1, 1], 0.288],
        [[1, 0, 0], 0.002],
        [[1, 0, 1], 0.067],
        [[1, 1, 0], 0.017],
        [[1, 1, 1], 0.014],
    ]

    probsHelper(["Z", "X", "Y"], probabilities, "balke_pearl")

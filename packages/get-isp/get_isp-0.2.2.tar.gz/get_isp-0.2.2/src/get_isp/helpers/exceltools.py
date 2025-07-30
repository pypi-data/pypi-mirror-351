from concurrent.futures import ThreadPoolExecutor
import os
import re
import pandas as pd
from tqdm import tqdm

from get_isp.helpers.ispchecker import get_isp_info


def get_isp_from_api(input_file, telephone_column):
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"File not found: {input_file}")

        tqdm.pandas()
        df = pd.read_excel(input_file, dtype=str)

        if telephone_column not in df.columns:
            raise ValueError(f"Column '{telephone_column}' not found in the Excel file.")

        df[telephone_column] = df[telephone_column].fillna("").str.strip().apply(lambda x: re.sub(r"\D", "", x))

        df["ISP"] = ""

        valid_mask = (df[telephone_column].str.len() == 10) & df[telephone_column].str.startswith("0")
        valid_numbers = df.loc[valid_mask, telephone_column]

        with ThreadPoolExecutor(max_workers=10) as executor:
            isp_results = list(
                tqdm(
                    executor.map(get_isp_info, valid_numbers),
                    total=len(valid_numbers),
                )
            )
            df.loc[valid_mask, "ISP"] = isp_results

        return df
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()

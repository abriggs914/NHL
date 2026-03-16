import datetime
import random
from collections import OrderedDict
from typing import Optional, Any, Literal

import numpy as np
import pandas as pd

import utility
from pyodbc_connection import connect
from sql_utility import no_specials
from utility import excel_column_name

#######################################################################################################################
#######################################################################################################################
#######################################################################################################################


VERSION = \
    """	
    General Utility file for Dataframe operations
    Version..............1.07
    Date...........2026-01-29
    Author(s)....Avery Briggs
    """


def VERSION_DETAILS():
    return VERSION.lower().split("version")[0].strip()


def VERSION_NUMBER():
    return float(".".join(VERSION.lower().split("version")[-1].split("date")[0].split(".")[-2:]).strip())


def VERSION_DATE():
    return datetime.datetime.strptime(VERSION.lower().split("date")[-1].split("author")[0].split(".")[-1].strip(),
                                      "%Y-%m-%d")


def VERSION_AUTHORS():
    return [w.removeprefix(".").strip().title() for w in VERSION.lower().split("author(s)")[-1].split("..") if
            w.strip()]


#######################################################################################################################
#######################################################################################################################
#######################################################################################################################


def is_date_dtype(df, col_name):
    """
    Check if the data type of a column in a Pandas DataFrame is a today or time data type.
    Args:
        df (pandas.DataFrame): The DataFrame containing the column to check.
        col_name (str): The name of the column to check.
    Returns:
        bool: True if the column data type is a today or time data type, False otherwise.
    """
    dtype = df.dtypes[col_name]
    return np.issubdtype(dtype, np.datetime64) or np.issubdtype(dtype, np.timedelta64)


def is_numeric_dtype(df, col_name):
    """
    Check if the values in a column of a Pandas DataFrame are numerical.
    Args:
        df (pandas.DataFrame): The DataFrame containing the column to check.
        col_name (str): The name of the column to check.
    Returns:
        bool: True if the values in the column are numerical, False otherwise.
    """
    dtype = df.dtypes[col_name]
    return np.issubdtype(dtype, np.number)


def random_df(
        n_rows: int = 5,
        n_columns: Optional[list[str] | dict[str: str] | int] = None,
        dtypes: tuple[str] | str = ('int', 'float', 'str', 'datetime', 'bool', 'list'),
        empty_freq: float | dict[str: float] | list[float] = 0,
        defaults: Optional[dict[str: Any]] = None,
        allow_sub_lists: bool = True,
        index_cols: Optional[list[str] | int | str] = None,
        auto_number: Optional[list[str | int | str]] = None,
        **kwargs
) -> pd.DataFrame:
    """
    Generate random data for a DataFrame.
    Param 'defaults' will take precedence over ALL kwargs params.
    :param n_rows: Number of rows
    :param n_columns: Number of columns, or a list of column names, or a dict of columns and data types.
    :param dtypes: A tuple of primitive datatypes that will constrain the random data's data type.
                    If dtypes is a dictionary, then it will be unioned with n_columns such that dtypes overwrites n_columns.
    :param empty_freq: The frequency of None values in the result DataFrame.
    :param defaults: A dictionary of string column names and the available options when choosing a cell value. Can be a single value or a list of options.
    :param allow_sub_lists: Decide whether the random DataFrame can contain sub-lists as cell-values.
    :param kwargs: Optional params to constrain the random data even more:
            min_random_int -- default: -5
            max_random_int -- default: 5
            min_random_float -- default: -5
            max_random_float -- default: 5
            min_random_date -- default: 100 days ago
            max_random_date -- default: 100 days from now
            min_len_random_str -- default: 1
            max_len_random_str -- default: 5
            min_sub_list_len -- default: 0
            max_sub_list_len -- default: 3
            match_sub_list_lens -- default: False
            match_sub_list_dtypes -- default: False
    :return: pandas Dataframe
    """

    valid_dtypes = ('int', 'float', 'str', 'date', 'datetime', 'bool', 'list')
    valid_dtypes2 = ('int', 'float', 'str', 'date', 'datetime', 'bool')

    default_num_columns: int = 5
    min_random_int = kwargs.get("min_random_int", -5)
    max_random_int = kwargs.get("max_random_int", 5)
    min_random_float = kwargs.get("min_random_float", -5)
    max_random_float = kwargs.get("max_random_float", 5)
    min_random_date = kwargs.get("min_random_date", datetime.datetime.now().date() + datetime.timedelta(days=-100))
    max_random_date = kwargs.get("max_random_date", datetime.datetime.now().date() + datetime.timedelta(days=100))
    min_len_random_str = kwargs.get("min_len_random_str", 1)
    max_len_random_str = kwargs.get("max_len_random_str", 5)
    min_sub_list_len = kwargs.get("min_sub_list_len", 0)
    max_sub_list_len = kwargs.get("max_sub_list_len", 3)
    match_sub_list_lens = kwargs.get("match_sub_list_lens", False)
    match_sub_list_dtypes = kwargs.get("match_sub_list_dtypes", False)
    list_kwargs = [
        "min_random_int",
        "max_random_int",
        "min_random_float",
        "max_random_float",
        "min_random_date",
        "max_random_date",
        "min_len_random_str",
        "max_len_random_str",
        "min_sub_list_len",
        "max_sub_list_len",
        "match_sub_list_lens",
        "match_sub_list_dtypes"
    ]
    for kw in list_kwargs:
        if kw in kwargs:
            kwargs.pop(kw)
    if kwargs:
        raise ValueError(f"Unexpected kwargs leftover: {kwargs=}")

    if isinstance(dtypes, dict):
        if isinstance(n_columns, dict):
            if len(n_columns) < len(dtypes):
                raise ValueError(f"Only {len(n_columns)} columns explicitly declared via 'n_columns', 'dtypes' identifies {len(dtypes)}.")
            n_columns = n_columns.copy()
            n_columns.update(dtypes)
        # elif isinstance(n_columns, (list, tuple)):
        #     for col in dtypes:
        #         if col not in n_columns:
        #             n_columns.append(col)
        elif isinstance(n_columns, int) or n_columns is None:
            # n_columns = max(n_columns, len(dtypes))
            n_columns = default_num_columns if n_columns is None else n_columns
            if n_columns < len(dtypes):
                raise ValueError(f"'n_columns' is explicitly declared as {n_columns}, 'dtypes' identifies mmore than required. Please omit or increase 'n_columns', or remove unnecessary columns from 'dtypes'.'")

            num_c = n_columns if isinstance(n_columns, int) else len(n_columns)
            n_columns = OrderedDict(dtypes)
            if num_c > len(dtypes):
                new_cols = excel_column_name(num_c + len(dtypes), up_to=True)
                for col in dtypes:
                    if col in new_cols:
                        new_cols.remove(col)
                n_columns.update(dict(zip(new_cols, [random.choice(valid_dtypes) for _ in range(len(new_cols))])))
                n_columns = {col: n_columns[col] for col in list(n_columns.keys())[:num_c]}

    if (n_rows < 0) or (not isinstance(n_rows, int)):
        raise ValueError(f"'n_rows' must be an int greater than 0, got {n_rows=}, {type(n_rows)=}")
    if (not isinstance(n_columns, (list, dict, int, type(None)))) or (isinstance(n_columns, int) and (n_columns < 0)):
        raise ValueError(
            f"'n_columns' must be an int greater than 0, or a list of strings, or a dictionary of string column names paired with the expected column's data type. Got {n_columns=}, {type(n_columns)=}")
    if (not isinstance(empty_freq, (list, dict, float, int))) or (
            isinstance(empty_freq, (float, int)) and (not (0 <= empty_freq <= 1))) or (
            isinstance(empty_freq, list) and [ef for ef in empty_freq if not 0 <= ef <= 1]) or (
            isinstance(empty_freq, dict) and [ef for ef in empty_freq.values() if not 0 < ef < 1]):
        raise ValueError(
            f"'empty_freq' must be a float, or a list of floats, or a dictionary of string column names paired with floats, representing the 'empty_freq' (0 <= EF <= 1) for that column. Got {empty_freq=}, {type(empty_freq)=}")
    if (defaults is not None) and (not isinstance(defaults, dict)):
        raise ValueError(f"'defaults' must be None, or an instance of a dictionary. Got {defaults=}, {type(defaults)=}")

    if not isinstance(min_random_int, int):
        raise ValueError(f"'min_random_int' must be an int, got: {min_random_int=}, {type(min_random_int)}")
    if not isinstance(max_random_int, int):
        raise ValueError(f"'max_random_int' must be an int, got: {max_random_int=}, {type(max_random_int)}")
    if not isinstance(min_random_float, (float, int)):
        raise ValueError(f"'min_random_float' must be an float, got: {min_random_float=}, {type(min_random_float)}")
    if not isinstance(max_random_float, (float, int)):
        raise ValueError(f"'max_random_float' must be an float, got: {max_random_float=}, {type(max_random_float)}")
    if not isinstance(min_random_date, (datetime.datetime, datetime.date, pd.Timestamp)):
        raise ValueError(
            f"'min_random_date' must be an datetime.datetime, datetime.today, or pd.Timestamp, got: {min_random_date=}, {type(min_random_date)}")
    if not isinstance(max_random_date, (datetime.datetime, datetime.date, pd.Timestamp)):
        raise ValueError(
            f"'max_random_date' must be an datetime.datetime, datetime.today, or pd.Timestamp, got: {max_random_date=}, {type(max_random_date)}")
    if not isinstance(min_len_random_str, int):
        raise ValueError(f"'min_len_random_str' must be an int, got: {min_len_random_str=}, {type(min_len_random_str)}")
    if not isinstance(max_len_random_str, int):
        raise ValueError(f"'max_len_random_str' must be an int, got: {max_len_random_str=}, {type(max_len_random_str)}")
    if not isinstance(min_sub_list_len, int):
        raise ValueError(f"'min_sub_list_len' must be an int, got: {min_sub_list_len=}, {type(min_sub_list_len)}")
    if not isinstance(max_sub_list_len, int):
        raise ValueError(f"'max_sub_list_len' must be an int, got: {max_sub_list_len=}, {type(max_sub_list_len)}")
    if not isinstance(match_sub_list_lens, bool):
        raise ValueError(
            f"'match_sub_list_lens' must be an bool, got: {match_sub_list_lens=}, {type(match_sub_list_lens)}")
    if not isinstance(match_sub_list_dtypes, bool):
        raise ValueError(
            f"'match_sub_list_dtypes' must be an bool, got: {match_sub_list_dtypes=}, {type(match_sub_list_dtypes)}")

    if not isinstance(allow_sub_lists, bool):
        raise ValueError(f"'allow_sub_lists' must be an bool, got: {allow_sub_lists=}, {type(allow_sub_lists)}")

    min_random_int, max_random_int = utility.minmax(min_random_int, max_random_int)
    min_random_float, max_random_float = utility.minmax(min_random_float, max_random_float)
    min_random_date, max_random_date = utility.minmax(min_random_date, max_random_date)
    min_len_random_str, max_len_random_str = utility.minmax(min_len_random_str, max_len_random_str)
    min_sub_list_len, max_sub_list_len = utility.minmax(min_sub_list_len, max_sub_list_len)

    n_c = default_num_columns if n_columns is None else n_columns
    n_c = len(n_c) if isinstance(n_c, (list, dict)) else n_c
    valid_cols = excel_column_name(n_c - 1)
    cn = valid_cols
    if isinstance(n_columns, (list, dict)) and all(n_columns) and (len(n_columns) == n_c):
        cn = list(n_columns)

    index_cols: list = index_cols if isinstance(index_cols, (list, tuple, dict)) else ([index_cols] if isinstance(index_cols, (int, str)) else [])
    auto_number: list = auto_number if isinstance(auto_number, (list, tuple, dict)) else ([auto_number] if isinstance(auto_number, (int, str)) else [])
    for i, col in enumerate(index_cols.copy()):
        if isinstance(col, int):
            index_cols[i] = cn[col]
    for i, col in enumerate(auto_number.copy()):
        if isinstance(col, int):
            auto_number[i] = cn[col]

    if index_cols:
        if set(index_cols).difference(set(cn)):
            raise ValueError(f"columns passed via 'index_cols'={index_cols} do not match output columns {cn}")
    if auto_number:
        if set(auto_number).difference(set(cn)):
            raise ValueError(f"columns passed via 'auto_number'={auto_number} do not match output columns {cn}")

    if isinstance(empty_freq, list) and (len(empty_freq) < n_c):
        raise ValueError(
            f"when passing a list for param 'empty_freq', it's length must be at least as long as the number of columns that will be created. (len(empty_freq) < len(n_columns)).")

    if index_cols and isinstance(empty_freq, (list, tuple, dict)):
        if set(index_cols).union(set(empty_freq)):
            raise ValueError(f"columns passed via 'index_cols'={index_cols} can not have empty values via the 'empty_freq' param.")
    if auto_number and isinstance(empty_freq, (list, tuple, dict)):
        if set(auto_number).union(set(empty_freq)):
            raise ValueError(f"columns passed via 'auto_number'={auto_number} can not have empty values via the 'empty_freq' param.")
        for col in auto_number.copy():
            if col not in index_cols:
                index_cols.append(col)

    if not isinstance(dtypes, (list, tuple)):
        dtypes = [dtypes]
    elif isinstance(dtypes, tuple):
        dtypes = list(dtypes)

    if isinstance(n_columns, dict):
        dtypes = [d_t for d_t in dtypes if d_t in n_columns.values()]

    if not allow_sub_lists:
        if "list" in dtypes:
            dtypes.remove("list")

    dt = [d_t for d_t in dtypes if d_t in valid_dtypes]
    dt2 = [d_t for d_t in dtypes if d_t in valid_dtypes2]
    if not dt:
        dt = valid_dtypes
    if not dt2:
        dt2 = valid_dtypes2
        if (len(dt) == 1) and (dt[0] == "list"):
            dt = valid_dtypes

    indexed = {}
    defaults = {} if defaults is None else defaults
    # defaults = {k: random.choice(v) if isinstance(v, list) else v for k, v in defaults.items()}
    defaults = {k: (lambda v_=v: random.choice(v_)) if isinstance(v, list) else v for k, v in defaults.items()}

    cn_dt = list(n_columns.values()) if isinstance(n_columns, dict) else [random.choice(dt) for _ in cn]
    matching_cn_dt = random.choice(dt2)
    matching_sub_len = random.randint(min_sub_list_len, max_sub_list_len)
    # lens_sub = [matching_sub_len if match_sub_list_lens else random.randint(min_sub_list_len, max_sub_list_len) for i in range(max_sub_list_len + 1)]
    cn_dt_sub = [matching_cn_dt if match_sub_list_dtypes else random.choice(dt2) for i in range(max_sub_list_len + 1)]
    cn_ef = [empty_freq.get(col, 0) if isinstance(empty_freq, dict) else (
        empty_freq[i] if isinstance(empty_freq, list) else empty_freq) for i, col in enumerate(cn)]
    cn_ef_sub = [[empty_freq.get(col, 0) if isinstance(empty_freq, dict) else (
        empty_freq[i] if isinstance(empty_freq, list) else empty_freq) for j in range(max_sub_list_len + 1)] for i, col
                 in enumerate(cn)]

    print(f"{n_columns=}")
    print(f"{defaults=}")
    print(f"{dtypes=}")
    print(f"{index_cols=}")
    print(f"{auto_number=}")

    print(f"{cn=}")
    print(f"{dt=}")
    print(f"{cn_dt=}")
    print(f"{cn_dt_sub=}")
    print(f"{cn_ef=}")
    print(f"{matching_cn_dt=}")
    print(f"{matching_sub_len=}")

    def get_random(dtype: Optional[str] = None, col_num: int = 0, nested: bool = False):
        # print(f"{dtype=}, {nested=}")
        if dtype.lower().strip() == "bool":
            return random.choice([True, False])
        if dtype.lower().strip() == "float":
            return utility.random_in_range(min_random_float, max_random_float)
        if dtype.lower().strip().replace("datetime.date", "date") == "date":
            return min_random_date + datetime.timedelta(
                days=random.randint(0, (max_random_date - min_random_date).days))
        if dtype.lower().strip().replace("datetime.datetime", "datetime") == "datetime":
            return min_random_date + datetime.timedelta(
                days=random.randint(0, (max_random_date - min_random_date).days))
        if dtype.lower().strip() == "str":
            return "".join([chr(random.randint(ord("A"), ord("Z"))) for i in
                            range(random.randint(max(0, min_len_random_str), max_len_random_str))])
        if not nested and (dtype.lower().strip() == "list"):
            return [(defaults.get(cn[col_num])()) if callable(defaults.get(cn[col_num])) else defaults.get(cn[col_num],
                                                                                                           (get_random(
                                                                                                               cn_dt_sub[
                                                                                                                   i],
                                                                                                               col_num=col_num,
                                                                                                               nested=True) if random.random() >
                                                                                                                               cn_ef_sub[
                                                                                                                                   col_num][
                                                                                                                                   i] else None))
                    for i in range(
                    matching_sub_len if match_sub_list_lens else random.randint(min_sub_list_len, max_sub_list_len))]
        elif nested and (dtype.lower().strip() == "list"):
            raise ValueError(
                "Cannot nest lists. Ensure that at least one other dtype is available to create random data with")
        if dtype.lower().strip() == "int":
            return random.randint(min_random_int, max_random_int)
        return (defaults.get(cn[col_num])()) if callable(defaults.get(cn[col_num])) else defaults.get(cn[col_num],
                                                                                                      get_random(
                                                                                                          random.choice(
                                                                                                              dt) if dtype is None else dtype,
                                                                                                          col_num=col_num))

    def get_index(col_num: int):
        col: str = cn[col_num]
        dtype = cn_dt[col_num]

        if col not in indexed:
            indexed[col] = []

        if col in auto_number:
            val = len(indexed[col])
        else:
            val = get_random(dtype, col_num=col_num, nested=False)
            while val in indexed[col]:
                val = get_random(dtype, col_num=col_num, nested=False)

        indexed[col].append(val)
        return val

    data = [
        dict(zip(cn, [get_index(j) if col in index_cols else ((defaults.get(cn[j])()) if callable(defaults.get(cn[j])) else defaults.get(cn[j],
                                                                                                 get_random(cn_dt[j],
                                                                                                            col_num=j) if random.random() >
                                                                                                                          cn_ef[
                                                                                                                              j] else None))
                      for j, col in enumerate(cn)]))
        for i in range(n_rows)
    ]
    return pd.DataFrame(data)


def top_n_with_other_bin(
        df: pd.DataFrame,
        column: str | list[str] | Any,
        top_n: int,
        other_label: str = "other"
) -> pd.DataFrame:
    """
    Returns a DataFrame with the top N most frequent values in a column and groups the rest into an 'other' bin.

    Args:
        df (pd.DataFrame): The input DataFrame.
        column (str): Column name to analyze.
        top_n (int): Number of top values to keep.
        other_label (str): Label for the aggregated 'other' bin.

    Returns:
        pd.DataFrame: A DataFrame with 'Value', 'Count', and 'Proportion' columns.
    """
    # Calculate counts and proportions
    counts = df[column].value_counts()
    proportions = df[column].value_counts(normalize=True)

    # Get top N values
    top_values = counts.head(top_n).index

    # Create result DataFrame
    top_df = pd.DataFrame({
        "Value": top_values,
        "Count": counts.loc[top_values].values,
        "Proportion": proportions.loc[top_values].values
    })

    # Handle 'other' values
    if len(counts) > top_n:
        other_count = counts.loc[~counts.index.isin(top_values)].sum()
        other_prop = proportions.loc[~proportions.index.isin(top_values)].sum()

        other_row = pd.DataFrame([{
            "Value": other_label,
            "Count": other_count,
            "Proportion": other_prop
        }])

        top_df = pd.concat([top_df, other_row], ignore_index=True)

    top_df["Value"] = top_df["Value"].apply(lambda v: list(v) if isinstance(v, tuple) else v)

    return top_df


def norm_columns(
        df: pd.DataFrame,
        date_position: Literal["start", "end", "ignore"] = "start",
        in_place: bool = True
) -> tuple[pd.DataFrame, dict[str, Any]]:

    def date_idx(txt: str) -> int:
        l_txt = txt.lower()
        try:
            return l_txt.index("date")
        except:
            return -1

    og_columns = df.columns.tolist()
    column_key = {}
    for col in og_columns:
        n_col = col
        l_col = str(col).lower()

        if date_position != "ignore":
            if (date_position == "end") and l_col.startswith("date"):
                d_idx = date_idx(col)
                n_col = f"{str(col)[d_idx+len("date"):].removeprefix("_").strip()}_Date"
            elif (date_position == "start") and l_col.endswith("date"):
                d_idx = date_idx(col)
                n_col = f"Date_{str(col)[:d_idx].removesuffix("_").strip()}"

        n_col = no_specials(n_col)

        column_key[col] = n_col
        if in_place:
            df = df.rename(columns={col: n_col})

    if len(set(df.columns)) != len(df.columns):
        raise ValueError(f"Got duplicate column names: ['{"', '".join(df.columns)}']")

    return df, column_key


if __name__ == '__main__':
    # # df = random_df(5, 3, match_sub_list_dtypes=True, dtypes=("list", "int"))
    # # print(df)
    # # print(random_df(n_columns=["Name", "Date", "Price", "Cust"]))
    # # print(
    # #     random_df(n_columns={"Name": "str", "Date": "datetime", "Price": "float", "Cust": "list"}, min_len_random_str=4,
    # #               max_len_random_str=4))
    # # print(random_df(n_columns={"Name": "str", "Date": "datetime", "Price": "float", "Cust": "list", "US": "bool"},
    # #                 min_len_random_str=4, max_len_random_str=4))
    # # print(random_df(n_columns={"Name": "list", "Cust": "list"}, max_sub_list_len=6))
    # # print(random_df(10, 6, dtypes="bool"))
    # # print(random_df(10, 6, min_sub_list_len=4, max_sub_list_len=5, match_sub_list_lens=False))
    # # print(random_df(10, 6, min_sub_list_len=0, max_sub_list_len=0, match_sub_list_lens=False))
    # # print(random_df(1, 1))
    # #
    # # print(random_df(3, 3, **{
    # #     "min_random_int": -8,
    # #     "max_random_int": -1,
    # #     "min_random_float": 100,
    # #     "max_random_float": -2,
    # #     "min_random_date": datetime.datetime(2021, 1, 1),
    # #     "max_random_date": datetime.datetime(2027, 12, 31, 23, 59, 59),
    # #     "min_len_random_str": -3,
    # #     "max_len_random_str": 7,
    # #     "min_sub_list_len": 14,
    # #     "max_sub_list_len": 6,
    # #     "match_sub_list_lens": False,
    # #     "match_sub_list_dtypes": True
    # # }))
    # #
    # # print(random_df(
    # #     3,
    # #     3,
    # #     empty_freq=0.3,
    # #     **{
    # #         "min_random_int": -8,
    # #         "max_random_int": -1,
    # #         "min_random_float": 100,
    # #         "max_random_float": -2,
    # #         "min_random_date": datetime.datetime(2021, 1, 1),
    # #         "max_random_date": datetime.datetime(2027, 12, 31, 23, 59, 59),
    # #         "min_len_random_str": -3,
    # #         "max_len_random_str": 7,
    # #         "min_sub_list_len": 14,
    # #         "max_sub_list_len": 6,
    # #         "match_sub_list_lens": False,
    # #         "match_sub_list_dtypes": True
    # #     }))
    # #
    # # print(random_df(
    # #     10,
    # #     3,
    # #     empty_freq=[0, 0.98, 1],
    # #     **{
    # #         "min_random_int": -8,
    # #         "max_random_int": -1,
    # #         "min_random_float": 100,
    # #         "max_random_float": -2,
    # #         "min_random_date": datetime.datetime(2021, 1, 1),
    # #         "max_random_date": datetime.datetime(2027, 12, 31, 23, 59, 59),
    # #         "min_len_random_str": -3,
    # #         "max_len_random_str": 7,
    # #         "min_sub_list_len": 14,
    # #         "max_sub_list_len": 6,
    # #         "match_sub_list_lens": False,
    # #         "match_sub_list_dtypes": True
    # #     }))
    # #
    # # print(random_df(
    # #     10,
    # #     3,
    # #     defaults={"A": [-1, -3, -5, -7, -9, -11], "B": 4, "C": 6, "D": 8, "E": 10},
    # #     **{
    # #         "min_random_int": -8,
    # #         "max_random_int": -1,
    # #         "min_random_float": 100,
    # #         "max_random_float": -2,
    # #         "min_random_date": datetime.datetime(2021, 1, 1),
    # #         "max_random_date": datetime.datetime(2027, 12, 31, 23, 59, 59),
    # #         "min_len_random_str": -3,
    # #         "max_len_random_str": 7,
    # #         "min_sub_list_len": 14,
    # #         "max_sub_list_len": 6,
    # #         "match_sub_list_lens": False,
    # #         "match_sub_list_dtypes": True
    # #     }))
    # #
    # # print(random_df(
    # #     10,
    # #     n_columns={"Name": "str", "Cust": "int", "CustType": "str", "Active": "bool"},
    # #     defaults={"CustType": ["A", "B", "C"], "Active": 1},
    # #     **{
    # #         "min_random_int": 16,
    # #         "max_random_int": 1,
    # #         "min_random_float": 100,
    # #         "max_random_float": -2,
    # #         "min_random_date": datetime.datetime(2021, 1, 1),
    # #         "max_random_date": datetime.datetime(2027, 12, 31, 23, 59, 59),
    # #         "min_len_random_str": 3,
    # #         "max_len_random_str": 7,
    # #         "min_sub_list_len": 14,
    # #         "max_sub_list_len": 6,
    # #         "match_sub_list_lens": False,
    # #         "match_sub_list_dtypes": True
    # #     }))
    # #
    # # print(random_df(
    # #     16,
    # #     {
    # #         "Model": "str",
    # #         "Group": "str",
    # #         "Section": "str",
    # #         "Desc": "str",
    # #         "Freq": "int",
    # #         "SortG": "int",
    # #         "SortSe": "int"
    # #     },
    # #     allow_sub_lists=False,
    # #     defaults={
    # #         "Model": ["A", "B", "C", "D", "E", "G", "H", "I", "J", "K", "L", "M", "N"],
    # #         "Group": ["Axle", "Deck", "GNK"],
    # #         "Freq": list(range(100)),
    # #         "Section": ["A", "B", "C", "D", "E", "F", "G"]
    # #     },
    # #     min_random_int=0,
    # #     max_random_int=9)
    # # )
    #
    # df_o = connect("SELECT TOP 1000 * FROM [Orders] ORDER BY [Order Date] DESC")
    #
    # df_o, df_o_key = norm_columns(df_o)
    # print("df_o")
    # print(df_o)
    # print("df_o.columns.tolist()")
    # print(df_o.columns.tolist())
    # print("df_o_key")
    # print(df_o_key)
    #
    # # Will throw an error because of duplicate column names
    # # df2 = pd.DataFrame({
    # #     "A": [1],
    # #     "A-": [2],
    # #     "A--": [3],
    # #     "A---": [4]
    # # })
    # # df_2, df_2_key = norm_columns(df2)
    # # print(df_2)
    #
    # def load_order_data(date_1: Optional[datetime.datetime] = None,
    #                     date_2: Optional[datetime.datetime] = None) -> pd.DataFrame:
    #     sql = """
    #           SELECT
    #               [O].[Quote Date]
    #                   , [O].[Order Date]
    #                   , [O].[Date Registered]
    #                   , [O].[Date Declined]
    #                   , [O].[Decline/Rejected]
    #                   , [O].[Date In Service]
    #                   , [O].[Invoice Date]
    #                   , [O].[Quote#]
    #                   , [O].[WO#]
    #                   , [O].[Serial Number]
    #                   , [O].[ProductID]
    #                   , [O].[Model No]
    #                   , [O].[US Sale]
    #                   , [O].[Price]
    #                   , ISNULL([P].[Prod Date], [P].[Prod Date2]) AS [ProdDate]
    #                   , ISNULL([P].[Prod Line], [P].[Prod Line2]) AS [ProdLine]
    #                   , [C].[Customer]
    #                   , [D].[COMPANY NAME]
    #           FROM
    #               [BWSdb].[dbo].[Orders] [O]
    #               LEFT JOIN
    #               [BWSdb].[dbo].[Production] [P]
    #           ON
    #               [O].[Quote#] = [P].[Quote#]
    #               LEFT JOIN
    #               [BWSdb].[dbo].[Customers] [C]
    #               ON
    #               [O].[CustID] = [C].[ID#]
    #               LEFT JOIN
    #               [BWSdb].[dbo].[Dealers] [D]
    #               ON
    #               [O].[DealerID] = [D].[ID]
    #           ;
    #           """
    #     df: pd.DataFrame = connect(sql)
    #     df, df_col_key = norm_columns(df, date_position="start")
    #
    #     date_cols = [col for col in df.columns if col.startswith("Date")]
    #     dfs = []
    #
    #     if date_1 is not None and date_2 is not None:
    #         # window
    #         for col in date_cols:
    #             dfs.append(df[(date_1 <= df[col]) & (df[col] <= date_2)])
    #     elif date_1 is not None:
    #         # since
    #         for col in date_cols:
    #             dfs.append(df[date_1 <= df[col]])
    #     elif date_2 is not None:
    #         # up-to
    #         for col in date_cols:
    #             dfs.append(df[df[col] <= date_2])
    #     else:
    #         return df
    #
    #     df = pd.concat(dfs)
    #     df.drop_duplicates(inplace=True)
    #
    #     return df
    #
    # df = load_order_data(date_1=datetime.datetime(2025, 10, 1), date_2=datetime.datetime(2025, 11, 30))
    # print(df)

    df3 = random_df(10, n_columns={"A": "datetime.date", "C": "datetime.date"})
    print(df3)

    df3 = random_df(3, dtypes={"A": "datetime.date", "C": "datetime.date"})
    print(df3)
    print(f"[A] and [C] should be datetime.dates as per dtypes")

    df3 = random_df(
        3,
        dtypes={"A": "datetime.date", "C": "datetime.date", "D": "int", "E": "int"},
        n_columns=6
    )
    print(df3)
    print(f"4 columns only, [A] and [C] should be datetime.dates as per dtypes")

import datetime
import tkinter
from typing import Any

import pandas

#######################################################################################################################
#######################################################################################################################
#######################################################################################################################

VERSION = \
    """	
    General JSON Centered Utility Functions
    Version..............1.04
    Date...........2026-03-16
    Author(s)....Avery Briggs
    """


def VERSION_DETAILS():
    return VERSION.lower().split("version")[0].strip()


def VERSION_NUMBER():
    return float(".".join(VERSION.lower().split("version")[-1].split("date")[0].split(".")[-2:]).strip())


def VERSION_DATE():
    return datetime.datetime.strptime(VERSION.lower().split("date")[-1].split("author")[0].split(".")[-1].strip(),
                                      "%Y-%m-%dictionary")


def VERSION_AUTHORS():
    return [w.removeprefix(".").strip().title() for w in VERSION.lower().split("author(s)")[-1].split("..") if
            w.strip()]


#######################################################################################################################
#######################################################################################################################
#######################################################################################################################


def jsonify(value: Any, t_depth: int = 0, in_line: bool = True) -> str:
    # print(f"t={type(value)}, {value=}")

    s_ = " " * 4 * t_depth
    s1_ = s_ + (" " * 4)

    if value is None:
        return "null"

    elif isinstance(value, dict):
        if in_line:
            return "{" + ", ".join([f"\"{jsonify(k).removeprefix(chr(34)).removesuffix(chr(34))}\": {jsonify(v, 0, True)}" for k, v in value.items()]) + "}"
        else:
            return f"{s_ if t_depth == 0 else ''}{{\n{s1_}" + f"\n{s1_}".join(
                [f"\"{jsonify(k, t_depth + 1, False).removeprefix(chr(34)).removesuffix(chr(34))}\": {jsonify(v, t_depth + 1, False)}," for k, v in value.items()])[
                                                              :-1] + f"\n{s_}}}"
    elif typ := isinstance(value, (list, tuple, set)):
        # if typ == set:
        #     p1, p2 = "{", "}"
        # elif typ == list:
        #     p1, p2 = "[", "]"
        # else:
        #     p1, p2 = "(", ")"
        p1, p2 = "[", "]"

        if in_line:
            return f"{p1}" + ", ".join([f"{jsonify(v, 0, True)}" for v in value]) + f"{p2}"
        else:
            return f"{s_ if t_depth == 0 else ''}{p1}\n{s1_}" + f"\n{s1_}".join(
                [f"{jsonify(v, t_depth + 1, False)}," for v in value])[:-1] + f"\n{s_}{p2}"
    elif isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, pandas.DataFrame):
        return value.to_json()

    elif isinstance(value, datetime.datetime):
        y, n, d, h, m, s = value.year, value.month, value.day, value.hour, value.minute, value.second
        return f"\"datetime.datetime({', '.join(map(str, [y, n, d, h, m, s]))})\""

    if isinstance(value, tkinter.Variable):
        if isinstance(value, tkinter.BooleanVar):
            return f"\"tkinter.BooleanVar(value={jsonify(value.get())})\""
        elif isinstance(value, tkinter.IntVar):
            return f"\"tkinter.IntVar(value={jsonify(value.get())})\""
        elif isinstance(value, tkinter.DoubleVar):
            return f"\"tkinter.DoubleVar(value={jsonify(value.get())})\""
        elif isinstance(value, tkinter.StringVar):
            return f"\"tkinter.StringVar(value={jsonify(value.get())})\""
        else:
            return f"\"tkinter.Variable(value={jsonify(value.get())})\""

    elif isinstance(value, str):
        return f"\"{value}\""
    elif hasattr(value, "__repr__"):
        rpr = repr(value)
        if all([
            "__main__" in rpr[:50],
            "object at" in rpr[:100],
            "<" in rpr[:5],
            ">" in rpr[-5:]
            ]):
            print(f"Object appears to have returned a generic repr string. This may not be json serializable.")
        return rpr
    elif hasattr(value, "__str__"):
        str_ = str(value)
        if all([
            "__main__" in str_[:50],
            "object at" in str_[:100],
            "<" in str_[:5],
            ">" in str_[-5:]
            ]):
            print(f"Object appears to have returned a generic str string. This may not be json serializable.")
        return str_
    else:
        return str(value)


    # def de_jsonify(value):
    #     if isinstance(value, str):
    #         if value.startswith("datetime.datetime(") and value.endswith(")") and value.count(",") == 5:
    #             # datetime


def peek_json(result, depth: int = 20):
    """
    Function takes a json object and attempts to gather all keys into a tree structure for viewing.
    If a list is found, assumes ALL list items are the same format as the first element, does not sample the rest.
    """
    def helper(data, d):
        if d > depth:
            return "..."

        if isinstance(data, dict):
            return {
                k: helper(v, d + 1)
                for k, v in data.items()
            }

        elif isinstance(data, list):
            if not data:
                return ["empty_list"]
            return [helper(data[0], d + 1)]

        elif isinstance(data, tuple):
            if not data:
                return ["empty_tuple"]
            return [helper(data[0], d + 1)]

        else:
            return type(data).__name__

    return helper(result, 0)


if __name__ == '__main__':
    tests = [
        1,
        -1,
        1.0,
        1e4,
        "None_",
        None,
        [],
        ["a", "b"],
        {"aa": 1, "b": 7},
        {"aa": 1, "b": {"1": [1, 3, 6]}},
        {"aa": datetime.datetime.now(), "b": {"1": [1, 3, {"a": 0, "b": [0, False, 0, {1: 3, 2: 4}]}]}, "c": "a"}
    ]

    for t in tests:
        print(f"\nv: '{t}'\n{jsonify(t, in_line=False)}")

import os
from datetime import datetime
from typing import Any, List, Optional

from dateutil import parser
from dotenv import dotenv_values
from pytz import timezone

from src.errors import ConfigurationError, KnownError
from src.sheets import Sheet

EST = timezone("US/Eastern")


def cast_bool(cell: str) -> bool:
    cell = str(cell).strip()

    # Default empty cells to a "No" boolean.
    if cell == "":
        cell = "No"

    if not (cell in ["Yes", "No", "TRUE", "FALSE"]):
        raise KnownError(f"Boolean cell value was not Yes or No; instead, was {cell}")
    return cell == "Yes" or cell == "TRUE"


def cast_date(cell: str, deadline: bool = True, optional: bool = False) -> Optional[datetime]:
    try:
        if optional and (cell is None or str(cell).strip() == ""):
            return None
        cell = str(cell).strip()
        suffix = " 11:59 PM" if deadline else ""
        return EST.localize(parser.parse(str(cell) + suffix))
    except Exception as err:
        raise KnownError(f"Could not convert cell to date format. Value = {cell}, Error = {err}.")


def cast_list_str(cell: str) -> List[str]:
    cell = str(cell).strip()
    if cell == "":
        return []
    items = [item.strip() for item in cell.split(",")]
    return items


def cast_list_int(cell: str) -> List[int]:
    cell = str(cell).strip()
    if cell == "":
        return []
    items = [int(item.strip()) for item in str(cell).split(",")]
    return items


def truncate(s, amount=300):
    s = str(s)
    if len(s) > amount:
        s = s[:amount] + "...see GCP for entire log."
    return s

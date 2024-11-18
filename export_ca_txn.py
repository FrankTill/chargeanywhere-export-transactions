"""
The module exports transactions from a particular Charge Anywhere channel.
"""

import os
import sys
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv
from loguru import logger

load_dotenv()
URL = os.getenv("CA_EXPORT_HOST", "")
KEY = os.getenv("CA_EXPORT_KEY", "")
SECRET = os.getenv("CA_EXPORT_SECRET", "")
FIELDS = os.getenv("FIELDS", "")
REPORT_NAME = os.getenv("REPORT_NAME", "")
START_DATE_STR = os.getenv("START_DATE", "")
END_DATE_STR = os.getenv("END_DATE", "")


def mandatory_values_loaded() -> bool:
    """Check whether all the mandatory values are loaded"""
    if "" in [URL, KEY, SECRET, REPORT_NAME, START_DATE_STR, END_DATE_STR]:
        return False
    return True


def get_to_date(from_date_str: str) -> str:
    """Get the to date string from the from date string"""
    from_date = datetime.strptime(from_date_str, "%m/%d/%Y")
    next_day = from_date + timedelta(days=1)
    return next_day.strftime("%m/%d/%Y")


def get_txn_data(from_date_str: str, to_date_str: str) -> str:
    """Get the transaction data for a range"""
    txn_data_in_range = ""
    query_body = {
        "ClientKey": KEY,
        "ClientSecret": SECRET,
        "DateFrom": from_date_str,
        "DateTo": to_date_str,
        "Fields": FIELDS,
    }
    resp = requests.get(url=URL, data=query_body, timeout=60)
    if resp.ok:
        txn_data_in_range = resp.text
    else:
        print(f"{resp.status_code}, {resp.text}")
    return txn_data_in_range


def write_report(txn_data: str) -> None:
    """Append the transaction data to the report"""
    with open(REPORT_NAME, "a", encoding="utf-8") as file:
        file.write(txn_data)


def main() -> None:
    """Get the transaction data for a time range and output a report"""
    if not mandatory_values_loaded():
        return
    logger.remove()
    logger.add(sys.stdout, level="INFO")
    from_date_str = START_DATE_STR
    to_date_str = get_to_date(from_date_str)
    end_date = datetime.strptime(END_DATE_STR, "%m/%d/%Y")
    with open(REPORT_NAME, "w", encoding="utf-8") as file:
        logger.info("Writing header")
        file.write(f"{FIELDS}\n")
    while datetime.strptime(to_date_str, "%m/%d/%Y").date() <= end_date.date():
        logger.info(f"Getting data for {from_date_str} to {to_date_str}")
        txn_data = get_txn_data(from_date_str, to_date_str)
        logger.info(f"Writing reports for {from_date_str} to {to_date_str}")
        write_report(txn_data)
        from_date_str = to_date_str
        to_date_str = get_to_date(from_date_str)


if __name__ == "__main__":
    main()

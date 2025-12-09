"""
Utility to pull departure congestion snapshots from Incheon Airport's open API.

The API is documented at:
  https://apis.data.go.kr/B551177/statusOfDepartureCongestion/getDepartureCongestion

Usage:
  export INCHEON_API_KEY="...your encoded service key..."
  python scripts/fetch_departure_congestion.py --pages 3 --rows 100 --out data/raw.csv

Notes:
  - The API only exposes recent 1-minute snapshots; pagination is shallow.
  - The key must be URL-encoded. You can grab it from the open data portal.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import datetime
from typing import List, TypedDict
from urllib.parse import unquote
import xml.etree.ElementTree as ET

import requests

BASE_URL = "https://apis.data.go.kr/B551177/statusOfDepartureCongestion/getDepartureCongestion"
ENV_KEY = "INCHEON_API_KEY"


class CongestionRow(TypedDict, total=False):
    terminalid: str
    gateid: str
    exitnumber: str
    gatenumber: str
    regdate: str  # yyyymmddHHMMSS
    congestion: str  # waitLength
    waittime: str  # minutes
    operatingtime: str


def _parse_xml_items(text: str) -> List[dict]:
    root = ET.fromstring(text)
    items_el = root.find(".//items")
    if items_el is None:
        return []
    items: List[dict] = []
    for item_el in items_el.findall("item"):
        item_dict = {child.tag: child.text for child in item_el}
        items.append(item_dict)
    return items


def _normalize_item(item: dict) -> CongestionRow:
    # Map API fields to our schema
    gate_id = item.get("gateId", "")
    exitnumber = ""
    if gate_id:
        # Extract number from pattern like DG1_E
        for part in gate_id.split("_"):
            if part.startswith("DG") and part[2:].isdigit():
                exitnumber = part[2:]
    return {
        "terminalid": item.get("terminalId", ""),
        "gateid": gate_id,
        "exitnumber": exitnumber,
        "gatenumber": gate_id,
        "regdate": item.get("occurtime", ""),
        "congestion": item.get("waitLength", ""),
        "waittime": item.get("waitTime", ""),
        "operatingtime": item.get("operatingTime", ""),
    }


def fetch_page(
    page: int,
    rows: int,
    *,
    terminal_id: str | None = None,
    gate_id: str | None = None,
    response_type: str = "xml",
    verbose: bool = False,
) -> List[CongestionRow]:
    raw_key = os.getenv(ENV_KEY)
    if not raw_key:
        raise RuntimeError(f"Missing API key in ${ENV_KEY}")
    # Unquote to avoid double-encoding (requests will encode parameters once)
    key = unquote(raw_key)

    params = {
        "serviceKey": key,
        "pageNo": page,
        "numOfRows": rows,
        "type": response_type,
    }
    if terminal_id:
        params["terminalId"] = terminal_id
    if gate_id:
        params["gateId"] = gate_id
    resp = requests.get(BASE_URL, params=params, timeout=15)
    resp.raise_for_status()
    if verbose:
        print(f"[debug] status={resp.status_code} url={resp.url}")
    try:
        data = resp.json()
        items = (
            data.get("response", {})
            .get("body", {})
            .get("items", {})
            .get("item", [])
        )
        if isinstance(items, dict):
            items = [items]
    except ValueError:
        # Fallback to XML parsing when API returns XML regardless of _type
        items = _parse_xml_items(resp.text)
        if verbose:
            print(f"[debug] parsed XML items count={len(items)}")
    return [_normalize_item(item) for item in items]


def write_csv(rows: List[CongestionRow], out_path: str) -> None:
    if not rows:
        print("No rows returned from API; nothing to write.", file=sys.stderr)
        return

    fieldnames = [
        "terminalid",
        "gateid",
        "exitnumber",
        "gatenumber",
        "regdate",
        "congestion",
        "waittime",
        "operatingtime",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"Wrote {len(rows)} rows to {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch departure congestion snapshots")
    parser.add_argument("--pages", type=int, default=1, help="Number of pages to pull")
    parser.add_argument("--rows", type=int, default=100, help="Rows per page")
    parser.add_argument(
        "--out",
        default=f"data/departure_congestion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        help="Output CSV path",
    )
    parser.add_argument("--terminal", dest="terminal_id", help="Filter by terminalId (e.g., P01)")
    parser.add_argument("--gate", dest="gate_id", help="Filter by gateId (e.g., DG2_E)")
    parser.add_argument(
        "--type",
        dest="response_type",
        choices=["xml", "json"],
        default="xml",
        help="API response type (xml/json). API may still return XML.",
    )
    parser.add_argument("--verbose", action="store_true", help="Print debug info and response URL")
    args = parser.parse_args()

    all_rows: List[CongestionRow] = []
    for page in range(1, args.pages + 1):
        page_rows = fetch_page(
            page,
            args.rows,
            terminal_id=args.terminal_id,
            gate_id=args.gate_id,
            response_type=args.response_type,
            verbose=args.verbose,
        )
        if not page_rows:
            break
        all_rows.extend(page_rows)

    write_csv(all_rows, args.out)


if __name__ == "__main__":
    main()

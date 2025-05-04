"""
tests/api_demo.py
Run a quick end‑to‑end pass against a local FastAPI invoice server.
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

import requests

BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
# SAMPLE_CSV = Path("sample-data/sample_invoices.csv")
# SAMPLE_CSV = Path("sample-data/invalid_invoice.csv")
SAMPLE_CSV = Path("sample-data/duplicate_invoice.csv")


def login(username: str, password: str) -> str:
    """Return JWT token string."""
    r = requests.post(
        f"{BASE_URL}/login",
        data={"username": username, "password": password},
        timeout=10,
    )
    if r.status_code != 200:
        sys.exit(f"Login failed for {username}: {r.text}")
    token = r.json()["access_token"]
    print(f"Logged in {username}")
    return token


def upload_csv(token: str, csv_path: Path) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    with csv_path.open("rb") as f:
        r = requests.post(
            f"{BASE_URL}/invoices/upload",
            headers=headers,
            files={"file": (csv_path.name, f, "text/csv")},
            timeout=30,
        )
    print("CSV upload:", r.status_code, r.text)
    r.raise_for_status()


def list_invoices(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/invoices", headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()
    print("Invoices:", json.dumps(data, indent=2))
    return data


def approve_first_pending(token: str, invoices: list[dict]) -> Optional[int]:
    headers = {"Authorization": f"Bearer {token}"}
    for inv in invoices:
        if inv["status"] == "Pending":
            inv_id = inv["id"]
            r = requests.post(
                f"{BASE_URL}/invoices/{inv_id}/approve",
                headers=headers,
                json={"comment": "Approved by script"},
                timeout=10,
            )
            print(f"Approve invoice {inv_id}:", r.status_code, r.text)
            r.raise_for_status()
            return inv_id
    print("No pending invoice to approve")
    return None


def show_history(token: str, inv_id: int):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(
        f"{BASE_URL}/invoices/{inv_id}/history", headers=headers, timeout=10
    )
    r.raise_for_status()
    print("History:", json.dumps(r.json(), indent=2))


def main():
    if not SAMPLE_CSV.exists():
        sys.exit(f"Sample CSV not found at {SAMPLE_CSV}")

    # 1. employee login & upload
    # emp_token = login("alice", "secret")
    # upload_csv(emp_token, SAMPLE_CSV)

    # 2. manager login & list / approve
    mgr_token = login("bob", "secret")
    all_invoices = list_invoices(mgr_token)
    if (inv_id := approve_first_pending(mgr_token, all_invoices)) is not None:
        show_history(mgr_token, inv_id)
    # show_history(mgr_token, 1)


if __name__ == "__main__":
    # main()
    upload_csv(login("alice", "secret"), SAMPLE_CSV)

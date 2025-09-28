#!/usr/bin/env python3
from backend.services.fx_service import fetch_eurjpy_from_ecb

if __name__ == "__main__":
    data = fetch_eurjpy_from_ecb()
    print("EUR/JPY updated:", data["date"], data["spot"])

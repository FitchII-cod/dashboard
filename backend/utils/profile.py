from flask import request
from backend.config import PROFILES, DEFAULT_PROFILE

def get_profile_id() -> str:
    q = request.args.get("profile")
    if q in PROFILES:
        return q
    c = request.cookies.get("profile")
    if c in PROFILES:
        return c
    return DEFAULT_PROFILE

def get_profile():
    pid = get_profile_id()
    return pid, PROFILES[pid]

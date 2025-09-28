from __future__ import annotations
import csv
from dataclasses import dataclass
from datetime import date, datetime, timedelta
import zoneinfo
from typing import Optional
from backend.config import TZ

WEEKDAY_JP = ["月","火","水","木","金","土","日"]
TZI = zoneinfo.ZoneInfo(TZ)

@dataclass
class Person:
    name: str
    kana: Optional[str]
    birthdate: Optional[date]
    month: int
    day: int
    relation: Optional[str]
    notes: Optional[str]

def parse_birthdate(s: str) -> tuple[Optional[date], int, int]:
    s = s.strip()
    if s.startswith("--"):
        m, d = int(s[2:4]), int(s[5:7])
        return None, m, d
    y, m, d = int(s[0:4]), int(s[5:7]), int(s[8:10])
    return date(y, m, d), m, d

def load_birthdays(csv_path: str) -> list[Person]:
    people = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            bd, m, d = parse_birthdate(row["date"])
            people.append(Person(
                name=row["name"].strip(),
                kana=(row.get("kana") or "").strip() or None,
                birthdate=bd,
                month=m, day=d,
                relation=(row.get("relation") or "").strip() or None,
                notes=(row.get("notes") or "").strip() or None,
            ))
    return people

def next_occurrence(month: int, day: int, today: date) -> date:
    year = today.year
    try:
        cand = date(year, month, day)
    except ValueError:
        if month == 2 and day == 29:
            cand = date(year, 2, 28)
        else:
            raise
    if cand < today:
        year += 1
        try:
            cand = date(year, month, day)
        except ValueError:
            if month == 2 and day == 29:
                cand = date(year, 2, 28)
            else:
                raise
    return cand

def compute_age(birthdate: Optional[date], on_date: date) -> Optional[int]:
    if not birthdate:
        return None
    years = on_date.year - birthdate.year
    if (on_date.month, on_date.day) < (birthdate.month, birthdate.day):
        years -= 1
    return years

def get_birthdays_view(csv_path: str) -> dict:
    today = datetime.now(TZI).date()
    people = load_birthdays(csv_path)
    today_list, upcoming_list = [], []

    for p in people:
        occ = next_occurrence(p.month, p.day, today)
        days_until = (occ - today).days
        age = compute_age(p.birthdate, occ)
        weekday = WEEKDAY_JP[occ.weekday()]
        entry = {
            "name": p.name,            # attendus en カタカナ
            "kana": p.kana,
            "date_str": f"{occ.month}月{occ.day}日（{weekday}）",
            "age": age,
            "days_until": days_until,
            "relation": p.relation,
            "notes": p.notes,
        }
        if days_until == 0:
            today_list.append(entry)
        elif 1 <= days_until <= 7:
            upcoming_list.append(entry)

    upcoming_list.sort(key=lambda x: x["days_until"])
    return {"today": today_list, "upcoming": upcoming_list}

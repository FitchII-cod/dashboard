# Ici tu brancheras ta vraie météo. On renvoie un mock lisible côté front.
def get_weather_today(profile_id: str) -> dict:
    # plus tard: choisir ville selon profil
    return {
        "city": "ナント",
        "cond": "晴れ時々くもり",
        "tmax": 26, "tmin": 17,
        "rainProb": 30,
        "windMs": 3, "windDir": "北",
        "deltaFromYesterday": 2
    }

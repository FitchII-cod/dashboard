# jobs/fetch_weather.py
from pathlib import Path
import json
import urllib.parse, urllib.request
from zoneinfo import ZoneInfo
import datetime as dt

# ====== CONFIG ======
BASE = Path(__file__).resolve().parents[1]
OUT  = BASE / "data" / "cache" / "weather_today.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

CITY_JA = "ナント"
LAT = 47.22
LON = -1.55
TZ  = ZoneInfo("Europe/Paris")

def fetch_open_meteo():
    daily = ",".join([
        "temperature_2m_max",
        "temperature_2m_min",
        "apparent_temperature_max",
        "apparent_temperature_min",
        "precipitation_sum",
        "precipitation_hours",
        "precipitation_probability_max",
        "snowfall_sum",
        "windspeed_10m_max",
        "windgusts_10m_max",
        "winddirection_10m_dominant",
        "sunrise",
        "sunset"
    ])
    hourly = ",".join([
        "temperature_2m",
        "apparent_temperature",
        "relativehumidity_2m",
        "cloudcover",
        "precipitation",
        "precipitation_probability",
        "winddirection_10m",
        "windspeed_10m"
    ])
    params = {
        "latitude": LAT,
        "longitude": LON,
        "timezone": "Europe/Paris",
        "daily": daily,
        "hourly": hourly,
        "past_days": 1
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

def wind_dir_jp(deg: float) -> str:
    dirs16 = ["北","北北東","北東","東北東","東","東南東","南東","南南東","南","南南西","南西","西南西","西","西北西","北西","北北西"]
    idx = int((deg + 11.25) // 22.5) % 16
    name = dirs16[idx]
    simplify = {"北北東":"北東","東北東":"北東","東南東":"南東","南南東":"南東","南南西":"南西","西南西":"南西","西北西":"北西","北北西":"北西"}
    return simplify.get(name, name)

def wind_strength_word(ms: float) -> str:
    if ms is None: return "—"
    if ms < 2:  return "弱い風"
    if ms < 5:  return "やや強い風"
    if ms < 8:  return "強い風"
    if ms < 12: return "非常に強い風"
    return "暴風"

def label_cloud(c:int) -> str:
    if c <= 20: return "快晴"
    if c <= 40: return "晴れ"
    if c <= 60: return "晴れ時々曇り"
    if c <= 80: return "曇り"
    return "曇りがち"

def cond_from_series(clouds_morning, clouds_afternoon, rain_prob_max, precip_sum, snow_sum):
    # priorité aux précipitations/neige
    if snow_sum and snow_sum > 0:
        return "雪"
    if precip_sum and precip_sum >= 10:
        return "大雨"
    if precip_sum and precip_sum > 0:
        return "雨"
    if rain_prob_max >= 60:
        return "にわか雨の可能性"

    am = round(sum(clouds_morning)/len(clouds_morning)) if clouds_morning else 50
    pm = round(sum(clouds_afternoon)/len(clouds_afternoon)) if clouds_afternoon else 50
    if abs(am - pm) >= 25:
        return f"{label_cloud(am)}のち{label_cloud(pm)}"
    return label_cloud((am+pm)//2)

def jp_delta_phrase(delta):
    if delta is None: return ""
    if delta >= 3: return "昨日よりかなり暖かいです。"
    if delta >= 1: return "昨日より少し暖かいです。"
    if delta <= -3: return "昨日よりかなり寒いです。"
    if delta <= -1: return "昨日より少し寒いです。"
    return "昨日と同じくらいです。"

def humidity_word(avg_hum):
    if avg_hum is None: return ""
    if avg_hum >= 80: return "湿度が高めです。"
    if avg_hum <= 35: return "乾燥しています。"
    return ""

def laundry_hint(rain_prob, clouds_pm):
    if rain_prob >= 60: return "洗濯物は室内推奨。"
    if rain_prob >= 30: return "一時的なにわか雨に注意。"
    avg = round(sum(clouds_pm)/len(clouds_pm)) if clouds_pm else 50
    if avg <= 40: return "洗濯日和です。"
    if avg <= 70: return "外干しは早めの取り込みを。"
    return "外干しは控えめに。"

def detail_phrase(am_clouds, pm_clouds, hourly_pprob_today):
    """Génère '午前は〜、午後は〜' et signale la pluie probable."""
    txts = []
    if am_clouds:
        txts.append(f"午前は{label_cloud(round(sum(am_clouds)/len(am_clouds)))}")
    if pm_clouds:
        txts.append(f"午後は{label_cloud(round(sum(pm_clouds)/len(pm_clouds)))}")
    detail = "、".join(txts) if txts else ""
    # si au moins 3h ≥60% de prob pluie, ajoute un avertissement
    if hourly_pprob_today and sum(1 for p in hourly_pprob_today if p >= 60) >= 3:
        detail = (detail + "。") if detail else detail
        detail += "にわか雨に注意。"
    return detail or "—"

def main():
    raw = fetch_open_meteo()
    daily  = raw.get("daily", {})
    hourly = raw.get("hourly", {})
    now_local = dt.datetime.now(TZ)
    key = now_local.replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:00")

    dtime  = daily.get("time", [])
    today  = dt.datetime.now(TZ).date().isoformat()
    yday   = (dt.datetime.now(TZ).date() - dt.timedelta(days=1)).isoformat()

    tcur = None
    htime = hourly.get("time", [])
    htemp = hourly.get("temperature_2m", [])
    idx_map = {t:i for i,t in enumerate(htime)}
    if key in idx_map and htemp:
        tcur = round(htemp[idx_map[key]])

    try:
        i_today = dtime.index(today)
    except ValueError:
        i_today = len(dtime)-1 if dtime else 0
    i_yday = dtime.index(yday) if yday in dtime else None

    # Agrégats daily
    tmax = round(daily.get("temperature_2m_max", [None])[i_today]) if daily.get("temperature_2m_max") else None
    tmin = round(daily.get("temperature_2m_min", [None])[i_today]) if daily.get("temperature_2m_min") else None
    app_max = round(daily.get("apparent_temperature_max", [None])[i_today]) if daily.get("apparent_temperature_max") else None
    precip_sum = daily.get("precipitation_sum", [0])[i_today] if daily.get("precipitation_sum") else 0
    precip_hours = daily.get("precipitation_hours", [0])[i_today] if daily.get("precipitation_hours") else 0
    rain_prob_max = int(daily.get("precipitation_probability_max", [0])[i_today]) if daily.get("precipitation_probability_max") else 0
    snow_sum = daily.get("snowfall_sum", [0])[i_today] if daily.get("snowfall_sum") else 0
    wind_kmh = daily.get("windspeed_10m_max", [None])[i_today] if daily.get("windspeed_10m_max") else None
    wind_ms = round(float(wind_kmh)/3.6) if wind_kmh is not None else None
    wind_dir_deg = daily.get("winddirection_10m_dominant", [None])[i_today] if daily.get("winddirection_10m_dominant") else None
    wind_dir = wind_dir_jp(float(wind_dir_deg)) if wind_dir_deg is not None else "—"
    sunrise = daily.get("sunrise", [None])[i_today] if daily.get("sunrise") else None
    sunset  = daily.get("sunset",  [None])[i_today] if daily.get("sunset")  else None

    delta = None
    if i_yday is not None and daily.get("temperature_2m_max"):
        delta = round(daily["temperature_2m_max"][i_today] - daily["temperature_2m_max"][i_yday])

    # Découpes horaires du jour
    htime   = hourly.get("time", [])
    hcloud  = hourly.get("cloudcover", [])
    hhum    = hourly.get("relativehumidity_2m", [])
    hpprob  = hourly.get("precipitation_probability", [])
    am_clouds, pm_clouds, hum_vals, pprob_today = [], [], [], []
    for t, c in zip(htime, hcloud or []):
        if t.startswith(today):
            hh = int(t[11:13])
            if 6 <= hh <= 11: am_clouds.append(int(c))
            if 12 <= hh <= 18: pm_clouds.append(int(c))
    for t, h in zip(htime, hhum or []):
        if t.startswith(today): hum_vals.append(int(h))
    for t, p in zip(htime, hpprob or []):
        if t.startswith(today): pprob_today.append(int(p))

    avg_hum = round(sum(hum_vals)/len(hum_vals)) if hum_vals else None
    cond = cond_from_series(am_clouds, pm_clouds, rain_prob_max, precip_sum, snow_sum)
    detail = detail_phrase(am_clouds, pm_clouds, pprob_today)

    # Hint naturel (comparatif, humidité, lessive, vent, lever/coucher)
    parts = []
    if delta is not None:
        parts.append(jp_delta_phrase(delta))
    if avg_hum is not None:
        hw = humidity_word(avg_hum)
        if hw: parts.append(hw)
    parts.append(laundry_hint(rain_prob_max, pm_clouds))
    if wind_ms is not None:
        parts.append(f"{wind_strength_word(wind_ms)}（{wind_ms}m/s、{wind_dir}風）。")
    if sunrise and sunset:
        parts.append(f"日の出は{sunrise[11:16]}、日没は{sunset[11:16]}。")
    hint = " ".join(p for p in parts if p).replace("。 ", "。")

    payload = {
        "city": CITY_JA,
        "cond": cond,
        "detail": detail,                
        "tmax": tmax,
        "tmin": tmin,
        "tmaxApparent": app_max,
        "rainProb": rain_prob_max,
        "rainHours": precip_hours,
        "precipMm": round(precip_sum, 1) if precip_sum is not None else None,
        "snowMm": round(snow_sum, 1) if snow_sum is not None else None,
        "windMs": wind_ms,
        "windDir": wind_dir,
        "humidityAvg": avg_hum,
        "sunrise": sunrise,
        "sunset": sunset,
        "deltaFromYesterday": delta,
        "hint": hint,
        "tcur": tcur
    }

    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[weather] wrote {OUT} → {payload}")

if __name__ == "__main__":
    main()

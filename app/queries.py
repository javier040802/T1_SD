import numpy as np

def q1(data, zone, conf):
    return len(data[zone][data[zone].confidence >= conf])

def q2(data, zone, conf):
    df = data[zone][data[zone].confidence >= conf]
    return {
        "avg": df.area_in_meters.mean(),
        "total": df.area_in_meters.sum(),
        "n": len(df)
    }

def q3(data, zone, conf, area_km2):
    count = q1(data, zone, conf)
    return count / area_km2[zone]

def q4(data, z1, z2, conf, area_km2):
    d1 = q3(data, z1, conf, area_km2)
    d2 = q3(data, z2, conf, area_km2)
    return {"z1": d1, "z2": d2, "winner": z1 if d1 > d2 else z2}

def q5(data, zone, bins):
    scores = data[zone].confidence
    hist, edges = np.histogram(scores, bins=bins, range=(0,1))
    return hist.tolist()

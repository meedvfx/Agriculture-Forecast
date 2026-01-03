import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_historical(path="data/data.csv"):
    df = pd.read_csv(path)

    cols = df.columns.str.lower()
    mapping = {}
    if "product" in cols:
        mapping[[c for c in df.columns if c.lower()=="product"][0]] = "product"
    elif "produit" in cols:
        mapping[[c for c in df.columns if c.lower()=="produit"][0]] = "product"

    if "ds" in cols:
        mapping[[c for c in df.columns if c.lower()=="ds"][0]] = "ds"
    elif "date" in cols:
        mapping[[c for c in df.columns if c.lower()=="date"][0]] = "ds"
    elif "year" in cols:
        mapping[[c for c in df.columns if c.lower()=="year"][0]] = "ds"

    if "y" in cols:
        mapping[[c for c in df.columns if c.lower()=="y"][0]] = "y"
    elif "production" in cols:
        mapping[[c for c in df.columns if c.lower()=="production"][0]] = "y"
    elif "value" in cols:
        mapping[[c for c in df.columns if c.lower()=="value"][0]] = "y"
    elif "tonnes" in cols:
        mapping[[c for c in df.columns if c.lower()=="tonnes"][0]] = "y"


    real_map = {}
    for k in df.columns:
        kl = k.lower()
        if kl == "product" or kl == "produit":
            real_map[k] = "product"
        if kl in ("ds","date","year"):
            real_map[k] = "ds"
        if kl in ("y","production","value","tonnes","production_tonnes"):
            real_map[k] = "y"
    df = df.rename(columns=real_map)

    if "ds" not in df.columns:
        st.error("Impossible de trouver la colonne de date dans data.csv (nom attendu: ds/date/year).")
        return pd.DataFrame(columns=["product","ds","y"])

    try:
        df["ds"] = pd.to_datetime(df["ds"], errors="coerce", dayfirst=False)
        mask_na = df["ds"].isna()
        if mask_na.any():
            try:
                df.loc[mask_na, "ds"] = pd.to_datetime(df.loc[mask_na, "ds"].astype(str), format="%Y", errors="coerce")
            except Exception:
                pass
    except Exception:
        pass

    df = df[["product","ds","y"]].dropna(subset=["product","ds","y"])
    df = df.sort_values(["product","ds"])
    df["y"] = pd.to_numeric(df["y"], errors="coerce")
    df = df.dropna(subset=["y"])
    return df

@st.cache_data
def load_forecast(path="data/prevision_2040.csv"):
    df = pd.read_csv(path)
    cols = df.columns.str.lower()
    real_map = {}
    for k in df.columns:
        kl = k.lower()
        if kl in ("ds","date"):
            real_map[k] = "ds"
        if kl in ("yhat","prediction","y","prediction_en_tonnes"):
            real_map[k] = "yhat"
        if kl in ("product","produit"):
            real_map[k] = "product"
    df = df.rename(columns=real_map)
    if "ds" not in df.columns or "yhat" not in df.columns or "product" not in df.columns:
        st.error("Le fichier de prévisions doit contenir au minimum : date/ds, product, prediction/yhat.")
        return pd.DataFrame(columns=["product","ds","yhat"])
    df["ds"] = pd.to_datetime(df["ds"], errors="coerce")
    df["yhat"] = pd.to_numeric(df["yhat"], errors="coerce")
    df = df.dropna(subset=["ds","yhat","product"])
    df = df.sort_values(["product","ds"])
    df["year"] = df["ds"].dt.year
    df = df[(df["year"]>=2024) & (df["year"]<=2040)]
    return df

def get_stats_series(df_series):
    arr = np.array(df_series)
    if len(arr)==0:
        return {}
    mean = np.mean(arr)
    mn = np.min(arr)
    mx = np.max(arr)
    try:
        years = len(arr)
        yoy = np.diff(arr) / (arr[:-1] + 1e-9)
        mean_yoy = np.mean(yoy) * 100
    except Exception:
        mean_yoy = np.nan
    return {"mean": mean, "min": mn, "max": mx, "avg_yoy_pct": mean_yoy}

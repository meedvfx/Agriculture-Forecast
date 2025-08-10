# app_advanced.py
# Ultra-advanced Streamlit app: historique, prévisions, comparaison modèles (Naive, Prophet, SARIMA),
# random-search rapide, exports, scénarios. Visualisations matplotlib + plotly.

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from io import BytesIO
import os
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings("ignore")

# MODEL IMPORTS (may need installation)
try:
    from prophet import Prophet
except Exception:
    Prophet = None
try:
    import statsmodels.api as sm
    from statsmodels.tsa.statespace.sarimax import SARIMAX
except Exception:
    SARIMAX = None

# =============
# Helpers
# =============
st.set_page_config(layout="wide", page_title="Ultra Dashboard — Production & Prévisions")

@st.cache_data
def load_csv_local(path):
    return pd.read_csv(path)

def normalize_hist(df):
    # normalize to columns product, ds, y
    df = df.copy()
    cols = {c.lower(): c for c in df.columns}
    rename = {}
    # product
    for key in ("product","produit","produit_name","product_name"):
        if key in cols:
            rename[cols[key]] = "product"; break
    # date
    for key in ("ds","date","year","annee","année"):
        if key in cols:
            rename[cols[key]] = "ds"; break
    # value
    for key in ("y","production","value","tonnes","production_tonnes","quantite"):
        if key in cols:
            rename[cols[key]] = "y"; break
    df = df.rename(columns=rename)
    if "ds" in df.columns:
        df["ds"] = pd.to_datetime(df["ds"], errors="coerce")
        # try year-only fix
        mask = df["ds"].isna()
        if mask.any():
            try:
                df.loc[mask, "ds"] = pd.to_datetime(df.loc[mask, "ds"].astype(str), format="%Y", errors="coerce")
            except Exception:
                pass
    if "y" in df.columns:
        df["y"] = pd.to_numeric(df["y"], errors="coerce")
    df = df.dropna(subset=["product","ds","y"])
    df = df.sort_values(["product","ds"]).reset_index(drop=True)
    return df[["product","ds","y"]]

def normalize_forecast(df):
    df = df.copy()
    cols = {c.lower(): c for c in df.columns}
    rename = {}
    for key in ("product","produit"):
        if key in cols: rename[cols[key]] = "product"; break
    for key in ("ds","date","year"):
        if key in cols: rename[cols[key]] = "ds"; break
    for key in ("yhat","prediction","prediction_value","y"):
        if key in cols: rename[cols[key]] = "yhat"; break
    df = df.rename(columns=rename)
    if "ds" in df.columns:
        df["ds"] = pd.to_datetime(df["ds"], errors="coerce")
    if "yhat" in df.columns:
        df["yhat"] = pd.to_numeric(df["yhat"], errors="coerce")
    df = df.dropna(subset=["product","ds","yhat"])
    df = df.sort_values(["product","ds"]).reset_index(drop=True)
    return df[["product","ds","yhat"]]

def fig_to_bytes(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return buf

def agg_yearly(df, value_col="y"):
    df2 = df.copy()
    df2["year"] = df2["ds"].dt.year
    return df2.groupby("year", as_index=False)[value_col].sum()

def safe_metrics(y_true, y_pred):
    # handle constant or tiny arrays
    if len(y_true)==0 or len(y_pred)==0 or np.all(np.isnan(y_pred)):
        return {"r2": np.nan, "mae": np.nan, "mse": np.nan}
    try:
        r2 = r2_score(y_true, y_pred)
    except Exception:
        r2 = np.nan
    return {"r2": r2, "mae": mean_absolute_error(y_true, y_pred), "mse": mean_squared_error(y_true, y_pred)}

# =============
# Load data (local files only; no side config)
# =============
DATA_HIST = "data/dataclean.csv"
DATA_FORE = "data/prediction_2040.csv"

if os.path.exists(DATA_HIST):
    df_hist_raw = load_csv_local(DATA_HIST)
    df_hist = normalize_hist(df_hist_raw)
else:
    df_hist = pd.DataFrame(columns=["product","ds","y"])

if os.path.exists(DATA_FORE):
    df_fore_raw = load_csv_local(DATA_FORE)
    df_fore = normalize_forecast(df_fore_raw)
else:
    df_fore = pd.DataFrame(columns=["product","ds","yhat"])

# =============
# Sidebar - navigation and options
# =============
st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller à", ["Accueil","Historique","Prévisions","Model Compare","Scénarios & Export"])

# Global random-search settings (fast by default)
st.sidebar.markdown("### Random Search (rapide)")
RS_ITER = st.sidebar.slider("Iterations par modèle (par produit)", 10, 500, 50, step=10)
SARIMA_ORDER_TRY = st.sidebar.selectbox("SARIMA quick grid size", ["tiny","small","medium"], index=1)
st.sidebar.markdown("Prophet disponible: " + ("✅" if Prophet is not None else "❌"))
st.sidebar.markdown("SARIMAX disponible: " + ("✅" if SARIMAX is not None else "❌"))

# =============
# PAGE: Accueil
# =============
if page == "Accueil":
    st.title("Production & Prévisions — Ultra Developer Dashboard")
    st.markdown("Résumé des données chargées (fichiers recherchés: data.csv et previsions_futures_2040.csv)")
    c1,c2 = st.columns(2)
    c1.metric("Lignes historiques", len(df_hist))
    c1.metric("Produits historiques", df_hist["product"].nunique() if not df_hist.empty else 0)
    c2.metric("Lignes prévisions", len(df_fore))
    c2.metric("Produits prévisions", df_fore["product"].nunique() if not df_fore.empty else 0)
    st.markdown("---")
    st.markdown("**Raccourcis**")
    st.write("- Aller à Historique pour visualiser les séries (matplotlib + plotly).")
    st.write("- Aller à Model Compare pour tester Naïf / Prophet / SARIMA sur un produit (Random Search rapide possible).")
    st.write("- Scénarios & Export pour appliquer multiplicateurs et télécharger.")

# =============
# PAGE: Historique
# =============
if page == "Historique":
    st.header("Données historiques")
    if df_hist.empty:
        st.warning("Fichier data.csv introuvable ou vide. Place data.csv dans le dossier de l'app.")
    else:
        products = ["Tous"] + sorted(df_hist["product"].unique().tolist())
        sel = st.selectbox("Produit", products)
        # year slider
        min_y = int(df_hist["ds"].dt.year.min())
        max_y = int(df_hist["ds"].dt.year.max())
        y0, y1 = st.slider("Plage d'années", min_y, max_y, (min_y, max_y))
        df_sel = df_hist[(df_hist["ds"].dt.year>=y0) & (df_hist["ds"].dt.year<=y1)]
        if sel!="Tous":
            df_sel = df_sel[df_sel["product"]==sel]
        if df_sel.empty:
            st.info("Aucune donnée pour cette sélection.")
        else:
            df_year = agg_yearly(df_sel,"y")
            st.subheader("Graphique (matplotlib)")
            fig, ax = plt.subplots(figsize=(10,4))
            ax.plot(df_year["year"], df_year["y"], marker="o", color="tab:blue")
            ax.set_xlabel("Année"); ax.set_ylabel("Production"); ax.grid(alpha=0.3)
            st.pyplot(fig)
            buf = fig_to_bytes(fig)
            st.download_button("Télécharger graphique (PNG)", data=buf, file_name="historique.png", mime="image/png")
            st.subheader("Tableau")
            st.dataframe(df_sel.sort_values("ds").reset_index(drop=True))
            csv = df_sel.to_csv(index=False).encode("utf-8")
            st.download_button("Télécharger CSV (filtré)", data=csv, file_name="historique_filtre.csv", mime="text/csv")

# =============
# PAGE: Prévisions
# =============
if page == "Prévisions":
    st.header("Prévisions (2023→2040)")
    if df_fore.empty:
        st.warning("Fichier previsions_futures_2040.csv introuvable ou vide. Place le fichier dans le dossier de l'app.")
    else:
        prods = ["Tous"] + sorted(df_fore["product"].unique().tolist())
        selp = st.selectbox("Produit (prévision)", prods)
        dff = df_fore.copy()
        if selp!="Tous":
            dff = dff[dff["product"]==selp]
        if dff.empty:
            st.info("Aucune prévision pour la sélection.")
        else:
            df_year = agg_yearly(dff,"yhat")
            st.subheader("Graphique (prévision) - matplotlib")
            fig2, ax2 = plt.subplots(figsize=(10,4))
            ax2.plot(df_year["year"], df_year["yhat"], marker="o", color="orange")
            ax2.set_xlabel("Année"); ax2.set_ylabel("Prévision"); ax2.grid(alpha=0.3)
            st.pyplot(fig2)
            st.download_button("Télécharger graphique (PNG)", data=fig_to_bytes(fig2), file_name="prevision.png", mime="image/png")
            st.subheader("Tableau")
            st.dataframe(df_year.rename(columns={"year":"date","yhat":"prediction"}))
            st.download_button("Télécharger prévisions (CSV)", data=df_year.rename(columns={"year":"date","yhat":"prediction"}).to_csv(index=False).encode("utf-8"), file_name="previsions_2023_2040.csv")

# =============
# PAGE: Model Compare
# =============
if page == "Model Compare":
    st.header("Comparer modèles (Naïf / Prophet / SARIMA) — par produit")
    if df_hist.empty:
        st.warning("Data manquante.")
    else:
        product_list = sorted(df_hist["product"].unique().tolist())
        prod = st.selectbox("Produit à tester", product_list)
        # train/test split year
        split_year = st.number_input("Année de split (train < split, test >= split)", value=2023, min_value=int(df_hist["ds"].dt.year.min()), max_value=int(df_hist["ds"].dt.year.max()))
        dfp = df_hist[df_hist["product"]==prod].sort_values("ds")
        train = dfp[dfp["ds"].dt.year < split_year]
        test = dfp[dfp["ds"].dt.year >= split_year]
        st.write(f"Train len: {len(train)} — Test len: {len(test)}")
        if len(train)<3 or len(test)<1:
            st.error("Pas assez de données pour entraîner/tester. Besoin d'au moins 3 en train et 1 en test.")
        else:
            # Naive model (last value)
            last_value = train.sort_values("ds").iloc[-1]["y"]
            y_true = test["y"].values
            y_pred_naive = np.array([last_value]*len(test))
            metrics_naive = safe_metrics(y_true, y_pred_naive)

            st.subheader("Naïf (last value)")
            st.write(metrics_naive)

            # Prophet test (random search quick)
            metrics_prophet = {"r2":np.nan,"mae":np.nan,"mse":np.nan}
            best_prophet_params = None
            if Prophet is not None:
                n_it = RS_ITER
                best_score = -1e9
                for i in range(n_it):
                    # random small search - keep ranges small for speed
                    params = {
                        "changepoint_prior_scale": float(10**np.random.uniform(-4, -0.3)), # 1e-4..0.5
                        "seasonality_prior_scale": float(10**np.random.uniform(-2, 1)),    # 0.01..10
                        "holidays_prior_scale": float(10**np.random.uniform(-2, 1)),
                        "seasonality_mode": np.random.choice(["additive","multiplicative"]),
                    }
                    try:
                        m = Prophet(
                            yearly_seasonality=True,
                            weekly_seasonality=False,
                            daily_seasonality=False,
                            seasonality_mode=params["seasonality_mode"],
                            changepoint_prior_scale=params["changepoint_prior_scale"],
                            seasonality_prior_scale=params["seasonality_prior_scale"],
                            holidays_prior_scale=params["holidays_prior_scale"],
                        )
                        m.fit(train.rename(columns={"ds":"ds","y":"y"}))
                        fc = m.predict(test[["ds"]])
                        y_pred = fc["yhat"].values
                        met = safe_metrics(y_true,y_pred)
                        # small combined score (higher better)
                        score = ( (met["r2"] if not np.isnan(met["r2"]) else -10) ) - (met["mae"]/ (np.mean(y_true)+1e-9)) - (met["mse"]/(np.mean(y_true)**2+1e-9))
                        if score>best_score:
                            best_score = score
                            metrics_prophet = met
                            best_prophet_params = params
                    except Exception:
                        continue
                st.subheader("Prophet (random quick search)")
                st.write("Meilleurs metrics (approx):", metrics_prophet)
                st.write("Meilleurs params (approx):", best_prophet_params)
            else:
                st.info("Prophet non installé — saut du modèle Prophet.")

            # SARIMA quick test
            metrics_sarima = {"r2":np.nan,"mae":np.nan,"mse":np.nan}
            best_sarima = None
            if SARIMAX is not None:
                y_train = train.set_index("ds")["y"].astype(float)
                y_test = test.set_index("ds")["y"].astype(float)
                # quick grid depending choice
                if SARIMA_ORDER_TRY=="tiny":
                    pvals = [0,1]; dvals=[0,1]; qvals=[0,1]
                elif SARIMA_ORDER_TRY=="small":
                    pvals=[0,1,2]; dvals=[0,1]; qvals=[0,1]
                else:
                    pvals=[0,1,2]; dvals=[0,1]; qvals=[0,1,2]
                best_score=-1e9
                for p in pvals:
                    for d in dvals:
                        for q in qvals:
                            try:
                                mod = SARIMAX(y_train, order=(p,d,q), enforce_stationarity=False, enforce_invertibility=False)
                                res = mod.fit(disp=False, maxiter=200)
                                pred = res.get_prediction(start=y_test.index[0], end=y_test.index[-1], dynamic=False)
                                y_pred = pred.predicted_mean.values
                                met = safe_metrics(y_test.values, y_pred)
                                score = ( (met["r2"] if not np.isnan(met["r2"]) else -10) ) - (met["mae"]/ (np.mean(y_test)+1e-9)) - (met["mse"]/(np.mean(y_test)**2+1e-9))
                                if score>best_score:
                                    best_score=score
                                    metrics_sarima=met
                                    best_sarima=(p,d,q)
                            except Exception:
                                continue
                st.subheader("SARIMA quick-grid")
                st.write("Meilleurs metrics (approx):", metrics_sarima)
                st.write("Meilleur order (p,d,q):", best_sarima)
            else:
                st.info("statsmodels non installé — saut SARIMA.")

            # Summary table
            st.subheader("Résumé comparatif")
            df_comp = pd.DataFrame([
                {"model":"Naive","r2":metrics_naive["r2"], "mae":metrics_naive["mae"], "mse":metrics_naive["mse"]},
                {"model":"Prophet","r2":metrics_prophet["r2"], "mae":metrics_prophet["mae"], "mse":metrics_prophet["mse"]},
                {"model":"SARIMA","r2":metrics_sarima["r2"], "mae":metrics_sarima["mae"], "mse":metrics_sarima["mse"]},
            ])
            st.dataframe(df_comp)

# =============
# PAGE: Scénarios & Export
# =============
if page == "Scénarios & Export":
    st.header("Scénarios & Export")
    st.write("Appliquer multiplicateur de scénario sur prévisions et exporter.")
    if df_fore.empty:
        st.warning("Aucun fichier de prévisions (previsions_futures_2040.csv) trouvé.")
    else:
        prod_list = sorted(df_fore["product"].unique())
        prod_choice = st.selectbox("Produit (scénario)", prod_list)
        factor = st.slider("Multiplicateur", 0.5, 2.0, 1.0, 0.01)
        apply_all = st.checkbox("Appliquer à tous les produits", value=False)
        if st.button("Générer & Télécharger CSV scénario"):
            df_scn = df_fore.copy()
            if apply_all:
                df_scn["yhat_scn"] = df_scn["yhat"] * factor
            else:
                mask = df_scn["product"]==prod_choice
                df_scn["yhat_scn"] = df_scn["yhat"]
                df_scn.loc[mask, "yhat_scn"] = df_scn.loc[mask, "yhat"]*factor
            out = df_scn.copy()
            out["year"] = out["ds"].dt.year
            out_agg = out.groupby(["product","year"], as_index=False).agg({"yhat":"sum","yhat_scn":"sum"})
            csv = out_agg.to_csv(index=False).encode("utf-8")
            st.download_button("Télécharger scénario CSV", data=csv, file_name="previsions_scenario.csv", mime="text/csv")
            st.success("Scénario généré.")

# =============
# Footer / tips
# =============
st.sidebar.markdown("---")
st.sidebar.markdown("💡 Tips:")
st.sidebar.markdown("- Place `data.csv` and `previsions_futures_2040.csv` in the same folder as this app.")
st.sidebar.markdown("- Use smaller Random Search iterations for quick tests, raise for more accuracy.")

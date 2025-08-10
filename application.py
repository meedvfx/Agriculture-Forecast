# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import os
from typing import Tuple, Dict

st.set_page_config(page_title="Production & Prévisions — Dashboard", layout="wide")

# ---------------------------
# UTILITAIRES & CHARGEMENT
# ---------------------------

@st.cache_data
def safe_read_csv(path_or_buffer) -> pd.DataFrame:
    """Lecture csv sécurisée (chemin ou file-like)."""
    try:
        df = pd.read_csv(path_or_buffer)
        return df
    except Exception as e:
        raise

def detect_and_normalize_hist(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise le dataframe historique pour avoir les colonnes :
    ['product', 'ds', 'y'].
    - Accepte 'product' ou 'produit'
    - 'ds' ou 'date' ou 'year'
    - 'y' ou 'production' ou 'value' ou 'production_tonnes'
    """
    if df_raw is None or df_raw.empty:
        return pd.DataFrame(columns=["product","ds","y"])

    df = df_raw.copy()
    cols = {c.lower(): c for c in df.columns}
    mapping = {}

    # product
    for key in ("product","produit","produit_name"):
        if key in cols:
            mapping[cols[key]] = "product"
            break

    # date / year
    for key in ("ds","date","year","annee","année"):
        if key in cols:
            mapping[cols[key]] = "ds"
            break

    # value
    for key in ("y","production","value","tonnes","production_tonnes","quantite"):
        if key in cols:
            mapping[cols[key]] = "y"
            break

    df = df.rename(columns=mapping)
    if "ds" not in df.columns or "product" not in df.columns or "y" not in df.columns:
        # try to guess by positions if possible
        st.warning("Colonnes attendues non trouvées exactement — vérifie les noms (product, ds/date/year, y/production).")
        # try to coerce heuristically
    # convert dates
    if "ds" in df.columns:
        df["ds"] = pd.to_datetime(df["ds"], errors="coerce")
        # if many NaT, try treating as year
        if df["ds"].isna().sum() > 0 and df["ds"].notna().sum() > 0:
            mask = df["ds"].isna()
            try:
                df.loc[mask, "ds"] = pd.to_datetime(df.loc[mask, "ds"].astype(str), format="%Y", errors="coerce")
            except Exception:
                pass
    # numeric y
    if "y" in df.columns:
        df["y"] = pd.to_numeric(df["y"], errors="coerce")

    df = df.dropna(subset=["product","ds","y"])
    df = df.sort_values(["product","ds"]).reset_index(drop=True)
    return df[["product","ds","y"]]

def detect_and_normalize_forecast(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise les prévisions pour avoir : ['product', 'ds', 'yhat'].
    """
    if df_raw is None or df_raw.empty:
        return pd.DataFrame(columns=["product","ds","yhat"])
    df = df_raw.copy()
    cols = {c.lower(): c for c in df.columns}
    mapping = {}
    for key in ("product","produit"):
        if key in cols:
            mapping[cols[key]] = "product"
            break
    for key in ("ds","date","year"):
        if key in cols:
            mapping[cols[key]] = "ds"
            break
    for key in ("yhat","prediction","prediction_value","y", "production_tonnes"):
        if key in cols:
            mapping[cols[key]] = "yhat"
            break
    df = df.rename(columns=mapping)
    if "ds" in df.columns:
        df["ds"] = pd.to_datetime(df["ds"], errors="coerce")
    if "yhat" in df.columns:
        df["yhat"] = pd.to_numeric(df["yhat"], errors="coerce")
    df = df.dropna(subset=["product","ds","yhat"])
    df = df.sort_values(["product","ds"]).reset_index(drop=True)
    # reduce to yearly predictions between 2023 and 2040 if applicable
    df["year"] = df["ds"].dt.year
    df = df[(df["year"] >= 2023) & (df["year"] <= 2040)].reset_index(drop=True)
    return df[["product","ds","yhat"]]

def fig_to_bytes(fig) -> BytesIO:
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return buf

# ---------------------------
# LECTURE DES FICHIERS (fichiers locaux ou upload)
# ---------------------------
st.sidebar.title("Configuration & Fichiers")
st.sidebar.markdown("Charger les fichiers ou utiliser les fichiers par défaut dans le dossier du projet.")

# uploader ou paths
uploaded_hist = st.sidebar.file_uploader("Uploader data.csv (historique)", type=["csv"])
uploaded_fore = st.sidebar.file_uploader("Uploader previsions_futures_2040.csv (prévisions)", type=["csv"])

# default local paths
DEFAULT_HIST = "data.csv"
DEFAULT_FORE = "previsions_futures_2040.csv"

# load historic
df_hist_raw = None
try:
    if uploaded_hist is not None:
        df_hist_raw = safe_read_csv(uploaded_hist)
    elif os.path.exists(DEFAULT_HIST):
        df_hist_raw = safe_read_csv(DEFAULT_HIST)
    else:
        df_hist_raw = pd.DataFrame()
except Exception as e:
    st.sidebar.error(f"Impossible de lire le fichier historique: {e}")
    df_hist_raw = pd.DataFrame()

# load forecast
df_fore_raw = None
try:
    if uploaded_fore is not None:
        df_fore_raw = safe_read_csv(uploaded_fore)
    elif os.path.exists(DEFAULT_FORE):
        df_fore_raw = safe_read_csv(DEFAULT_FORE)
    else:
        df_fore_raw = pd.DataFrame()
except Exception as e:
    st.sidebar.error(f"Impossible de lire le fichier de prévisions: {e}")
    df_fore_raw = pd.DataFrame()

# normalize
df_hist = detect_and_normalize_hist(df_hist_raw)
df_fore = detect_and_normalize_forecast(df_fore_raw)

# ---------------------------
# NAVIGATION
# ---------------------------
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", ["Accueil", "Historique", "Prévisions", "Comparaison", "Export & Scénarios"])

# ---------------------------
# UTILS STATS
# ---------------------------
def compute_basic_stats(series: pd.Series) -> Dict[str, float]:
    arr = series.dropna().values
    if len(arr) == 0:
        return {"mean": np.nan, "min": np.nan, "max": np.nan, "avg_yoy_pct": np.nan}
    mean = float(np.mean(arr))
    mn = float(np.min(arr))
    mx = float(np.max(arr))
    # year on year average change in percent
    try:
        yoy = np.diff(arr) / (arr[:-1] + 1e-9)
        avg_yoy = float(np.mean(yoy) * 100)
    except Exception:
        avg_yoy = float("nan")
    return {"mean": mean, "min": mn, "max": mx, "avg_yoy_pct": avg_yoy}

# ---------------------------
# PAGE: Accueil
# ---------------------------
if page == "Accueil":
    st.title("Dashboard — Production & Prévisions (développeur)")
    st.markdown("**Résumé des données chargées**")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Lignes historiques", len(df_hist))
        st.metric("Produits historiques", df_hist["product"].nunique() if not df_hist.empty else 0)
    with c2:
        st.metric("Lignes prévisions 2023→2040", len(df_fore))
        st.metric("Produits prévisions", df_fore["product"].nunique() if not df_fore.empty else 0)
    st.markdown("---")
    st.markdown("**Notes / Vérifications**")
    st.write("- Si tu n'as pas uploadé les fichiers, l'app tente de charger `data.csv` et `previsions_futures_2040.csv` du dossier courant.")
    st.write("- Les graphiques utilisent matplotlib (export PNG disponible).")
    st.write("- Pages: Historique (bleu), Prévisions (orange) — pas de superposition graphique (tu l'avais demandé).")

# ---------------------------
# PAGE: Historique
# ---------------------------
if page == "Historique":
    st.header("Visualisation des données historiques")
    if df_hist.empty:
        st.warning("Aucune donnée historique chargée. Upload `data.csv` ou place-le dans le dossier de l'app.")
    else:
        products = ["Tous les produits"] + sorted(df_hist["product"].unique().tolist())
        sel_product = st.selectbox("Produit", products, index=1 if len(products)>1 else 0)
        years = df_hist["ds"].dt.year
        min_y, max_y = int(years.min()), int(years.max())
        sel_years = st.slider("Plage d'années", min_y, max_y, (min_y, max_y))

        # filter
        df_filt = df_hist.copy()
        if sel_product != "Tous les produits":
            df_filt = df_filt[df_filt["product"] == sel_product]
        df_filt = df_filt[(df_filt["ds"].dt.year >= sel_years[0]) & (df_filt["ds"].dt.year <= sel_years[1])]

        if df_filt.empty:
            st.info("Aucune donnée pour cette sélection.")
        else:
            # aggregate yearly (sum)
            df_plot = df_filt.copy()
            df_plot["year"] = df_plot["ds"].dt.year
            df_year = df_plot.groupby("year", as_index=False)["y"].sum()

            stats = compute_basic_stats(df_year["y"])
            st.subheader("KPI")
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Moyenne", f"{stats['mean']:.2f}")
            k2.metric("Min", f"{stats['min']:.2f}")
            k3.metric("Max", f"{stats['max']:.2f}")
            k4.metric("Croissance annuelle moyenne (YoY %)", f"{stats['avg_yoy_pct']:.2f}%")

            st.subheader("Graphique (Historique) - matplotlib")
            fig, ax = plt.subplots(figsize=(10,4))
            ax.plot(df_year["year"], df_year["y"], marker="o", color="tab:blue", linewidth=2)
            ax.set_xlabel("Année"); ax.set_ylabel("Production"); ax.grid(alpha=0.3)
            ax.set_title(f"Historique — {sel_product}")
            st.pyplot(fig)

            # download png
            buf = fig_to_bytes(fig)
            st.download_button("Télécharger graphique (PNG)", data=buf, file_name="historique.png", mime="image/png")

            st.subheader("Tableau (filtré)")
            st.dataframe(df_filt.sort_values("ds").reset_index(drop=True))

            csv_bytes = df_filt.to_csv(index=False).encode("utf-8")
            st.download_button("Télécharger données (CSV)", data=csv_bytes, file_name="historique_filtre.csv", mime="text/csv")

# ---------------------------
# PAGE: Prévisions
# ---------------------------
if page == "Prévisions":
    st.header("Prévisions futures (annuelles, 2023 → 2040)")
    if df_fore.empty:
        st.warning("Aucune prévision chargée. Upload `previsions_futures_2040.csv` ou place-le dans le dossier de l'app.")
    else:
        products_f = ["Tous les produits"] + sorted(df_fore["product"].unique().tolist())
        sel_product_f = st.selectbox("Produit (prévision)", products_f, index=1 if len(products_f)>1 else 0)

        df_filt = df_fore.copy()
        if sel_product_f != "Tous les produits":
            df_filt = df_filt[df_filt["product"] == sel_product_f]

        if df_filt.empty:
            st.info("Aucune prévision pour la sélection.")
        else:
            # aggregate yearly
            df_filt["year"] = df_filt["ds"].dt.year
            df_year = df_filt.groupby("year", as_index=False)["yhat"].sum()

            stats = compute_basic_stats(df_year["yhat"])
            st.subheader("KPI prévisionnel")
            c1, c2, c3 = st.columns(3)
            c1.metric("Moyenne prévue", f"{stats['mean']:.2f}")
            c2.metric("Min prévue", f"{stats['min']:.2f}")
            c3.metric("Max prévue", f"{stats['max']:.2f}")

            st.subheader("Graphique (Prévisions) - matplotlib")
            fig2, ax2 = plt.subplots(figsize=(10,4))
            ax2.plot(df_year["year"], df_year["yhat"], marker="o", color="orange", linewidth=2)
            ax2.set_xlabel("Année"); ax2.set_ylabel("Production prévue"); ax2.grid(alpha=0.3)
            ax2.set_title(f"Prévisions 2023→2040 — {sel_product_f}")
            st.pyplot(fig2)

            buf2 = fig_to_bytes(fig2)
            st.download_button("Télécharger graphique prévision (PNG)", data=buf2, file_name="prevision.png", mime="image/png")

            st.subheader("Tableau des prévisions (années)")
            st.dataframe(df_year.rename(columns={"year":"date","yhat":"prediction"}).reset_index(drop=True))
            csv_bytes_f = df_year.rename(columns={"year":"date","yhat":"prediction"}).to_csv(index=False).encode("utf-8")
            st.download_button("Télécharger prévisions (CSV)", data=csv_bytes_f, file_name="previsions_2023_2040.csv", mime="text/csv")

# ---------------------------
# PAGE: Comparaison (numérique, pas superposé)
# ---------------------------
if page == "Comparaison":
    st.header("Comparaison: dernier historique vs première prévision (numérique)")
    if df_hist.empty or df_fore.empty:
        st.warning("Charge les données historiques et les prévisions pour utiliser cette page.")
    else:
        prods_common = sorted(list(set(df_hist["product"].unique()) & set(df_fore["product"].unique())))
        if not prods_common:
            st.info("Aucun produit commun entre historique et prévisions.")
        else:
            sel = st.selectbox("Produit pour comparaison", prods_common)
            hist_p = df_hist[df_hist["product"]==sel].sort_values("ds")
            fore_p = df_fore[df_fore["product"]==sel].sort_values("ds")
            last_hist = hist_p.tail(1)
            first_fore = fore_p.head(1)
            if last_hist.empty or first_fore.empty:
                st.info("Données insuffisantes pour comparaison.")
            else:
                last_val = float(last_hist["y"].values[0])
                last_year = int(last_hist["ds"].dt.year.values[0])
                first_val = float(first_fore["yhat"].values[0])
                first_year = int(first_fore["ds"].dt.year.values[0])
                diff = first_val - last_val
                pct = (diff / (last_val + 1e-9)) * 100

                st.subheader(f"Produit: {sel}")
                st.metric("Dernière valeur historique", f"{last_val:.2f}", delta=None)
                st.metric("Première prévision (année)", f"{first_year}", delta=None)
                st.metric("Première prévision (valeur)", f"{first_val:.2f}", delta=f"{pct:.2f}%")

                # Table small
                st.markdown("**Détails**")
                st.write("Dernières lignes historiques :")
                st.dataframe(hist_p.tail(5))
                st.write("Premières lignes prévision :")
                st.dataframe(fore_p.head(5))

# ---------------------------
# PAGE: Export & Scénarios
# ---------------------------
if page == "Export & Scénarios":
    st.header("Export des données et scénarios")
    st.write("Générer des exports, appliquer des scénarios de croissance sur les prévisions et télécharger les résultats.")

    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("Exporter jeux de données")
        if not df_hist.empty:
            csv_hist = df_hist.to_csv(index=False).encode("utf-8")
            st.download_button("Télécharger historique (CSV)", data=csv_hist, file_name="historique_export.csv", mime="text/csv")
        if not df_fore.empty:
            csv_fore = df_fore.to_csv(index=False).encode("utf-8")
            st.download_button("Télécharger prévisions (raw) (CSV)", data=csv_fore, file_name="previsions_raw_export.csv", mime="text/csv")

    with col2:
        st.subheader("Scénarios sur prévision (facteur simple)")
        if df_fore.empty:
            st.info("Aucune prévision chargée.")
        else:
            prod_list = sorted(df_fore["product"].unique())
            prod_choice = st.selectbox("Produit (scénario)", prod_list)
            factor = st.slider("Multiplicateur de scénario (ex: 1.1 = +10%)", 0.5, 2.0, 1.0, 0.01)
            apply_to_all = st.checkbox("Appliquer le même facteur à tous les produits", value=False)

            if st.button("Appliquer scénario & télécharger"):
                if apply_to_all:
                    df_scn = df_fore.copy()
                    df_scn["yhat_scn"] = df_scn["yhat"] * factor
                else:
                    df_scn = df_fore.copy()
                    mask = df_scn["product"] == prod_choice
                    df_scn.loc[mask, "yhat_scn"] = df_scn.loc[mask, "yhat"] * factor
                    df_scn.loc[~mask, "yhat_scn"] = df_scn.loc[~mask, "yhat"]

                # aggregate yearly and export
                df_scn["year"] = df_scn["ds"].dt.year
                df_out = df_scn.groupby(["product","year"], as_index=False).agg({"yhat":"sum","yhat_scn":"sum"})
                csv_out = df_out.to_csv(index=False).encode("utf-8")
                st.download_button("Télécharger scénario (CSV)", data=csv_out, file_name="previsions_scenario.csv", mime="text/csv")
                st.success("Scénario appliqué et prêt au téléchargement.")

# ---------------------------
# Footer: recommandations
# ---------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("🔧 Conseils :")
st.sidebar.markdown("* Vérifie que `data.csv` contient `product`, `date` (ou `year`) et `production` (ou `y`).*")
st.sidebar.markdown("* Met à jour `previsions_futures_2040.csv` si tu veux recalculer les graphiques.*")
st.sidebar.markdown("* Pour recalculer modèles (Prophet), exécute ton notebook localement puis ré-uploade le CSV.*")

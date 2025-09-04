# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64

st.set_page_config(page_title="Dashboard Production", layout="wide")

# -----------------------
# Fonctions utilitaires
# -----------------------
@st.cache_data
def load_historical(path="data/dataclean2.csv"):
    df = pd.read_csv(path)
    # On s'attend à des colonnes au minimum : ['product', 'ds' or 'date' or 'Year', 'y' or 'production' or 'value']
    # On essaye d'identifier les colonnes communes
    cols = df.columns.str.lower()
    # normalize known names
    mapping = {}
    if "product" in cols:
        mapping[[c for c in df.columns if c.lower()=="product"][0]] = "product"
    elif "produit" in cols:
        mapping[[c for c in df.columns if c.lower()=="produit"][0]] = "product"

    # date column
    if "ds" in cols:
        mapping[[c for c in df.columns if c.lower()=="ds"][0]] = "ds"
    elif "date" in cols:
        mapping[[c for c in df.columns if c.lower()=="date"][0]] = "ds"
    elif "year" in cols:
        mapping[[c for c in df.columns if c.lower()=="year"][0]] = "ds"

    # value column
    if "y" in cols:
        mapping[[c for c in df.columns if c.lower()=="y"][0]] = "y"
    elif "production" in cols:
        mapping[[c for c in df.columns if c.lower()=="production"][0]] = "y"
    elif "value" in cols:
        mapping[[c for c in df.columns if c.lower()=="value"][0]] = "y"
    elif "tonnes" in cols:
        mapping[[c for c in df.columns if c.lower()=="tonnes"][0]] = "y"

    # apply mapping safely
    # mapping keys are lists because we used list comprehensions; normalize properly
    # rebuild mapping properly
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

    # Ensure ds exists
    if "ds" not in df.columns:
        st.error("Impossible de trouver la colonne de date dans data.csv (nom attendu: ds/date/year).")
        return pd.DataFrame(columns=["product","ds","y"])

    # Convertir ds en datetime (si year only, on force 01-01)
    try:
        # si année seulement (ex : 1986), to_datetime gère
        df["ds"] = pd.to_datetime(df["ds"], errors="coerce", dayfirst=False)
        # si conversion échoue mais valeurs comme '1986', faire format='%Y'
        mask_na = df["ds"].isna()
        if mask_na.any():
            # essayer en format année
            try:
                df.loc[mask_na, "ds"] = pd.to_datetime(df.loc[mask_na, "ds"].astype(str), format="%Y", errors="coerce")
            except Exception:
                pass
    except Exception:
        pass

    # garder colonnes utiles
    df = df[["product","ds","y"]].dropna(subset=["product","ds","y"])
    df = df.sort_values(["product","ds"])
    # for safety cast numeric
    df["y"] = pd.to_numeric(df["y"], errors="coerce")
    df = df.dropna(subset=["y"])
    return df

@st.cache_data
def load_forecast(path="data/prediction_2040.csv"):
    df = pd.read_csv(path)
    # expected columns: date/ds, product, prediction/yhat
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
    # réduire à années entières (si besoin), on met la date 01-01-YYYY
    df["year"] = df["ds"].dt.year
    # keep only 2023..2040 range just in case
    df = df[(df["year"]>=2024) & (df["year"]<=2040)]
    return df

def plot_matplotlib_timeseries(dates, values, title="", color="blue", figsize=(10,4)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(dates, values, marker="o", linestyle="-", color=color)
    ax.set_title(title)
    ax.set_xlabel("Année")
    ax.set_ylabel("Production")
    ax.grid(alpha=0.3)
    return fig

def get_stats_series(df_series):
    arr = np.array(df_series)
    if len(arr)==0:
        return {}
    mean = np.mean(arr)
    mn = np.min(arr)
    mx = np.max(arr)
    # CAGR-like average annual growth (geometric) if years >1 and positives
    try:
        years = len(arr)
        # better: compute year-on-year percentage mean
        yoy = np.diff(arr) / (arr[:-1] + 1e-9)
        mean_yoy = np.mean(yoy) * 100
    except Exception:
        mean_yoy = np.nan
    return {"mean": mean, "min": mn, "max": mx, "avg_yoy_pct": mean_yoy}

def fig_to_bytes(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return buf

# -----------------------
# Chargement des données
# -----------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller à", ["Accueil", "Historique", "Prévisions"])

# load once
with st.spinner("Chargement des données..."):
    df_hist = load_historical("data/dataclean.csv")
    df_fore = load_forecast("data/prediction_2040.csv")

# -----------------------
# PAGE: Accueil
# -----------------------
if page == "Accueil":
    st.title("Dashboard — Production & Prévisions")
    st.markdown("""
    **Résumé** :
    - Données historiques : {} lignes, {} produits.  
    - Prévisions (2023→2040) : {} lignes, {} produits.
    """.format(len(df_hist), df_hist["product"].nunique(), len(df_fore), df_fore["product"].nunique()))
    st.write("Sélectionnez une page dans la barre latérale pour visualiser les données historiques ou les prévisions futures.")
    st.markdown("**Fonctionnalités** : filtres par produit, export CSV, téléchargements d'images (matplotlib).")

# -----------------------
# PAGE: Historique
# -----------------------
if page == "Historique":
    st.header("Données historiques")
    if df_hist.empty:
        st.warning("Aucune donnée historique chargée (vérifie data.csv).")
    else:
        # selectors
        produits = sorted(df_hist["product"].unique())
        sel_product = st.selectbox("Choisir un produit", ["Tous les produits"] + produits, index=1 if len(produits)>0 else 0)
        min_year = int(df_hist["ds"].dt.year.min())
        max_year = int(df_hist["ds"].dt.year.max())
        year_range = st.slider("Plage d'années", min_year, max_year, (min_year, max_year))

        # filter
        df_filtered = df_hist.copy()
        if sel_product != "Tous les produits":
            df_filtered = df_filtered[df_filtered["product"]==sel_product]
        df_filtered = df_filtered[(df_filtered["ds"].dt.year>=year_range[0]) & (df_filtered["ds"].dt.year<=year_range[1])]

        # stats
        st.subheader("Statistiques")
        if df_filtered.empty:
            st.info("Aucune donnée pour la sélection.")
        else:
            stats = get_stats_series(df_filtered["y"].values)
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Moyenne", f"{stats['mean']:.2f}")
            c2.metric("Min", f"{stats['min']:.2f}")
            c3.metric("Max", f"{stats['max']:.2f}")
            c4.metric("Croissance moyenne YoY (%)", f"{stats['avg_yoy_pct']:.2f}%")

            # plot
            st.subheader("Graphique (Historique)")
            # aggregate per year to have yearly ticks
            df_plot = df_filtered.copy()
            df_plot["year"] = df_plot["ds"].dt.year
            df_year = df_plot.groupby("year", as_index=False)["y"].sum()
            fig = plot_matplotlib_timeseries(df_year["year"], df_year["y"],
                                            title=f"Historique — {sel_product if sel_product!='Tous les produits' else 'Tous produits'}",
                                            color="blue")
            st.pyplot(fig)

            # download image
            buf = fig_to_bytes(fig)
            st.download_button("Télécharger le graphique (PNG)", data=buf, file_name="historique.png", mime="image/png")

            # table
            st.subheader("Tableau")
            st.dataframe(df_filtered.sort_values("ds").reset_index(drop=True))

            # export csv
            csv_bytes = df_filtered.to_csv(index=False).encode("utf-8")
            st.download_button("Télécharger données filtrées (CSV)", data=csv_bytes, file_name="historique_filtre.csv", mime="text/csv")

# -----------------------
# PAGE: Prévisions
# -----------------------
if page == "Prévisions":
    st.header("Prévisions futures (2023 → 2040)")
    if df_fore.empty:
        st.warning("Aucune donnée de prévision chargée (vérifie previsions_futures_2040.csv).")
    else:
        produits_f = sorted(df_fore["product"].unique())
        sel_product_f = st.selectbox("Choisir un produit (prévision)", ["Tous les produits"] + produits_f, index=1 if len(produits_f)>0 else 0)

        # filter
        dff = df_fore.copy()
        if sel_product_f != "Tous les produits":
            dff = dff[dff["product"]==sel_product_f]
        # aggregate yearly (should already be yearly)
        df_year_f = dff.groupby(dff:=dff["ds"].dt.year).agg({"yhat":"sum"}).reset_index().rename(columns={dff.name:"year"})

        # stats on forecast per product
        st.subheader("Statistiques prévisionnelles")
        if df_year_f.empty:
            st.info("Aucune prévision pour la sélection.")
        else:
            stats_f = get_stats_series(df_year_f["yhat"].values)
            c1,c2,c3 = st.columns(3)
            c1.metric("Production moyenne prévue", f"{stats_f['mean']:.2f}")
            c2.metric("Production min prévue", f"{stats_f['min']:.2f}")
            c3.metric("Production max prévue", f"{stats_f['max']:.2f}")

            # plot forecast
            st.subheader("Graphique (Prévision)")
            fig2 = plot_matplotlib_timeseries(df_year_f["year"], df_year_f["yhat"],
                                            title=f"Prévision 2023→2040 — {sel_product_f if sel_product_f!='Tous les produits' else 'Tous produits'}",
                                            color="orange")
            st.pyplot(fig2)
            buf2 = fig_to_bytes(fig2)
            st.download_button("Télécharger le graphique prévision (PNG)", data=buf2, file_name="prevision.png", mime="image/png")

            # table
            st.subheader("Tableau des prévisions (années)")
            st.dataframe(df_year_f.rename(columns={"year":"date","yhat":"prediction"}).reset_index(drop=True))

            # export csv
            csv_f = df_year_f.rename(columns={"year":"date","yhat":"prediction"})
            csv_bytes_f = csv_f.to_csv(index=False).encode("utf-8")
            st.download_button("Télécharger prévisions (CSV)", data=csv_bytes_f, file_name="previsions_2023_2040.csv", mime="text/csv")

        # Numeric comparison: last historical vs first forecast (if product exists in both)
        st.markdown("---")
        st.subheader("Comparaison (numérique) : dernier historique vs première prévision")
        # compute
        if sel_product_f != "Tous les produits":
            hist_prod = df_hist[df_hist["product"]==sel_product_f]
            last_hist_row = hist_prod.sort_values("ds").tail(1)
            first_fore_row = df_fore[(df_fore["product"]==sel_product_f)].sort_values("ds").head(1)
            if not last_hist_row.empty and not first_fore_row.empty:
                last_val = float(last_hist_row["y"].values[0])
                first_val = float(first_fore_row["yhat"].values[0])
                diff = first_val - last_val
                pct = (diff / (last_val+1e-9))*100
                st.write(f"Produit: **{sel_product_f}**")
                st.write(f"- Dernière valeur historique ({last_hist_row['ds'].dt.year.values[0]}): **{last_val:.2f}**")
                st.write(f"- Première valeur prévue ({first_fore_row['ds'].dt.year.values[0]}): **{first_val:.2f}**")
                st.write(f"- Différence: **{diff:.2f}**  →  **{pct:.2f}%**")
            else:
                st.info("Pas de données historiques ou prévision disponibles pour ce produit pour la comparaison.")
        else:
            st.info("Sélectionne un produit spécifique pour la comparaison numérique.")

# -----------------------
# Footer
# -----------------------
st.sidebar.markdown("---")
st.sidebar.markdown("Data: `data.csv`, Prévisions: `previsions_futures_2040.csv`")
st.sidebar.markdown("Exécuter : `streamlit run app.py`")

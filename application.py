# app.py (corrigé & robuste)
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Dashboard Production", layout="wide")


# -----------------------
# Utilitaires
# -----------------------
def find_first_column(cols, candidates):
    """Retourne le premier nom de colonne (exact) trouvé parmi candidates (insensible à la casse)."""
    cols_l = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand.lower() in cols_l:
            return cols_l[cand.lower()]
    return None


@st.cache_data
def load_data(path_hist="data/dataclean.csv", path_fut="data/prediction_2040.csv"):
    """Charge et normalise les fichiers historiques et prévisions.
       Renomme les colonnes en 'Produit', 'Date', 'Valeur' pour uniformité."""
    # ---- Historiques
    try:
        df_hist = pd.read_csv(path_hist)
    except Exception as e:
        st.error(f"Impossible de charger le fichier historique '{path_hist}': {e}")
        return pd.DataFrame(columns=["Produit", "Date", "Valeur"]), pd.DataFrame(columns=["Produit", "Date", "Valeur"])

    # ---- Prévisions
    try:
        df_fut = pd.read_csv(path_fut)
    except Exception as e:
        st.error(f"Impossible de charger le fichier prévisions '{path_fut}': {e}")
        return pd.DataFrame(columns=["Produit", "Date", "Valeur"]), pd.DataFrame(columns=["Produit", "Date", "Valeur"])

    # Normalisation des colonnes (historiques)
    prod_col = find_first_column(df_hist.columns, ["product", "produit", "Produit", "Produit_name", "libelle"])
    date_col = find_first_column(df_hist.columns, ["ds", "date", "year", "Date", "YEAR"])
    val_col = find_first_column(df_hist.columns, ["y", "value", "production", "production_tonnes", "production_tonnes", "valeur", "tonnes"])

    if prod_col is None or date_col is None or val_col is None:
        st.warning("Fichier historique: impossible de détecter automatiquement 'product/date/value'. Vérifie les noms de colonnes.")
    else:
        df_hist = df_hist.rename(columns={prod_col: "Produit", date_col: "Date", val_col: "Valeur"})

    # Normalisation des colonnes (prévisions)
    prod_col = find_first_column(df_fut.columns, ["product", "produit", "Produit"])
    date_col = find_first_column(df_fut.columns, ["ds", "date", "Date", "year"])
    val_col = find_first_column(df_fut.columns, ["yhat", "prediction", "y", "valeur", "prediction_en_tonnes", "value", "valeur_prevue"])

    if prod_col is None or date_col is None or val_col is None:
        st.warning("Fichier prévisions: impossible de détecter automatiquement 'product/date/prediction'. Vérifie les noms de colonnes.")
    else:
        df_fut = df_fut.rename(columns={prod_col: "Produit", date_col: "Date", val_col: "Valeur"})

    # Convertir Date en datetime et Valeur en numérique, puis nettoyer
    def clean_df(df):
        if "Date" in df.columns:
            # tentative générale
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=False)
            # pour les années seulement (ex: '1986') — retenter si NaT
            mask = df["Date"].isna()
            if mask.any():
                try:
                    df.loc[mask, "Date"] = pd.to_datetime(df.loc[mask, "Date"].astype(str), format="%Y", errors="coerce")
                except Exception:
                    pass
        # Valeur -> numeric
        if "Valeur" in df.columns:
            df["Valeur"] = pd.to_numeric(df["Valeur"], errors="coerce")
        # Produit -> string
        if "Produit" in df.columns:
            df["Produit"] = df["Produit"].astype(str)
        # Drop lignes incomplètes
        keep_cols = [c for c in ["Produit", "Date", "Valeur"] if c in df.columns]
        df = df.dropna(subset=keep_cols)
        # Sort
        if "Produit" in df.columns and "Date" in df.columns:
            df = df.sort_values(["Produit", "Date"])
        return df.reset_index(drop=True)

    df_hist = clean_df(df_hist)
    df_fut = clean_df(df_fut)

    return df_hist, df_fut


def plot_timeseries(df, title, y_label, color):
    """Trace une série temporelle où df contient 'Date' (datetime) et 'Valeur' (num)."""
    fig, ax = plt.subplots(figsize=(10, 4))
    if df.empty:
        ax.text(0.5, 0.5, "Aucune donnée à afficher", ha="center", va="center")
    else:
        ax.plot(df["Date"], df["Valeur"], color=color, linewidth=2, marker="o")
    ax.set_title(title, fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel(y_label)
    ax.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    st.pyplot(fig)


def df_to_yearly(df):
    """Agrège par année et renvoie DataFrame avec colonnes ['Date','Valeur'] où Date = 1er janvier de l'année."""
    if df.empty:
        return pd.DataFrame(columns=["Date", "Valeur", "year"])
    tmp = df.copy()
    tmp["year"] = tmp["Date"].dt.year
    agg = tmp.groupby("year", as_index=False)["Valeur"].sum()
    agg["Date"] = pd.to_datetime(agg["year"].astype(str) + "-01-01")
    return agg[["Date", "Valeur", "year"]]


def fig_to_bytes(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return buf


# -----------------------
# Chargement des données
# -----------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller à", ["Accueil", "Historique", "Prévisions", "Analyse détaillée"])

with st.spinner("Chargement des données..."):
    df_hist, df_fut = load_data("data/dataclean.csv", "data/prediction_2040.csv")


# -----------------------
# PAGE: Accueil
# -----------------------
if page == "Accueil":
    st.title("Dashboard — Production & Prévisions")
    st.markdown(
        f"**Résumé** :\n\n- Données historiques : {len(df_hist)} lignes, {df_hist['Produit'].nunique() if 'Produit' in df_hist.columns else 0} produits.\n"
        f"- Prévisions (2023→2040) : {len(df_fut)} lignes, {df_fut['Produit'].nunique() if 'Produit' in df_fut.columns else 0} produits."
    )
    st.write("Utilise la barre latérale pour naviguer. Les colonnes détectées ont été renommées en `Produit`, `Date`, `Valeur`.")


# -----------------------
# PAGE: Historique
# -----------------------
if page == "Historique":
    st.header("Données historiques")
    if df_hist.empty:
        st.warning("Aucune donnée historique chargée (vérifie data/dataclean.csv).")
    else:
        produits = sorted(df_hist["Produit"].unique())
        produit_select = st.selectbox("Choisir un produit", ["Tous les produits"] + produits, index=1 if produits else 0)

        # Filtrage par produit
        if produit_select == "Tous les produits":
            df_prod = df_hist.copy()
        else:
            df_prod = df_hist[df_hist["Produit"] == produit_select].copy()

        if df_prod.empty:
            st.info("Aucune donnée pour ce produit.")
        else:
            # définir bornes de dates (date objects pour st.date_input)
            min_date = df_prod["Date"].min().date()
            max_date = df_prod["Date"].max().date()

            date_range = st.date_input(
                "Plage de dates (début, fin)",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            # date_input peut retourner une seule date si l'utilisateur choisit 1 valeur => forcer tuple
            if isinstance(date_range, tuple) or isinstance(date_range, list):
                start_dt, end_dt = date_range[0], date_range[1]
            else:
                start_dt = date_range
                end_dt = date_range

            # Filtrer selon plage
            df_filtered = df_prod[(df_prod["Date"].dt.date >= start_dt) & (df_prod["Date"].dt.date <= end_dt)].copy()

            # Statistiques
            st.subheader("Statistiques")
            if df_filtered.empty:
                st.info("Aucune donnée dans la plage sélectionnée.")
            else:
                mean_v = df_filtered["Valeur"].mean()
                min_v = df_filtered["Valeur"].min()
                max_v = df_filtered["Valeur"].max()
                # calc YoY moyen si au moins 2 années
                try:
                    yearly = df_to_yearly(df_filtered)
                    yoy = yearly["Valeur"].pct_change().dropna().mean() * 100
                except Exception:
                    yoy = np.nan

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Moyenne", f"{mean_v:.2f}")
                c2.metric("Min", f"{min_v:.2f}")
                c3.metric("Max", f"{max_v:.2f}")
                c4.metric("Croissance YoY moyenne", f"{yoy:.2f}%")

                # Graphique (annuel)
                st.subheader("Graphique (Historique - agrégé par année)")
                yearly = df_to_yearly(df_filtered)
                plot_timeseries(yearly, f"Historique — {produit_select}", "Production (annuelle)", "blue")

                # Téléchargements
                st.subheader("Données")
                st.dataframe(df_filtered.reset_index(drop=True))
                csv_bytes = df_filtered.to_csv(index=False).encode("utf-8")
                st.download_button("Télécharger données filtrées (CSV)", csv_bytes, file_name="historique_filtre.csv", mime="text/csv")


# -----------------------
# PAGE: Prévisions
# -----------------------
if page == "Prévisions":
    st.header("Prévisions futures (2023 → 2040)")
    if df_fut.empty:
        st.warning("Aucune donnée de prévision chargée (vérifie data/prediction_2040.csv).")
    else:
        produits_f = sorted(df_fut["Produit"].unique())
        sel_product_f = st.selectbox("Choisir un produit (prévision)", ["Tous les produits"] + produits_f, index=1 if produits_f else 0)

        if sel_product_f == "Tous les produits":
            df_pf = df_fut.copy()
        else:
            df_pf = df_fut[df_fut["Produit"] == sel_product_f].copy()

        if df_pf.empty:
            st.info("Aucune prévision disponible pour la sélection.")
        else:
            # Agrégation annuelle
            df_year_f = df_to_yearly(df_pf)

            st.subheader("Statistiques prévisionnelles")
            mean_f = df_year_f["Valeur"].mean() if not df_year_f.empty else np.nan
            min_f = df_year_f["Valeur"].min() if not df_year_f.empty else np.nan
            max_f = df_year_f["Valeur"].max() if not df_year_f.empty else np.nan
            c1, c2, c3 = st.columns(3)
            c1.metric("Production moyenne prévue", f"{mean_f:.2f}")
            c2.metric("Production min prévue", f"{min_f:.2f}")
            c3.metric("Production max prévue", f"{max_f:.2f}")

            st.subheader("Graphique (Prévision annuelle)")
            plot_timeseries(df_year_f, f"Prévision 2023→2040 — {sel_product_f}", "Production prévue (annuelle)", "orange")

            st.subheader("Tableau des prévisions (années)")
            st.dataframe(df_year_f[["year", "Valeur"]].rename(columns={"year": "Année", "Valeur": "Prédiction"}).reset_index(drop=True))

            csv_f = df_year_f[["year", "Valeur"]].rename(columns={"year":"Année","Valeur":"Prédiction"})
            st.download_button("Télécharger prévisions (CSV)", csv_f.to_csv(index=False).encode("utf-8"), file_name="previsions_2023_2040.csv", mime="text/csv")


# -----------------------
# PAGE: Analyse détaillée
# -----------------------
if page == "Analyse détaillée":
    st.header("Analyse détaillée — Historique vs Prévision (séparés)")
    products_common = sorted(list(set(df_hist["Produit"].unique()) & set(df_fut["Produit"].unique())))
    if not products_common:
        st.info("Aucun produit commun trouvé entre historique et prévisions.")
    else:
        prod_choice = st.selectbox("Produit (commun)", products_common)
        hist_p = df_hist[df_hist["Produit"] == prod_choice].copy()
        fut_p = df_fut[df_fut["Produit"] == prod_choice].copy()

        if hist_p.empty:
            st.info("Pas d'historique pour ce produit.")
        else:
            st.subheader("Historique (annuel)")
            hist_yearly = df_to_yearly(hist_p)
            plot_timeseries(hist_yearly, f"Historique — {prod_choice}", "Production (annuelle)", "blue")

        if fut_p.empty:
            st.info("Pas de prévisions pour ce produit.")
        else:
            st.subheader("Prévisions (annuel)")
            fut_yearly = df_to_yearly(fut_p)
            plot_timeseries(fut_yearly, f"Prévisions — {prod_choice}", "Production prévue (annuelle)", "orange")

        # Statistiques comparées
        st.subheader("Comparaison statistique")
        stats = {
            "Période": ["Historique", "Prévisions"],
            "Moyenne": [
                hist_p["Valeur"].mean() if not hist_p.empty else np.nan,
                fut_p["Valeur"].mean() if not fut_p.empty else np.nan,
            ],
            "Max": [
                hist_p["Valeur"].max() if not hist_p.empty else np.nan,
                fut_p["Valeur"].max() if not fut_p.empty else np.nan,
            ],
            "Min": [
                hist_p["Valeur"].min() if not hist_p.empty else np.nan,
                fut_p["Valeur"].min() if not fut_p.empty else np.nan,
            ],
        }
        stats_df = pd.DataFrame(stats)
        st.dataframe(stats_df)
        st.download_button("Télécharger comparaison (CSV)", stats_df.to_csv(index=False).encode("utf-8"), file_name="comparaison_stats.csv", mime="text/csv")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Data: `data/dataclean.csv`, Prévisions: `data/prediction_2040.csv`")
st.sidebar.markdown("Exécuter : `streamlit run app.py`")

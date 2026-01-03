# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64

from utils.data_loader import load_historical, load_forecast, get_stats_series
from utils.plots import plot_matplotlib_timeseries, fig_to_bytes

st.set_page_config(page_title="Dashboard Production", layout="wide")


st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller à", ["Accueil", "Historique", "Prévisions"])

with st.spinner("Chargement des données..."):
    df_hist = load_historical("data/data.csv")
    df_fore = load_forecast("data/prevision_2040.csv")


if page == "Accueil":
    st.title("Dashboard — Production & Prévisions")
    st.markdown("""
    **Résumé** :
    - Données historiques : {} lignes, {} produits.  
    - Prévisions (2023→2040) : {} lignes, {} produits.
    """.format(len(df_hist), df_hist["product"].nunique(), len(df_fore), df_fore["product"].nunique()))
    st.write("Sélectionnez une page dans la barre latérale pour visualiser les données historiques ou les prévisions futures.")
    st.markdown("**Fonctionnalités** : filtres par produit, export CSV, téléchargements d'images (matplotlib).")

if page == "Historique":
    st.header("Données historiques")
    if df_hist.empty:
        st.warning("Aucune donnée historique chargée (vérifie data.csv).")
    else:
        produits = sorted(df_hist["product"].unique())
        sel_product = st.selectbox("Choisir un produit", ["Tous les produits"] + produits, index=1 if len(produits)>0 else 0)
        min_year = int(df_hist["ds"].dt.year.min())
        max_year = int(df_hist["ds"].dt.year.max())
        year_range = st.slider("Plage d'années", min_year, max_year, (min_year, max_year))

        df_filtered = df_hist.copy()
        if sel_product != "Tous les produits":
            df_filtered = df_filtered[df_filtered["product"]==sel_product]
        df_filtered = df_filtered[(df_filtered["ds"].dt.year>=year_range[0]) & (df_filtered["ds"].dt.year<=year_range[1])]

        st.subheader("Statistiques")
        if df_filtered.empty:
            st.info("Aucune donnée pour la sélection.")
        else:
            stats = get_stats_series(df_filtered["y"].values)
            c1,c2,c3 = st.columns(3)
            c1.metric("Moyenne", f"{stats['mean']:.2f}")
            c2.metric("Min", f"{stats['min']:.2f}")
            c3.metric("Max", f"{stats['max']:.2f}")

            st.subheader("Graphique (Historique)")
            df_plot = df_filtered.copy()
            df_plot["year"] = df_plot["ds"].dt.year
            df_year = df_plot.groupby("year", as_index=False)["y"].sum()
            fig = plot_matplotlib_timeseries(df_year["year"], df_year["y"],
                                            title=f"Historique — {sel_product if sel_product!='Tous les produits' else 'Tous produits'}",
                                            color="blue")
            st.pyplot(fig)

            buf = fig_to_bytes(fig)
            st.download_button("Télécharger le graphique (PNG)", data=buf, file_name="historique.png", mime="image/png")

            st.subheader("Tableau")
            st.dataframe(df_filtered.sort_values("ds").reset_index(drop=True))

            csv_bytes = df_filtered.to_csv(index=False).encode("utf-8")
            st.download_button("Télécharger données filtrées (CSV)", data=csv_bytes, file_name="historique_filtre.csv", mime="text/csv")


if page == "Prévisions":
    st.header("Prévisions futures (2023 → 2040)")
    if df_fore.empty:
        st.warning("Aucune donnée de prévision chargée (vérifie previsions_futures_2040.csv).")
    else:
        produits_f = sorted(df_fore["product"].unique())
        sel_product_f = st.selectbox("Choisir un produit (prévision)", ["Tous les produits"] + produits_f, index=1 if len(produits_f)>0 else 0)

        dff = df_fore.copy()
        if sel_product_f != "Tous les produits":
            dff = dff[dff["product"]==sel_product_f]
        df_year_f = dff.groupby(dff:=dff["ds"].dt.year).agg({"yhat":"sum"}).reset_index().rename(columns={dff.name:"year"})

        st.subheader("Statistiques prévisionnelles")
        if df_year_f.empty:
            st.info("Aucune prévision pour la sélection.")
        else:
            stats_f = get_stats_series(df_year_f["yhat"].values)
            c1,c2,c3 = st.columns(3)
            c1.metric("Production moyenne prévue", f"{stats_f['mean']:.2f}")
            c2.metric("Production min prévue", f"{stats_f['min']:.2f}")
            c3.metric("Production max prévue", f"{stats_f['max']:.2f}")

            st.subheader("Graphique (Prévision)")
            fig2 = plot_matplotlib_timeseries(df_year_f["year"], df_year_f["yhat"],
                                            title=f"Prévision 2023→2040 — {sel_product_f if sel_product_f!='Tous les produits' else 'Tous produits'}",
                                            color="orange")
            st.pyplot(fig2)
            buf2 = fig_to_bytes(fig2)
            st.download_button("Télécharger le graphique prévision (PNG)", data=buf2, file_name="prevision.png", mime="image/png")

            st.subheader("Tableau des prévisions (années)")
            st.dataframe(df_year_f.rename(columns={"year":"date","yhat":"prediction"}).reset_index(drop=True))

            csv_f = df_year_f.rename(columns={"year":"date","yhat":"prediction"})
            csv_bytes_f = csv_f.to_csv(index=False).encode("utf-8")
            st.download_button("Télécharger prévisions (CSV)", data=csv_bytes_f, file_name="previsions_2023_2040.csv", mime="text/csv")

        st.markdown("---")
        st.subheader("Comparaison (numérique) : dernier historique vs première prévision")
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

st.sidebar.markdown("---")

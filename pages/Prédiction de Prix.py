# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 09:26:15 2025

@author: meedz
"""

import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.compose import ColumnTransformer
import numpy as np
from datetime import date
##########################################################################3
st.set_page_config(page_title="Prédiction de Prix des Produits", layout="centered", page_icon="data:image/svg+xml,%3csvg stroke-width='1.75' id='Layer_1' data-name='Layer 1' xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3e%3cdefs%3e%3cstyle%3e.cls-n1wrucdvdcsstajotcwn1-1%7bfill:none%3bstroke:%23FC0F0F%3bstroke-miterlimit:10%3b%3b%7d%3c/style%3e%3c/defs%3e%3cpolyline class='cls-n1wrucdvdcsstajotcwn1-1' points='7.23 6.27 1.5 12 7.23 17.73'/%3e%3cpolyline class='cls-n1wrucdvdcsstajotcwn1-1' points='16.77 17.73 22.5 12 16.77 6.27'/%3e%3cline class='cls-n1wrucdvdcsstajotcwn1-1' x1='11.05' y1='12' x2='12.95' y2='12'/%3e%3cline class='cls-n1wrucdvdcsstajotcwn1-1' x1='15.82' y1='12' x2='17.73' y2='12'/%3e%3cline class='cls-n1wrucdvdcsstajotcwn1-1' x1='6.27' y1='12' x2='8.18' y2='12'/%3e%3c/svg%3e")

st.title("📊 Prédiction du Prix des Produits")
st.write("Cette application permet de prédire le prix des produits selon la ville, le produit et la date.")

# ----------------- Chargement du modèle -----------------



@st.cache_data  
def load_data(url):
    df = pd.read_csv(url)
    return df

df = load_data("data/dataset.csv")

df['Date'] = pd.to_datetime(df['Date'])
df['month'] = df['Date'].dt.month
df['year'] = df['Date'].dt.year
df['day'] = df['Date'].dt.day
df = df.drop(columns=['Date'])

Q1 = df["Prix"].quantile(0.25)
Q3 = df["Prix"].quantile(0.75)
IQR = Q3 - Q1
df = df[(df["Prix"] >= (Q1 -1.5 * IQR)) & (df["Prix"] <= (Q1 + 1.5 * IQR))]

x = df.drop('Prix', axis=1)
y = df['Prix']
cat_cols = ['Produits', 'Villes']
num_cols = ['month', 'year', 'day']
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
num_pip = Pipeline(steps = [
    ('scaler', MinMaxScaler())
])

cat_pip = Pipeline(steps = [
    ('encoder', OneHotEncoder())
])
col_trans = ColumnTransformer(transformers = [
    ('num_pipe', num_pip, num_cols),
    ('cat_pipe', cat_pip, cat_cols),
])


pipe_rf = Pipeline(steps=[
    ('preprocessor', col_trans),
    ('regressor', RandomForestRegressor(        
        n_jobs=-1,
        random_state=42,
        warm_start=True,
        bootstrap = True,
        max_depth = 500,
        oob_score = True,
    ))
])

pipe_rf.fit(x_train, y_train)

model = pipe_rf

# ----------------- Interface Utilisateur -----------------

villes = df['Villes'].unique().tolist()
produits = df['Produits'].unique().tolist()


ville = st.selectbox("Choisissez la ville :", villes)
produit = st.selectbox("Choisissez le produit :", produits)
date = st.date_input("Choisissez la date :",   
          value=pd.to_datetime("2024-01-01"),
          min_value=pd.to_datetime("2017-01-01"),
          max_value=pd.to_datetime("2050-12-31")
          )

##################################################################
if st.button("Prédire le prix"):
    input_df = pd.DataFrame({
    "Villes": [ville],
    "Produits": [produit],
    "Date": [pd.to_datetime(date)]
})
    
    
    input_df['year'] = input_df['Date'].dt.year
    input_df['month'] = input_df['Date'].dt.month
    input_df['day'] = input_df['Date'].dt.day
    
    
    input_df = input_df.drop(columns=['Date'])
    
    
    
    
    prix_pred = model.predict(input_df)[0]
    
    # Résultat
    st.success(f"💰 Le prix prédit pour **{produit}** à **{ville}** le **{date}** est : **{prix_pred:.2f}** MAD")

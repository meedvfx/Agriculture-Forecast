import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.compose import ColumnTransformer
import numpy as np
from datetime import date


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

import pickle

with open(r"C:\users\meedz\desktop\stage\site\modele\model.pkl", "wb") as f:
    pickle.dump(pipe_rf, f)

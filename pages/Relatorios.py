import streamlit as st
from pymongo import MongoClient
import os
import pandas as pd
import plotly.express as px

# --- Conexão ao MongoDB ---


def connect_to_mongo():
    uri = os.environ.get(
        "MONGO_URI",
        "mongodb+srv://emiliods79:uD5A2J4o38dpk0hX@cluster0.ufpae.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    )
    client = MongoClient(uri)
    db = client['pibit_app']
    return db


db = connect_to_mongo()
animais_col = db['animais']
amostras_col = db['amostras']
exames_col = db['exames']
reagentes_col = db['reagentes']

st.title("Relatórios e Estatísticas do Sistema")

# --- Coleta de Dados ---
animais = list(animais_col.find())
amostras = list(amostras_col.find())
exames = list(exames_col.find())
reagentes = list(reagentes_col.find())

# --- KPIs ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Animais cadastrados", len(animais))
col2.metric("Amostras cadastradas", len(amostras))
col3.metric("Exames cadastrados", len(exames))
col4.metric("Reagentes cadastrados", len(reagentes))

st.markdown("---")

# --- Gráfico: Animais por Sexo ---
df_animais = pd.DataFrame(animais)
if not df_animais.empty and "sexo" in df_animais.columns:
    fig = px.histogram(df_animais, x="sexo",
                       title="Distribuição dos Animais por Sexo")
    st.plotly_chart(fig, use_container_width=True)

# --- Gráfico: Amostras por Método de Coleta ---
df_amostras = pd.DataFrame(amostras)
if not df_amostras.empty and "metodo_coleta" in df_amostras.columns:
    fig2 = px.histogram(df_amostras, x="metodo_coleta",
                        title="Amostras por Método de Coleta")
    st.plotly_chart(fig2, use_container_width=True)

# --- Gráfico: Exames por Tipo ---
df_exames = pd.DataFrame(exames)
if not df_exames.empty and "tipo_exame" in df_exames.columns:
    fig3 = px.histogram(df_exames, x="tipo_exame", title="Exames por Tipo")
    st.plotly_chart(fig3, use_container_width=True)

# --- Gráfico: Reagentes por Tipo ---
df_reagentes = pd.DataFrame(reagentes)
if not df_reagentes.empty and "tipo" in df_reagentes.columns:
    fig4 = px.histogram(df_reagentes, x="tipo", title="Reagentes por Tipo")
    st.plotly_chart(fig4, use_container_width=True)

# --- Tabelas detalhadas (opcional) ---
with st.expander("Ver tabelas detalhadas"):
    st.subheader("Animais")
    st.dataframe(df_animais)
    st.subheader("Amostras")
    st.dataframe(df_amostras)
    st.subheader("Exames")
    st.dataframe(df_exames)
    st.subheader("Reagentes")
    st.dataframe(df_reagentes)

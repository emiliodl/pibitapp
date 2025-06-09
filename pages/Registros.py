import streamlit as st
from pymongo import MongoClient
import pandas as pd
import altair as alt
import os
from bson import ObjectId


# Conexão ao MongoDB Atlas
def connect_to_mongo():
    uri = ("mongodb+srv://emiliods79:uD5A2J4o38dpk0hX@cluster0.ufpae.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    client = MongoClient(uri)
    db = client['pibit_app']  # Ou já especificado na URI, se preferir.
    return db

# Função auxiliar para converter ObjectIds recursivamente
def convert_objectid_to_str(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectid_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(elem) for elem in obj]
    else:
        return obj

# Função para buscar amostras do banco de dados
def fetch_samples():
    db = connect_to_mongo()
    collection = db['amostras']
    samples = list(collection.find())
    
    # Aplica a conversão recursiva para cada amostra
    processed_samples = [convert_objectid_to_str(sample) for sample in samples]
    return processed_samples

# Função para buscar reagentes do banco de dados
def fetch_reagents():
    db = connect_to_mongo()
    collection = db['reagentes']
    reagents = list(collection.find())
    
    # Aplica a conversão recursiva para cada reagente
    processed_reagents = [convert_objectid_to_str(reagent) for reagent in reagents]
    return processed_reagents

# Função para filtrar pelo nome do animal
def filter_by_animal_name(df, column_name='Nome comum'):
    pesquisa = st.sidebar.text_input("Pesquisar pelo nome do animal:")
    if pesquisa:
        # Garante que a coluna é string para usar contains
        df = df[df[column_name].astype(str).str.contains(pesquisa, case=False, na=False)]
    return df

# Injetar CSS customizado para ajustar o container do multiselect (se necessário)
st.markdown(
    """
    <style>
    /* Ajusta o container do multiselect para ter altura máxima e scroll vertical */
    div[data-baseweb="select"] > div {
        max-height: 150px;
        overflow-y: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Página principal
st.title("Amostras e Reagentes")

# Cria abas para 'Registros', 'Relatório' e 'Reagentes'
tabs = st.tabs(["Registros", "Relatório", "Reagentes"])

# Aba Amostras - Registros e Relatório
with tabs[0]:
    st.header("Lista de Registros - Amostras")
    samples = fetch_samples()
    if samples:
        df_samples = pd.DataFrame(samples)
    else:
        st.info("Nenhuma amostra registrada ainda.")
        st.stop()
    
    # --- Filtros na sidebar ---
    st.sidebar.header("Filtros para Amostras")
    
    # Filtro por Data de coleta (se existir a coluna)
    if 'Data de coleta' in df_samples.columns:
        df_samples['Data de coleta'] = pd.to_datetime(df_samples['Data de coleta'], errors='coerce')
        # Remove linhas com 'NaT' (Not a Time) após a conversão, se necessário
        df_samples.dropna(subset=['Data de coleta'], inplace=True) 

        if not df_samples['Data de coleta'].empty: # Verifica se ainda há datas válidas
            data_min = df_samples['Data de coleta'].min()
            data_max = df_samples['Data de coleta'].max()
            data_selecionada = st.sidebar.date_input("Selecione o intervalo de datas:",
                                                     value=(data_min, data_max))
            if isinstance(data_selecionada, tuple) and len(data_selecionada) == 2:
                inicio, fim = data_selecionada
                df_samples = df_samples[(df_samples['Data de coleta'] >= pd.to_datetime(inicio)) & 
                                        (df_samples['Data de coleta'] <= pd.to_datetime(fim))]
        else:
            st.sidebar.warning("Nenhuma data de coleta válida encontrada para filtrar.")

    # Filtro pelo Nome do animal (se existir)
    if 'Nome comum' in df_samples.columns:
        df_samples = filter_by_animal_name(df_samples, 'Nome comum')
    
    # Exibe a tabela filtrada
    st.dataframe(df_samples, use_container_width=True)
    
    # Opção para exportar como CSV
    csv_samples = df_samples.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Baixar Amostras como CSV",
        data=csv_samples,
        file_name="amostras_registradas.csv",
        mime="text/csv"
    )

with tabs[1]:
    st.header("Relatório de Amostras")
    
    # Exemplo de gráfico: distribuição das espécies ou Nome do animal
    if 'Nome comum' in df_samples.columns:
        # Cria uma contagem por nome do animal
        especies = df_samples['Nome comum'].value_counts().reset_index()
        especies.columns = ['Nome comum', 'Quantidade']
        
        # Gráfico de barras usando Altair
        grafico = alt.Chart(especies).mark_bar().encode(
            x=alt.X("Nome comum:N", sort='-y', title="Nome comum"),
            y=alt.Y("Quantidade:Q", title="Quantidade"),
            tooltip=["Nome comum", "Quantidade"]
        ).properties(
            width=600,
            height=400,
            title="Distribuição de Espécies"
        )
        st.altair_chart(grafico, use_container_width=True)
    else:
        st.info("Coluna 'Nome do animal' não encontrada para gerar o relatório.")

# Aba Reagentes
with tabs[2]:
    st.header("Reagentes")
    reagents = fetch_reagents()
    if reagents:
        df_reagents = pd.DataFrame(reagents)
        st.dataframe(df_reagents, use_container_width=True)
        
        # Opção para exportar como CSV
        csv_reagents = df_reagents.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar Reagentes como CSV",
            data=csv_reagents,
            file_name="reagentes_registrados.csv",
            mime="text/csv"
        )
    else:
        st.info("Nenhum reagente registrado ainda.")
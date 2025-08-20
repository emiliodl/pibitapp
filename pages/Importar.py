import streamlit as st
from pymongo import MongoClient
import datetime
import os
import pandas as pd

# Conexão ao MongoDB (usando variável de ambiente)


def connect_to_mongo():
    uri = os.environ.get(
        "MONGO_URI",
        "mongodb+srv://emiliods79:uD5A2J4o38dpk0hX@cluster0.ufpae.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    )
    client = MongoClient(uri)
    db = client['pibit_app']
    return db


db = connect_to_mongo()

st.title("Importação de Dados para MongoDB")

# Seleção do tipo de planilha para definir a coleção
tipo_planilha = st.radio(
    "Selecione o tipo de planilha a ser importada:",
    options=["Animais", "Amostras", "Exames", "Reagentes"]
)

colecao_map = {
    "Animais": "animais",
    "Amostras": "amostras",
    "Exames": "exames",
    "Reagentes": "reagentes"
}
collection = db[colecao_map[tipo_planilha]]

# Upload do arquivo
uploaded_file = st.file_uploader(
    "Selecione uma planilha (CSV ou Excel)",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:
    try:
        # Leitura com pandas
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Padronização dos nomes das colunas para minúsculas e sem espaços
        df.columns = [col.strip().lower().replace(" ", "_")
                      for col in df.columns]

        # Renomeie para os nomes usados no sistema, se necessário
        renomear = {}
        if tipo_planilha == "Amostras":
            renomear = {
                "data_de_coleta": "data_coleta",
                "local_de_coleta": "local_coleta",
                "tipo_de_amostra": "metodo_coleta",
                "condicao": "condicao_amostra",
                "destino": "destino_amostra",
                "resultado_do_exame": "resultado_exame",
                "observacoes_da_amostra": "observacoes",
            }
        elif tipo_planilha == "Animais":
            renomear = {
                "nome_comum": "nome_comum",
                "nome_cientifico": "nome_cientifico",
                "sexo": "sexo",
                "peso": "peso",
                "hvu": "hvu",
                "microchip": "microchip",
                "orgao": "orgao",
                "status": "status",
                "funcao": "funcao",
                "local_origem": "local_origem",
                "data_nascimento": "data_nascimento",
                "observacoes": "observacoes",
            }
        elif tipo_planilha == "Exames":
            renomear = {
                "amostra_id": "amostra_id",
                "tipo_de_exame": "tipo_exame",
                "laboratorio_realizador": "laboratorio_realizador",
                "data_de_realizacao": "data_realizacao",
                "resultado_detalhado": "resultado_detalhado",
                "responsavel_exame": "responsavel_exame",
                "observacoes_do_exame": "observacoes_exame",
            }
        elif tipo_planilha == "Reagentes":
            renomear = {
                'id': '_id',
                "nome_do_reagente": "nome",
                "fabricante": "fabricante",
                "numero_do_lote": "numero_lote",
                "data_de_validade": "data_validade",
                "quantidade": "quantidade",
                "unidade": "unidade",
                "local_de_armazenamento": "local_armazenamento",
                "observacoes_do_reagente": "observacoes",
            }
        df.rename(columns=renomear, inplace=True)


        # Converter hora para string, se existir
        if 'hora' in df.columns:
            df['hora'] = df['hora'].apply(
                lambda x: x.isoformat() if isinstance(x, datetime.time) else str(x)
            )

        st.subheader("Visualização dos Dados")
        st.dataframe(df.head())

        if st.button("Importar dados"):
            # Remove campos vazios de cada registro
            dados = [
                {k: v for k, v in row.items() if pd.notnull(v) and v != ""}
                for row in df.to_dict(orient="records")
            ]
            resultado = collection.insert_many(dados)
            st.success(
                f"Foram inseridos {len(resultado.inserted_ids)} documentos na coleção '{collection.name}'!"
            )

    except Exception as e:
        st.error(f"Ocorreu um erro ao importar os dados: {e}")

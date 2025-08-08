import streamlit as st
from pymongo import MongoClient
import os

def connect_to_mongo():
    uri = ("mongodb+srv://emiliods79:uD5A2J4o38dpk0hX@cluster0.ufpae.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    client = MongoClient(uri)
    db = client['pibit_app']  
    return db

animais_col = connect_to_mongo()['animais']
amostras_col = connect_to_mongo()['amostras']
def carregar_animais_mongo():
    return list(animais_col.find())
def carregar_amostras_mongo():
    return list(amostras_col.find())

st.title("Animais Registrados")

animais = carregar_animais_mongo()

if not animais:
    st.info("Nenhum animal cadastrado no banco de dados.")
else:
    for animal in animais:
        with st.expander(f"{animal.get('nome_comum', 'Sem nome comum')} ({animal.get('nome_cientifico', 'Sem nome científico')})"):
            st.markdown(f"**ID:** {animal.get('_id', 'Sem ID')}")
            st.markdown(f"**Sexo:** {animal.get('sexo', 'Não informado')}")
            st.markdown(f"**Peso (kg):** {animal.get('peso', 'Não informado')}")
            st.markdown(f"**ID HVU:** {animal.get('hvu', animal.get('animal_hvu', 'Não informado'))}")
            st.markdown(f"**Microchip:** {animal.get('microchip', 'Não informado')}")
            st.markdown(f"**Órgão responsável:** {animal.get('orgao', animal.get('animal_orgao', 'Não informado'))}")
            st.markdown(f"**Status:** {animal.get('status', 'Não informado')}")
            st.markdown(f"**Função:** {animal.get('funcao', 'Não informado')}")
            st.markdown(f"**Local de Origem:** {animal.get('local_origem', 'Não informado')}")
            st.markdown(f"**Data de Nascimento:** {animal.get('data_nascimento', 'Não informado')}")
            st.markdown(f"**Observações:** {animal.get('observacoes', 'Nenhuma')}")

            st.write("---")
            st.subheader("Amostras Coletadas:")
            amostras = amostras_col.find({"animal_id": animal['_id']})
            if amostras:
                for amostra in amostras:
                    id = amostra.get('_id', 'Sem ID')
                    local_coleta = amostra.get('local_coleta', 'Sem local de coleta')
                    data_coleta = amostra.get('data_coleta', 'Sem data de coleta')
                    tipo = amostra.get("tipo", "Sem tipo")
                    data = amostra.get("data", "Sem data")
                    st.write(f"- Tipo: {tipo}, Data: {data}")
            else:
                st.info("Nenhuma amostra para este animal ainda.")
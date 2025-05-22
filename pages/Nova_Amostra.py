import streamlit as st
from pymongo import MongoClient
import os

# Conexão ao MongoDB
def connect_to_mongo():
    uri = ("mongodb+srv://emiliods79:uD5A2J4o38dpk0hX@cluster0.ufpae.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    client = MongoClient(uri)
    db = client['pibit_app']  # Ou já especificado na URI, se preferir.
    return db
# Função para buscar sugestões do MongoDB
db = connect_to_mongo()
collection = db['amostras']

# Verificação de login
if not st.session_state.get("LOGGED_IN"):
    st.warning("Você precisa fazer login para acessar esta página.")
    st.stop()

st.title("Registrar Nova Amostra")

with st.form("form_registro_amostra"):
    # --- Novo! ID controlado pelo usuário ---
    id_input = st.text_input(
        "ID da Amostra (único)", 
        placeholder="Digite um ID alfanumérico único"
    )
    id_hvu = st.text_input("Id do hvu")
    microchip = st.text_input("Microchip")
    especie_input = st.text_input("Espécie (Nome Científico)")
    origem = st.text_input("Origem (Orgão responsável)")
    nome_comum_input = st.text_input("Nome Comum")
    local_coleta = st.text_input("Local de Coleta")
    data_coleta = st.date_input("Data da Coleta")
    nome_coletor = st.text_input("Nome do Coletor")
    metodo_coleta = st.selectbox(
        "Método de Coleta",
        ["Swab nasal", "Swab oral", "Swab cloacal", "Sangue", "Necrópsia"]
    )
    condicao_amostra = st.selectbox(
        "Condição da Amostra",
        ["Temperatura ambiente", "Refrigerada", "Sem identificação", "Coagulada"]
    )
    destino_amostra = st.text_input("Destino da Amostra")
    sexo = st.selectbox("Sexo do Animal:", ["", "Macho", "Fêmea", "Desconhecido"])
    status = st.selectbox("Status do Animal:", ["", "Vivo", "Morto", "Desconhecido"])
    peso = st.number_input("Peso (kg):", min_value=0.0, format="%.2f", step=0.01)
    funcao = st.text_input("Função do Animal (opcional)")
    latitude = st.text_input("Latitude")
    longitude = st.text_input("Longitude")
    resultado_exame = st.text_input("Resultado do Exame (opcional)")
    observacoes = st.text_area("Observações (opcional)")

    submit = st.form_submit_button("Registrar Amostra")

if submit:
    # Valida ID informado
    if not id_input:
        st.error("Você deve informar um ID único para a amostra.")
    elif collection.find_one({"_id": id_input}):
        st.error(f"Já existe uma amostra com _id = '{id_input}'. Escolha outro.")
    else:
        # Monta o dicionário incluindo o _id fornecido
        sample_data = {
            "_id": id_input,
            "id hvu": id_hvu,
            "microchip": microchip,
            'origem': origem,
            "especie": especie_input,
            "nome comum": nome_comum_input,
            "local_coleta": local_coleta,
            "data_coleta": str(data_coleta),
            "nome_coletor": nome_coletor,
            "metodo_coleta": metodo_coleta,
            "condicao_amostra": condicao_amostra,
            "destino_amostra": destino_amostra,
            "sexo": sexo,
            "status": status,
            "peso": peso,
            "funcao": funcao,
            "latitude": latitude,
            "longitude": longitude,
            "resultado_exame": resultado_exame,
            "observacoes": observacoes
        }
        # Remove campos vazios
        sample_data = {k: v for k, v in sample_data.items() if v not in (None, "", [])}
        try:
            collection.insert_one(sample_data)
            st.success(f"Amostra registrada com _id = '{id_input}' com sucesso!")
        except Exception as e:
            st.error(f"Erro ao registrar a amostra: {e}")
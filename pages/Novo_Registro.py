import streamlit as st
from pymongo import MongoClient
import os
import pandas as pd
from datetime import date  # Para usar date.today() como valor padrão

# --- Configurações Iniciais ---
st.set_page_config(layout="wide")  # Define o layout da página como amplo

# --- Conexão ao MongoDB ---


def connect_to_mongo():
    uri = os.environ.get(
        'MONGO_URI', "mongodb+srv://emiliods79:uD5A2J4o38dpk0hX@cluster0.ufpae.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    client = MongoClient(uri)
    db = client['pibit_app']
    return db


def add_document(collection_name, doc_data):
    db = connect_to_mongo()
    collection = db[collection_name]

    # Verifica se o _id já existe antes de inserir
    if "_id" in doc_data and collection.find_one({"_id": doc_data["_id"]}):
        return False, f"Erro: Já existe um registro com o ID '{doc_data['_id']}' na coleção '{collection_name}'."

    try:
        collection.insert_one(doc_data)
        return True, f"Registro com ID '{doc_data.get('_id', 'N/A')}' adicionado com sucesso na coleção '{collection_name}'!"
    except Exception as e:
        return False, f"Erro ao adicionar registro na coleção '{collection_name}': {e}"


# --- Verificação de Login (Mantida) ---
if not st.session_state.get("LOGGED_IN"):
    st.warning("Você precisa fazer login para acessar esta página.")
    st.stop()

# --- Título Principal ---
st.title("Novo Registro no Sistema")
st.write("Escolha o tipo de registro que deseja adicionar:")

# --- Abas para Registro ---
tab_animal, tab_amostra, tab_exame, tab_reagente = st.tabs([
    "Registrar Animal",
    "Registrar Amostra",
    "Registrar Exame",
    "Registrar Reagente"
])

# --- Aba: Registrar Animal ---
with tab_animal:
    st.header("Registrar Novo Animal")
    with st.form("form_registro_animal"):
        st.markdown("**Informações do Animal**")
        animal_id_input = st.text_input(
            "ID do Animal (único)", placeholder="Ex: ANM001")
        animal_nome_comum = st.text_input("Nome Comum")
        animal_nome_cientifico = st.text_input("Nome Científico")
        animal_sexo = st.selectbox(
            "Sexo", ["", "Macho", "Fêmea", "Desconhecido"])
        animal_peso = st.number_input(
            "Peso (kg)", min_value=0.0, format="%.2f", step=0.01)
        animal_hvu = st.text_input(
            "ID do HVU (Hospital Veterinário Universitário)")
        animal_microchip = st.text_input("Microchip")
        animal_orgao = st.text_input("Origem (Órgão responsável)")
        animal_status = st.text_input("Status")
        animal_funcao = st.text_input("Função (opcional)")
        animal_local_origem = st.text_input("Local de Origem")
        animal_idade = st.text_input("Idade (opcional)")
        animal_faixa_etaria = st.selectbox(
            'Faixa Etária (opcional)', ["Filhote", "Suvenil",' Sub Adulto', "Adulto", "Senil"]
        )
        animal_observacoes = st.text_area("Observações (opcional)")
        animal_classe = st.selectbox(
            'Classe', ["Ave", "Mamífero", "Répteis",' Anfíbios', "Peixes"]
        )
        submit_animal = st.form_submit_button("Registrar Animal")

        if submit_animal:
            if not animal_id_input:
                st.error("Por favor, insira um ID único para o animal.")
            else:
                animal_data = {
                    "_id": animal_id_input,  # Usa o ID fornecido pelo usuário
                    "nome_comum": animal_nome_comum,
                    "nome_cientifico": animal_nome_cientifico,
                    "sexo": animal_sexo,
                    "peso": animal_peso,
                    "status": animal_status,
                    "funcao": animal_funcao,
                    "local_origem": animal_local_origem,
                    "hvu": animal_hvu,
                    "microchip": animal_microchip,
                    "orgao": animal_orgao,
                    "idade": animal_idade,
                    'faixa_etaria': animal_faixa_etaria,
                    "observacoes": animal_observacoes
                }
                # Remove campos vazios ou nulos antes de inserir
                animal_data = {
                    k: v for k, v in animal_data.items() if v not in (None, "", [])}

                success, message = add_document('animais', animal_data)
                if success:
                    st.success(message)
                else:
                    st.error(message)

# --- Aba: Registrar Amostra ---
with tab_amostra:
    st.header("Registrar Nova Amostra")
    with st.form("form_registro_amostra"):
        st.markdown("**Informações da Amostra**")
        amostra_id_input = st.text_input(
            "ID da Amostra (único)", placeholder="Ex: AMS001")

        # Opcional: dropdown com animais existentes para vincular a amostra
        db = connect_to_mongo()
        animais_collection = db['animais']
        # Buscar apenas o _id e nome_comum
        animais_existentes = list(animais_collection.find(
            {}, {"_id": 1, "nome_comum": 1}))

        animal_options = [
            ""] + [f"{animal.get('nome_comum', 'Animal sem nome')} (ID: {animal['_id']})" for animal in animais_existentes]
        selected_animal_str = st.selectbox(
            "Vincular a qual Animal?", options=animal_options)

        # Extrair o ID do animal selecionado
        linked_animal_id = None
        if selected_animal_str and " (ID: " in selected_animal_str:
            linked_animal_id = selected_animal_str.split(
                " (ID: ")[1][:-1]  # Extrai o ID entre " (ID: " e ")"
        amostra_local_coleta = st.text_input("Local de Coleta da Amostra")
        amostra_data_coleta = st.date_input(
            "Data da Coleta da Amostra", value=date.today())
        amostra_nome_coletor = st.text_input("Nome do Coletor")
        amostra_metodo_coleta = st.selectbox(
            "Método de Coleta",
            ["", "Swab nasal", "Swab oral", "Swab cloacal", "Sangue", "Necrópsia"]
        )
        amostra_condicao = st.selectbox(
            "Condição da Amostra",
            ["", "Temperatura ambiente", "Refrigerada", "Congelada",
                "Sem identificação", "Coagulada", "Hemolisada"]
        )
        amostra_destino = st.text_input(
            "Destino da Amostra (e.g., Laboratório X, Biobanco)")
        amostra_latitude = st.text_input("Latitude (opcional)")
        amostra_kit = st.text_input("Kit utilizado (opcional)")
        amostra_longitude = st.text_input("Longitude (opcional)")
        amostra_resultado_exame = st.text_input(
            "Resultado do Exame (inicial, opcional)")
        amostra_observacoes = st.text_area("Observações (opcional)")
        amostra_caixa = st.text_input("Caixa de amarzenamento/Freezer (opcional)")
        amostra_disponibilidade = st.checkbox("Sangue disponível para uso?")
        amostra_dna = st.checkbox("DNA disponível para uso?")
        amostra_rna = st.checkbox("RNA disponível para uso?")
        amostra_sequenciamento = st.selectbox(
            "Sequenciamento realizado?", ["", "Sim", "Não"]
        )

        submit_amostra = st.form_submit_button("Registrar Amostra")

        if submit_amostra:
            if not amostra_id_input:
                st.error("Por favor, insira um ID único para a amostra.")
            elif not linked_animal_id:
                st.error(
                    "Por favor, selecione um animal para vincular esta amostra.")
            else:
                amostra_data = {
                    "_id": amostra_id_input,
                    "animal_id": linked_animal_id,
                    "local_coleta_amostra": amostra_local_coleta,
                    "data_coleta_amostra": str(amostra_data_coleta),
                    "nome_coletor": amostra_nome_coletor,
                    "metodo_coleta": amostra_metodo_coleta,
                    "condicao_amostra": amostra_condicao,
                    "destino_amostra": amostra_destino,
                    "longitude": amostra_longitude,
                    "resultado_exame": amostra_resultado_exame,
                    "latitude": amostra_latitude,
                    "kit_utilizado": amostra_kit,
                    "observacoes": amostra_observacoes,
                    "caixa": amostra_caixa,
                    "sangue_disponivel": amostra_disponibilidade,
                    "dna_disponivel": amostra_dna,
                    "rna_disponivel": amostra_rna,
                    'sequenciamento': amostra_sequenciamento
                }
                amostra_data = {
                    k: v for k, v in amostra_data.items() if v not in (None, "", [])}

                success, message = add_document('amostras', amostra_data)
                if success:
                    st.success(message)
                else:
                    st.error(message)

# --- Aba: Registrar Exame ---
with tab_exame:
    st.header("Registrar Novo Exame")
    with st.form("form_registro_exame"):
        st.markdown("**Informações do Exame**")
        exame_id_input = st.text_input(
            "ID do Exame (único)", placeholder="Ex: EXM001")

        # Opcional: dropdown com amostras existentes para vincular o exame
        db = connect_to_mongo()
        amostras_collection = db['amostras']
        # Buscar apenas o _id e tipo de amostra
        amostras_existentes = list(amostras_collection.find(
            {}, {"_id": 1, "metodo_coleta": 1}))

        amostra_options = [
            ""] + [f"{amostra.get('metodo_coleta', 'Amostra sem tipo')} (ID: {amostra['_id']})" for amostra in amostras_existentes]
        selected_amostra_str = st.selectbox(
            "Vincular a qual Amostra?", options=amostra_options)

        # Extrair o ID da amostra selecionada
        linked_amostra_id = None
        if selected_amostra_str and " (ID: " in selected_amostra_str:
            linked_amostra_id = selected_amostra_str.split(" (ID: ")[1][:-1]

        exame_tipo = st.text_input("Tipo de Exame")
        exame_laboratorio = st.text_input("Laboratório Realizador")
        exame_data_realizacao = st.date_input(
            "Data de Realização", value=date.today())
        exame_resultado = st.text_area("Resultado do Exame")
        exame_responsavel = st.text_input("Responsável pelo Exame")
        exame_procotocolo = st.text_input("Protocolo Utilizado")
        exame_observacoes = st.text_area("Observações do Exame (opcional)")

        submit_exame = st.form_submit_button("Registrar Exame")

        if submit_exame:
            if not exame_id_input:
                st.error("Por favor, insira um ID único para o exame.")
            elif not linked_amostra_id:
                st.error(
                    "Por favor, selecione uma amostra para vincular este exame.")
            else:
                exame_data = {
                    "_id": exame_id_input,
                    "amostra_id": linked_amostra_id,  # Vincula ao ID da amostra
                    "tipo_exame": exame_tipo,
                    "laboratorio_realizador": exame_laboratorio,
                    "data_realizacao": str(exame_data_realizacao),
                    "resultado_detalhado": exame_resultado,
                    "responsavel_exame": exame_responsavel,
                    "observacoes_exame": exame_observacoes,
                    "protocolo_exame": exame_procotocolo
                }
                exame_data = {k: v for k, v in exame_data.items()
                              if v not in (None, "", [])}

                success, message = add_document('exames', exame_data)
                if success:
                    st.success(message)
                else:
                    st.error(message)

# --- Aba: Registrar Reagente ---
with tab_reagente:
    st.header("Registrar Novo Reagente")
    with st.form("form_registro_reagente"):
        st.markdown("**Informações do Reagente**")
        reagente_id_input = st.text_input(
            "ID do Reagente (único)", placeholder="Ex: REG001")
        reagente_nome = st.text_input("Nome do Reagente")
        reagente_codigo = st.text_input("Código")
        reagente_lote = st.text_input("Número do Lote")
        reagente_marca = st.text_input("Marca")
        reagente_validade = st.date_input(
            "Data de Validade", value=date.today())
        reagente_quantidade = st.number_input(
            "Quantidade (e.g., ml, g, unidades)", min_value=0.0, format="%.2f", step=0.01)
        reagente_local_armazenamento = st.text_input("Local de Armazenamento")
        reagente_observacoes = st.text_area(
            "Observações do Reagente (opcional)")

        submit_reagente = st.form_submit_button("Registrar Reagente")

        if submit_reagente:
            if not reagente_id_input:
                st.error("Por favor, insira um ID único para o reagente.")
            else:
                reagente_data = {
                    "_id": reagente_id_input,
                    "nome": reagente_nome,
                    "codigo": reagente_codigo,
                    "numero_lote": reagente_lote,
                    "marca": reagente_marca,
                    "data_validade": str(reagente_validade),
                    "quantidade": reagente_quantidade,
                    "local_armazenamento": reagente_local_armazenamento,
                    "observacoes": reagente_observacoes
                }
                reagente_data = {
                    k: v for k, v in reagente_data.items() if v not in (None, "", [])}

                success, message = add_document('reagentes', reagente_data)
                if success:
                    st.success(message)
                else:
                    st.error(message)

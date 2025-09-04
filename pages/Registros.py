import streamlit as st
from pymongo import MongoClient
import os


# Função utilitária para exibir campos preenchidos
def exibir_campos(campos):
    for campo, valor in campos.items():
        if valor not in ('Não informado', '', None, 'Nenhuma'):
            st.markdown(f"**{campo}:** {valor}")


# Conexão segura com MongoDB
def connect_to_mongo():
    uri = os.environ.get(
        "MONGO_URI",
        "mongodb+srv://emiliods79:uD5A2J4o38dpk0hX@cluster0.ufpae.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    )
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        db = client['pibit_app']
        db.command("ping")
        return db
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        st.stop()


db = connect_to_mongo()
animais_col = db['animais']
amostras_col = db['amostras']
exames_col = db['exames']
reagentes_col = db['reagentes']


def carregar_animais_mongo():
    try:
        return list(animais_col.find())
    except Exception as e:
        st.error(f"Erro ao carregar animais: {e}")
        return []


def carregar_amostras_mongo():
    try:
        return list(amostras_col.find())
    except Exception as e:
        st.error(f"Erro ao carregar amostras: {e}")
        return []


def carregar_exames_mongo():
    try:
        return list(exames_col.find())
    except Exception as e:
        st.error(f"Erro ao carregar exames: {e}")
        return []


def carregar_reagentes_mongo():
    try:
        return list(reagentes_col.find())
    except Exception as e:
        st.error(f"Erro ao carregar reagentes: {e}")
        return []


st.title("Registros do Sistema")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Animais", "Amostras", "Exames", "Reagentes"])

# ---------------- TAB 1: Animais ----------------
with tab1:
    st.header("Animais Registrados")
    busca = st.text_input("Buscar animal por nome comum, científico ou microchip:")
    animais = carregar_animais_mongo()
    amostras = carregar_amostras_mongo()

    # Filtro de busca
    if busca:
        animais = [
            animal for animal in animais
            if busca.lower() in str(animal.get('nome_comum', '')).lower()
            or busca.lower() in str(animal.get('nome_cientifico', '')).lower()
            or busca.lower() in str(animal.get('microchip', '')).lower()
        ]

    # Paginação
    por_pagina = 7
    total = len(animais)
    inicio = (st.session_state.get("pagina_animal", 1) - 1) * por_pagina
    fim = inicio + por_pagina
    animais_pagina = animais[inicio:fim]

    if not animais_pagina:
        st.info("Nenhum animal cadastrado no banco de dados.")
    else:
        st.caption(
            f"Mostrando {inicio+1} a {min(fim, total)} de {total} animais")
        for animal in animais_pagina:
            with st.expander(f"{animal.get('nome_comum', 'Sem nome comum')} ({animal.get('_id', 'Sem ID')})", expanded=False):
                campos = {
                    "ID": animal.get('_id', 'Sem ID'),
                    "Sexo": animal.get('sexo', 'Não informado'),
                    "Peso (kg)": animal.get('peso', 'Não informado'),
                    "ID HVU": animal.get('hvu', 'Não informado'),
                    "Microchip": animal.get('microchip', 'Não informado'),
                    "Órgão responsável": animal.get('orgao', 'Não informado'),
                    "Status": animal.get('status', 'Não informado'),
                    "Função": animal.get('funcao', 'Não informado'),
                    "Local de Origem": animal.get('local_origem', 'Não informado'),
                    "Data de Nascimento": animal.get('data_nascimento', 'Não informado'),
                    "Observações": animal.get('observacoes', 'Nenhuma'),
                    'Faixa etária': animal.get('faixa_etaria', 'Não informado'),
                    'Classe': animal.get('classe', 'Não informado')
                }
                exibir_campos(campos)

                st.write("---")
                st.subheader("Amostras Coletadas:")
                amostras_do_animal = [a for a in amostras if a.get(
                    'animal_id') == animal.get('_id')]
                if amostras_do_animal:
                    for amostra in amostras_do_animal:
                        texto = f"- Tipo: {amostra.get('metodo_coleta', 'Sem tipo')}, Data: {amostra.get('data_coleta', 'Sem data')}"
                        if amostra.get('local_coleta'):
                            texto += f", Local: {amostra.get('local_coleta')}"
                        st.write(texto)
                else:
                    st.info("Nenhuma amostra para este animal ainda.")

                # Exclusão do animal
                st.markdown("---")
                st.warning(
                    "Esta ação é irreversível. Tem certeza que deseja excluir este animal?")
                if st.button("Confirmar exclusão", key=f"del_animal_{animal.get('_id')}"):
                    animais_col.delete_one({"_id": animal['_id']})
                    st.success(
                        "Animal excluído com sucesso! Atualize a página para ver a lista atualizada.")

        # Paginação embaixo
        pagina = st.number_input(
            "Página", min_value=1, max_value=max(1, (total - 1) // por_pagina + 1),
            value=st.session_state.get("pagina_animal", 1), step=1, key="pagina_animal"
        )

# ---------------- TAB 2: Amostras ----------------
with tab2:
    st.header("Amostras Cadastradas")
    busca_amostra = st.text_input(
        "Buscar amostra por ID, tipo ou animal:", key="busca_amostra")
    amostras = carregar_amostras_mongo()

    # Filtro de busca
    if busca_amostra:
        amostras = [
            a for a in amostras
            if busca_amostra.lower() in str(a.get('_id', '')).lower()
            or busca_amostra.lower() in str(a.get('tipo', '')).lower()
            or busca_amostra.lower() in str(a.get('animal_id', '')).lower()
        ]

    # Paginação
    por_pagina = 7
    total = len(amostras)
    inicio = (st.session_state.get("pagina_amostra", 1) - 1) * por_pagina
    fim = inicio + por_pagina
    amostras_pagina = amostras[inicio:fim]

    if not amostras_pagina:
        st.info("Nenhuma amostra cadastrada no banco de dados.")
    else:
        st.caption(
            f"Mostrando {inicio+1} a {min(fim, total)} de {total} amostras")
        for amostra in amostras_pagina:
            # Usar o ID da amostra para garantir que cada expander seja único
            amostra_id = amostra.get('_id', 'Sem ID')
            with st.expander(f"Amostra {amostra_id}"):
                # --- INÍCIO DA MODIFICAÇÃO ---

                # 1. Exibir os campos não editáveis primeiro
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**ID:** `{amostra.get('_id', 'Sem ID')}`")
                    st.markdown(f"**Animal ID:** {amostra.get('animal_id', 'Não informado')}")
                    st.markdown(f"**Tipo:** {amostra.get('metodo_coleta', 'Não informado')}")
                    st.markdown(f"**Local de Coleta:** {amostra.get('local_coleta', 'Não informado')}")

                with col2:
                    st.markdown(f"**Data de Coleta:** {amostra.get('data_coleta_amostra', 'Não informado')}")
                    st.markdown(f"**Caixa/Freezer:** {amostra.get('caixa', 'Não informado')}")
                    st.markdown(f"**Observações:** {amostra.get('observacoes', 'Nenhuma')}")
                    st.markdown(f"**Sequenciamento:** {amostra.get('Sequenciamento', 'Amostra não sequenciada')}")

                st.markdown("---")
                st.subheader("Disponibilidade")

                # 2. Criar checkboxes interativos para alterar a disponibilidade
                col_sangue, col_dna, col_rna = st.columns(3)

                # Obter o estado atual do banco de dados (True/False)
                sangue_disponivel_atual = amostra.get('sangue_disponivel', False)
                dna_disponivel_atual = amostra.get('dna_disponivel', False)
                rna_disponivel_atual = amostra.get('rna_disponivel', False)

                # Criar os checkboxes. O valor deles será o novo estado.
                with col_sangue:
                    novo_status_sangue = st.checkbox(
                        "Sangue Disponível",
                        value=sangue_disponivel_atual,
                        key=f"sangue_{amostra_id}" # Chave única para cada checkbox
                    )
                with col_dna:
                    novo_status_dna = st.checkbox(
                        "DNA Disponível",
                        value=dna_disponivel_atual,
                        key=f"dna_{amostra_id}"
                    )
                with col_rna:
                    novo_status_rna = st.checkbox(
                        "RNA Disponível",
                        value=rna_disponivel_atual,
                        key=f"rna_{amostra_id}"
                    )

                # 3. Verificar se houve mudança e atualizar o banco de dados
                if novo_status_sangue != sangue_disponivel_atual:
                    amostras_col.update_one(
                        {'_id': amostra_id},
                        {'$set': {'sangue_disponivel': novo_status_sangue}}
                    )
                    st.toast("Disponibilidade de Sangue atualizada!")
                    st.rerun() # Recarrega o script para refletir a mudança

                if novo_status_dna != dna_disponivel_atual:
                    amostras_col.update_one(
                        {'_id': amostra_id},
                        {'$set': {'dna_disponivel': novo_status_dna}}
                    )
                    st.toast("Disponibilidade de DNA atualizada!")
                    st.rerun()

                if novo_status_rna != rna_disponivel_atual:
                    amostras_col.update_one(
                        {'_id': amostra_id},
                        {'$set': {'rna_disponivel': novo_status_rna}}
                    )
                    st.toast("Disponibilidade de RNA atualizada!")
                    st.rerun()

                # --- FIM DA MODIFICAÇÃO ---

                # Seção de Exclusão (inalterada)
                st.markdown("---")
                st.warning(
                    "Esta ação é irreversível. Tem certeza que deseja excluir esta amostra?")
                if st.button("Confirmar exclusão", key=f"del_amostra_{amostra_id}"):
                    amostras_col.delete_one({"_id": amostra_id})
                    st.success(
                        "Amostra excluída com sucesso! Atualize a página para ver a lista atualizada.")
                    st.rerun()

        # Paginação embaixo (inalterada)
        pagina = st.number_input(
            "Página", min_value=1, max_value=max(1, (total - 1) // por_pagina + 1),
            value=st.session_state.get("pagina_amostra", 1), step=1, key="pagina_amostra"
        )

# ---------------- TAB 3: Exames ----------------
with tab3:
    st.header("Exames Cadastrados")
    busca_exame = st.text_input(
        "Buscar exame por ID, animal, amostra ou tipo:", key="busca_exame")
    exames = carregar_exames_mongo()

    # Filtro de busca
    if busca_exame:
        exames = [
            e for e in exames
            if busca_exame.lower() in str(e.get('_id', '')).lower()
            or busca_exame.lower() in str(e.get('animal_id', '')).lower()
            or busca_exame.lower() in str(e.get('amostra_id', '')).lower()
            or busca_exame.lower() in str(e.get('tipo_exame', '')).lower()
        ]

    # Paginação
    por_pagina = 7
    total = len(exames)
    inicio = (st.session_state.get("pagina_exame", 1) - 1) * por_pagina
    fim = inicio + por_pagina
    exames_pagina = exames[inicio:fim]

    if not exames_pagina:
        st.info("Nenhum exame cadastrado no banco de dados.")
    else:
        st.caption(
            f"Mostrando {inicio+1} a {min(fim, total)} de {total} exames")
        for exame in exames_pagina:
            with st.expander(f"Exame {exame.get('_id', 'Sem ID')}"):
                campos = {
                    "ID": exame.get('_id', 'Sem ID'),
                    "Amostra ID": exame.get('amostra_id', 'Não informado'),
                    "Animal ID": exame.get('animal_id', 'Não informado'),
                    "Tipo de Exame": exame.get('tipo_exame', 'Não informado'),
                    "Laboratório Realizador": exame.get('laboratorio_realizador', 'Não informado'),
                    "Data de Realização": exame.get('data_realizacao', 'Não informado'),
                    "Resultado": exame.get('resultado_detalhado', 'Não informado'),
                    "Responsável": exame.get('responsavel_exame', 'Não informado'),
                    "Observações": exame.get('observacoes_exame', 'Nenhuma')
                }
                exibir_campos(campos)

                # Exclusão do exame
                st.markdown("---")
                st.warning(
                    "Esta ação é irreversível. Tem certeza que deseja excluir este exame?")
                if st.button("Confirmar exclusão", key=f"del_exame_{exame.get('_id')}"):
                    exames_col.delete_one({"_id": exame['_id']})
                    st.success(
                        "Exame excluído com sucesso! Atualize a página para ver a lista atualizada.")

        # Paginação embaixo
        pagina = st.number_input(
            "Página", min_value=1, max_value=max(1, (total - 1) // por_pagina + 1),
            value=st.session_state.get("pagina_exame", 1), step=1, key="pagina_exame"
        )

# ---------------- TAB 4: Reagentes ----------------
with tab4:
    st.header("Reagentes Cadastrados")
    busca_reagente = st.text_input(
        "Buscar reagente por nome, tipo ou fornecedor:", key="busca_reagente")
    reagentes = carregar_reagentes_mongo()

    # Filtro de busca
    if busca_reagente:
        reagentes = [
            r for r in reagentes
            if busca_reagente.lower() in str(r.get('nome', '')).lower()
            or busca_reagente.lower() in str(r.get('tipo', '')).lower()
            or busca_reagente.lower() in str(r.get('fornecedor', '')).lower()
        ]

    # Paginação
    por_pagina = 7
    total = len(reagentes)
    inicio = (st.session_state.get("pagina_reagente", 1) - 1) * por_pagina
    fim = inicio + por_pagina
    reagentes_pagina = reagentes[inicio:fim]

    if not reagentes_pagina:
        st.info("Nenhum reagente cadastrado no banco de dados.")
    else:
        st.caption(
            f"Mostrando {inicio+1} a {min(fim, total)} de {total} reagentes")
        for reagente in reagentes_pagina:
            with st.expander(f"Reagente {reagente.get('nome', 'Sem ID')}"):
                campos = {
                    "ID": reagente.get('_id', 'Sem ID'),
                    "Nome": reagente.get('nome', 'Não informado'),
                    "Código": reagente.get('codigo', 'Não informado'),
                    "Número do Lote": reagente.get('numero_lote', 'Não informado'),
                    "Marca": reagente.get('marca', 'Não informado'),
                    "Validade": reagente.get('data_validade', 'Não informado'),
                    "Quantidade": reagente.get('quantidade', 'Não informado'),
                    "Unidade": reagente.get('unidade', 'Não informado'),
                    "Local de Armazenamento": reagente.get('local_armazenamento', 'Não informado'),
                    "Observações": reagente.get('observacoes', 'Nenhuma')
                }
                exibir_campos(campos)
                nova_quantidade = st.number_input(
                    "Atualizar quantidade disponível", min_value=0, value=int(reagente.get('quantidade', 0)), step=1, key=f"qtd_{reagente.get('_id')}")
                if st.button("Salvar nova quantidade", key=f"btn_{reagente.get('_id')}"):
                    reagentes_col.update_one({"_id": reagente['_id']}, {
                                             "$set": {"quantidade": nova_quantidade}})
                    st.success("Quantidade atualizada!")

                # Confirmação para deleção (sem expander aninhado)
                st.markdown("---")
                st.warning(
                    "Esta ação é irreversível. Tem certeza que deseja excluir este reagente?")
                if st.button("Confirmar exclusão", key=f"del_{reagente.get('_id')}"):
                    reagentes_col.delete_one({"_id": reagente['_id']})
                    st.success(
                        "Reagente excluído com sucesso! Atualize a página para ver a lista atualizada.")

        # Paginação embaixo
        pagina = st.number_input(
            "Página", min_value=1, max_value=max(1, (total - 1) // por_pagina + 1),
            value=st.session_state.get("pagina_reagente", 1), step=1, key="pagina_reagente"
        )

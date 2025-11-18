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

# helper: transforma chave em rótulo legível


def _prettify(key: str) -> str:
    return key.replace('_', ' ').capitalize()

# helper: exibe todos os campos preenchidos de um documento (somente non-empty)


def display_document(doc: dict, title: str = None):
    if title:
        st.subheader(title)
    if not doc:
        st.info("Registro não encontrado.")
        return
    # exibir _id primeiro
    if '_id' in doc and doc['_id'] not in (None, '', []):
        st.markdown(f"**ID:** `{doc['_id']}`")
    for k, v in doc.items():
        if k == '_id':
            continue
        if v in (None, '', [], {}, 'Não informado', 'Nenhuma'):
            continue
        # formatar listas e dicts
        if isinstance(v, list):
            v = ', '.join(map(str, v)) if v else v
        elif isinstance(v, dict):
            v = ', '.join(f"{_prettify(kk)}: {vv}" for kk,
                          vv in v.items() if vv not in (None, '', []))
        st.markdown(f"**{_prettify(k)}:** {v}")


# ---------------- TAB 1: Animais ----------------
with tab1:
    st.header("Animais Registrados")
    busca = st.text_input(
        "Buscar animal por nome comum, científico ou microchip:")
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
                # mostrar todos os campos preenchidos do animal
                display_document(animal, title="Dados do Animal")

                st.write("---")
                st.subheader("Amostras Coletadas:")
                amostras_do_animal = [a for a in amostras if a.get(
                    'animal_id') == animal.get('_id')]
                if amostras_do_animal:
                    for amostra in amostras_do_animal:
                        # exibir somente campos preenchidos da amostra (resumido)
                        st.markdown(
                            f"**Amostra:** `{amostra.get('_id')}` — {_prettify('metodo_coleta')}: {amostra.get('metodo_coleta','Não informado')}")
                        # opcional: botao para expandir amostra completa
                        if st.button("Ver detalhes da amostra", key=f"ver_am_{amostra.get('_id')}_{animal.get('_id')}"):
                            display_document(
                                amostra, title=f"Detalhes da Amostra {amostra.get('_id')}")
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
    animais = carregar_animais_mongo()  # garantir disponibilidade

    # Filtro de busca
    if busca_amostra:
        amostras = [
            a for a in amostras
            if busca_amostra.lower() in str(a.get('_id', '')).lower()
            or busca_amostra.lower() in str(a.get('metodo_coleta', '')).lower()
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
            amostra_id = amostra.get('_id', 'Sem ID')
            with st.expander(f"Amostra {amostra_id}"):
                # exibir todos os campos preenchidos da amostra
                display_document(amostra, title="Dados da Amostra")

                # mostrar animal relacionado, se houver
                animal = next((an for an in animais if an.get(
                    '_id') == amostra.get('animal_id')), None)
                if animal:
                    st.markdown("---")
                    display_document(
                        animal, title=f"Animal relacionado ({animal.get('nome_comum','Sem nome')})")

                # disponibilidade - manter checkboxes já existentes
                st.markdown("---")
                st.subheader("Disponibilidade")

                # valores atuais (fallbacks seguros)
                current_status = amostra.get('status_amostra') or amostra.get(
                    'condicao_amostra') or amostra.get('status') or "Não informado"
                current_disponivel = bool(amostra.get('disponivel')) if 'disponivel' in amostra else (
                    str(current_status).lower() in ('disponivel', 'disponível', 'disponible'))
                current_local = amostra.get('destino_amostra') or amostra.get(
                    'local_coleta') or amostra.get('local_armazenamento') or ""

                # opções de status padronizadas
                status_options = ["Disponível", "Reservada",
                                  "Em uso", "Consumida", "Perdida", "Não informado"]
                # tenta achar índice atual nas opções (caso insira um valor arbitrário, usa "Não informado")
                try:
                    status_index = next(i for i, s in enumerate(
                        status_options) if s.lower() == str(current_status).strip().lower())
                except StopIteration:
                    status_index = status_options.index("Não informado")

                col1, col2 = st.columns([2, 2])
                with col1:
                    novo_status = st.selectbox(
                        "Status da amostra", options=status_options, index=status_index, key=f"status_{amostra_id}")
                    disponivel_checkbox = st.checkbox(
                        "Disponível", value=current_disponivel, key=f"disp_{amostra_id}")
                with col2:
                    novo_local = st.text_input(
                        "Local / Destino", value=current_local, key=f"local_{amostra_id}")

                if st.button("Salvar disponibilidade", key=f"salvar_disp_{amostra_id}"):
                    update = {
                        "status_amostra": novo_status,
                        "disponivel": bool(disponivel_checkbox),
                        "destino_amostra": novo_local
                    }
                    try:
                        amostras_col.update_one(
                            {"_id": amostra_id}, {"$set": update})
                        st.success("Disponibilidade atualizada com sucesso.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Erro ao atualizar disponibilidade: {e}")

                # Seção de Exclusão
                st.markdown("---")
                st.warning(
                    "Esta ação é irreversível. Tem certeza que deseja excluir esta amostra?")
                if st.button("Confirmar exclusão", key=f"del_amostra_{amostra_id}"):
                    amostras_col.delete_one({"_id": amostra_id})
                    st.success(
                        "Amostra excluída com sucesso! Atualize a página para ver a lista atualizada.")
                    st.rerun()

        # Paginação embaixo
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
    amostras = carregar_amostras_mongo()
    animais = carregar_animais_mongo()

    # Filtro de busca
    if busca_exame:
        exames = [
            e for e in exames
            if busca_exame.lower() in str(e.get('_id', '')).lower()
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
                # exibir todos os campos do exame
                display_document(exame, title="Dados do Exame")

                # exibir amostra relacionada e animal relacionado (com nome em extenso)
                amostra = next((a for a in amostras if a.get(
                    '_id') == exame.get('amostra_id')), None)
                animal = None
                if amostra:
                    animal = next((an for an in animais if an.get(
                        '_id') == amostra.get('animal_id')), None)
                    st.markdown("---")
                    # incluir animal nome em extenso entre parênteses na linha da amostra
                    if animal:
                        display_document(
                            amostra, title=f"Amostra relacionada ({animal.get('nome_comum','Sem nome')} — {animal.get('_id')})")
                        # opcional: também mostrar o animal completo abaixo
                        display_document(animal, title="Animal relacionado")
                    else:
                        display_document(amostra, title="Amostra relacionada")

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
                # exibe dinamicamente todos os campos preenchidos do reagente
                display_document(reagente, title="Dados do Reagente")
                nova_quantidade = st.number_input(
                    "Atualizar quantidade disponível", min_value=0, value=int(reagente.get('quantidade', 0)), step=1, key=f"qtd_{reagente.get('_id')}")
                if st.button("Salvar nova quantidade", key=f"btn_{reagente.get('_id')}"):
                    reagentes_col.update_one({"_id": reagente['_id']}, {
                                             "$set": {"quantidade": nova_quantidade}})
                    st.success("Quantidade atualizada!")

                # Confirmação para deleção (sem expander aninhada)
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

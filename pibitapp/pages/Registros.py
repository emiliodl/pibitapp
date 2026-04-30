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
        st.markdown(f"**ID Interno:** `{doc['_id']}`")
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
    # ATUALIZADO: Descrição da busca inclui ID HVU
    busca = st.text_input(
        "Buscar animal por nome, microchip ou ID HVU:", key="busca_animal_input")
    
    animais = carregar_animais_mongo()
    amostras = carregar_amostras_mongo()

    # ATUALIZADO: Filtro de busca incluindo o campo id_hvu
    if busca:
        termo = busca.lower()
        animais = [
            a for a in animais
            if termo in str(a.get('nome_comum', '')).lower()
            or termo in str(a.get('nome_cientifico', '')).lower()
            or termo in str(a.get('microchip', '')).lower()
            or termo in str(a.get('id_hvu', '')).lower()  # Busca por ID HVU
            or termo in str(a.get('_id', '')).lower()      # Busca por ID do banco
        ]

    # Paginação
    por_pagina = 7
    total = len(animais)
    inicio = (st.session_state.get("pagina_animal", 1) - 1) * por_pagina
    fim = inicio + por_pagina
    animais_pagina = animais[inicio:fim]

    if not animais_pagina:
        st.info("Nenhum animal encontrado com este critério.")
    else:
        st.caption(
            f"Mostrando {inicio+1} a {min(fim, total)} de {total} animais")
        for animal in animais_pagina:
            # Título do expander exibindo ID HVU para facilitar identificação
            label_hvu = f" | HVU: {animal.get('id_hvu')}" if animal.get('id_hvu') else ""
            with st.expander(f"{animal.get('nome_comum', 'Sem nome')} ({animal.get('_id')}){label_hvu}", expanded=False):
                display_document(animal, title="Dados do Animal")
                if st.button("Editar animal", key=f"editar_animal_{animal.get('_id')}"):
                    flag = f"editando_{animal.get('_id')}"
                    st.session_state[flag] = not st.session_state.get(flag, False)

                if st.session_state.get(f"editando_{animal.get('_id')}"):
                    st.subheader("Editar Dados do Animal")
                    with st.form(key=f"form_editar_animal_{animal.get('_id')}"):

                        col1, col2 = st.columns(2)
                        with col1:
                            novo_nome_comum = st.text_input("Nome Comum", value=animal.get("nome_comum", ""))
                            novo_nome_cientifico = st.text_input("Nome Científico", value=animal.get("nome_cientifico", ""))
                            novo_id_projeto = st.text_input("ID do Projeto", value=animal.get("animal_id_projeto", ""))
                            novo_hvu = st.text_input("ID do HVU", value=animal.get("hvu", ""))
                            novo_microchip = st.text_input("Microchip", value=animal.get("microchip", ""))
                            novo_local_origem = st.text_input("Local de Origem", value=animal.get("local_origem", ""))
                            nova_idade = st.text_input("Idade", value=animal.get("idade", ""))
                            nova_suspeita = st.text_input("Suspeita Clínica", value=animal.get("suspeita_clinica", ""))

                        with col2:
                            sexo_opts = ["", "Macho", "Fêmea", "Desconhecido"]
                            sexo_atual = animal.get("sexo", "")
                            novo_sexo = st.selectbox("Sexo", sexo_opts,
                                index=sexo_opts.index(sexo_atual) if sexo_atual in sexo_opts else 0)

                            orgao_opts = ['UFPI', 'NEPPAS', 'IBAMA - CETAS - PI', 'IBAMA - CETAS - CE',
                                          'IBAMA - CETAS - RN', 'SEMARH - CETAS - PI', 'UFPA', 'UFRR',
                                          'UFAC', 'UFOB', 'DSEI LESTE - AM', 'ZOOLOGICO -PI', 'PARTICULAR', 'Outro']
                            orgao_atual = animal.get("orgao", "UFPI")
                            novo_orgao = st.selectbox("Órgão de Origem", orgao_opts,
                                index=orgao_opts.index(orgao_atual) if orgao_atual in orgao_opts else 0)

                            status_opts = ["", "Vida livre", "Cativeiro"]
                            status_atual = animal.get("status", "")
                            novo_status = st.selectbox("Status do Animal", status_opts,
                                index=status_opts.index(status_atual) if status_atual in status_opts else 0)

                            funcao_opts = ["PET", "Trabalho", "Lazer", "Outros"]
                            funcao_atual = animal.get("funcao", "Outros")
                            nova_funcao = st.selectbox("Função", funcao_opts,
                                index=funcao_opts.index(funcao_atual) if funcao_atual in funcao_opts else 3)

                            faixa_opts = ["Filhote", "Suvenil", " Sub Adulto", "Adulto", "Senil", "Não Informado"]
                            faixa_atual = animal.get("faixa_etaria", "Não Informado")
                            nova_faixa = st.selectbox("Faixa Etária", faixa_opts,
                                index=faixa_opts.index(faixa_atual) if faixa_atual in faixa_opts else 5)

                            classe_opts = ["Ave", "Mamífero", "Répteis", " Anfíbios", "Peixes"]
                            classe_atual = animal.get("classe", "")
                            nova_classe = st.selectbox("Classe", classe_opts,
                                index=classe_opts.index(classe_atual) if classe_atual in classe_opts else 0)

                            novo_peso = st.number_input("Peso (kg)", min_value=0.0, format="%.2f", step=0.01,
                                value=float(animal.get("peso", 0.0)))

                        novas_obs = st.text_area("Observações", value=animal.get("observacoes", ""))

                        col_s, col_c = st.columns(2)
                        with col_s:
                            salvar = st.form_submit_button("Salvar alterações")
                        with col_c:
                            cancelar = st.form_submit_button("Cancelar")

                        if salvar:
                            update_data = {
                                "nome_comum": novo_nome_comum,
                                "nome_cientifico": novo_nome_cientifico,
                                "animal_id_projeto": novo_id_projeto,
                                "hvu": novo_hvu,
                                "microchip": novo_microchip,
                                "local_origem": novo_local_origem,
                                "idade": nova_idade,
                                "suspeita_clinica": nova_suspeita,
                                "sexo": novo_sexo,
                                "orgao": novo_orgao,
                                "status": novo_status,
                                "funcao": nova_funcao,
                                "faixa_etaria": nova_faixa,
                                "classe": nova_classe,
                                "peso": novo_peso,
                                "observacoes": novas_obs,
                            }
                            update_data = {k: v for k, v in update_data.items() if v not in (None, "", [])}
                            animais_col.update_one({"_id": animal["_id"]}, {"$set": update_data})
                            st.success("✅ Animal atualizado com sucesso!")
                            st.session_state[f"editando_{animal.get('_id')}"] = False
                            st.rerun()

                        if cancelar:
                            st.session_state[f"editando_{animal.get('_id')}"] = False
                            st.rerun()


                st.write("---")
                st.subheader("Amostras Coletadas:")
                amostras_do_animal = [a for a in amostras if a.get(
                    'animal_id') == animal.get('_id')]
                if amostras_do_animal:
                    for amostra in amostras_do_animal:
                        st.markdown(
                            f"**Amostra:** `{amostra.get('_id')}` — {_prettify('metodo_coleta')}: {amostra.get('metodo_coleta','Não informado')}")
                        if st.button("Ver detalhes da amostra", key=f"ver_am_{amostra.get('_id')}_{animal.get('_id')}"):
                            display_document(
                                amostra, title=f"Detalhes da Amostra {amostra.get('_id')}")
                else:
                    st.info("Nenhuma amostra para este animal ainda.")

                st.markdown("---")
                st.warning("Esta ação é irreversível.")
                if st.button("Confirmar exclusão", key=f"del_animal_{animal.get('_id')}"):
                    animais_col.delete_one({"_id": animal['_id']})
                    st.success("Animal excluído! Recarregue a página.")
                    st.rerun()

        st.number_input(
            "Página", min_value=1, max_value=max(1, (total - 1) // por_pagina + 1),
            value=st.session_state.get("pagina_animal", 1), step=1, key="pagina_animal"
        )

# ---------------- TAB 2: Amostras ----------------
with tab2:
    st.header("Amostras Cadastradas")
    busca_amostra = st.text_input(
        "Buscar amostra por ID, tipo ou animal:", key="busca_amostra")
    amostras = carregar_amostras_mongo()
    animais = carregar_animais_mongo()

    if busca_amostra:
        termo_am = busca_amostra.lower()
        amostras = [
            a for a in amostras
            if termo_am in str(a.get('_id', '')).lower()
            or termo_am in str(a.get('metodo_coleta', '')).lower()
            or termo_am in str(a.get('animal_id', '')).lower()
        ]

    por_pagina = 7
    total_am = len(amostras)
    inicio_am = (st.session_state.get("pagina_amostra", 1) - 1) * por_pagina
    fim_am = inicio_am + por_pagina
    amostras_pagina = amostras[inicio_am:fim_am]

    if not amostras_pagina:
        st.info("Nenhuma amostra encontrada.")
    else:
        for amostra in amostras_pagina:
            amostra_id = amostra.get('_id', 'Sem ID')
            with st.expander(f"Amostra {amostra_id}"):
                display_document(amostra, title="Dados da Amostra")

                animal = next((an for an in animais if an.get(
                    '_id') == amostra.get('animal_id')), None)
                if animal:
                    st.markdown("---")
                    display_document(
                        animal, title=f"Animal relacionado ({animal.get('nome_comum','Sem nome')})")

                st.markdown("---")
                st.subheader("Disponibilidade")
                
                current_status = amostra.get('status_amostra') or "Não informado"
                current_disponivel = bool(amostra.get('disponivel'))
                current_local = amostra.get('destino_amostra') or ""

                status_options = ["Disponível", "Reservada", "Em uso", "Consumida", "Perdida", "Não informado"]
                try:
                    status_index = next(i for i, s in enumerate(status_options) if s.lower() == str(current_status).strip().lower())
                except:
                    status_index = 5

                col1, col2 = st.columns(2)
                with col1:
                    novo_status = st.selectbox("Status", options=status_options, index=status_index, key=f"status_{amostra_id}")
                    disponivel_checkbox = st.checkbox("Disponível", value=current_disponivel, key=f"disp_{amostra_id}")
                with col2:
                    novo_local = st.text_input("Local / Destino", value=current_local, key=f"local_{amostra_id}")

                if st.button("Salvar alterações", key=f"salvar_disp_{amostra_id}"):
                    amostras_col.update_one({"_id": amostra_id}, {"$set": {
                        "status_amostra": novo_status,
                        "disponivel": bool(disponivel_checkbox),
                        "destino_amostra": novo_local
                    }})
                    st.success("Atualizado!")
                    st.rerun()

                if st.button("Excluir amostra", key=f"del_amostra_{amostra_id}"):
                    amostras_col.delete_one({"_id": amostra_id})
                    st.rerun()

        st.number_input("Página", min_value=1, max_value=max(1, (total_am - 1) // por_pagina + 1), key="pagina_amostra")

# ---------------- TAB 3: Exames ----------------
with tab3:
    st.header("Exames Cadastrados")
    busca_exame = st.text_input("Buscar exame:", key="busca_exame")
    exames = carregar_exames_mongo()

    if busca_exame:
        termo_ex = busca_exame.lower()
        exames = [e for e in exames if termo_ex in str(e.values()).lower()]

    por_pagina = 7
    total_ex = len(exames)
    inicio_ex = (st.session_state.get("pagina_exame", 1) - 1) * por_pagina
    exames_pagina = exames[inicio_ex : inicio_ex + por_pagina]

    for exame in exames_pagina:
        with st.expander(f"Exame {exame.get('_id')}"):
            display_document(exame)
            if st.button("Excluir Exame", key=f"del_ex_{exame.get('_id')}"):
                exames_col.delete_one({"_id": exame.get('_id')})
                st.rerun()

    st.number_input("Página", min_value=1, max_value=max(1, (total_ex - 1) // por_pagina + 1), key="pagina_exame")

# ---------------- TAB 4: Reagentes ----------------
with tab4:
    st.header("Reagentes Cadastrados")
    busca_reagente = st.text_input("Buscar reagente:", key="busca_reagente")
    reagentes = carregar_reagentes_mongo()

    if busca_reagente:
        termo_re = busca_reagente.lower()
        reagentes = [r for r in reagentes if termo_re in str(r.get('nome', '')).lower()]

    for reagente in reagentes:
        with st.expander(f"Reagente: {reagente.get('nome')}"):
            display_document(reagente)
            nova_qtd = st.number_input("Qtd", value=int(reagente.get('quantidade', 0)), key=f"q_{reagente['_id']}")
            if st.button("Atualizar Qtd", key=f"b_{reagente['_id']}"):
                reagentes_col.update_one({"_id": reagente['_id']}, {"$set": {"quantidade": nova_qtd}})
                st.success("Ok!")
            if st.button("Excluir", key=f"d_{reagente['_id']}"):
                reagentes_col.delete_one({"_id": reagente['_id']})
                st.rerun()

import streamlit as st

# --- Funções para gerenciar dados (simulando um CRUD) ---
def carregar_animais():
    # Simula carregar de um DB ou arquivo
    if 'animais' not in st.session_state:
        st.session_state.animais = []
    return st.session_state.animais

def adicionar_animal(nome, especie):
    st.session_state.animais.append({'id': len(st.session_state.animais) + 1, 'nome': nome, 'especie': especie, 'amostras': []})

def adicionar_amostra(animal_id, tipo_amostra, data_coleta):
    for animal in st.session_state.animais:
        if animal['id'] == animal_id:
            animal['amostras'].append({'tipo': tipo_amostra, 'data': data_coleta})
            break

# --- Interface do Streamlit ---
st.title("Sistema de Gestão de Animais e Amostras")

tab1, tab2 = st.tabs(["Animais Cadastrados", "Adicionar Novo Animal"])

with tab1:
    st.header("Lista de Animais Cadastrados")
    animais = carregar_animais()

    if not animais:
        st.info("Nenhum animal cadastrado ainda.")
    else:
        for animal in animais:
            # Usando expander para cada animal
            with st.expander(f"**{animal['nome']}** ({animal['especie']})"):
                st.write(f"ID do Animal: {animal['id']}")
                st.write("---")
                st.subheader("Amostras Coletadas:")
                if animal['amostras']:
                    for amostra in animal['amostras']:
                        st.write(f"- Tipo: {amostra['tipo']}, Data: {amostra['data']}")
                else:
                    st.info("Nenhuma amostra para este animal ainda.")

                st.subheader("Adicionar Nova Amostra:")
                with st.form(key=f"form_amostra_{animal['id']}"):
                    tipo_amostra = st.text_input("Tipo da Amostra", key=f"tipo_{animal['id']}")
                    data_coleta = st.date_input("Data da Coleta", key=f"data_{animal['id']}")
                    submit_button = st.form_submit_button("Adicionar Amostra")

                    if submit_button:
                        if tipo_amostra:
                            adicionar_amostra(animal['id'], tipo_amostra, str(data_coleta))
                            st.success("Amostra adicionada com sucesso!")
                            st.rerun() # Recarregar para mostrar a nova amostra
                        else:
                            st.warning("Por favor, preencha o tipo da amostra.")

with tab2:
    st.header("Adicionar Novo Animal")
    with st.form("form_novo_animal"):
        nome_animal = st.text_input("Nome do Animal")
        especie_animal = st.text_input("Espécie")
        submit_novo_animal = st.form_submit_button("Cadastrar Animal")

        if submit_novo_animal:
            if nome_animal and especie_animal:
                adicionar_animal(nome_animal, especie_animal)
                st.success(f"Animal '{nome_animal}' cadastrado com sucesso!")
                st.rerun() # Recarregar para aparecer na lista de animais
            else:
                st.warning("Por favor, preencha todos os campos.")
import streamlit as st
from pymongo import MongoClient
from bson import SON
from widgets import __login__
from datetime import datetime, timedelta

st.markdown(
    """
    <h1 style='text-align: center; font-size: 32px; margin-top: 10px;'>
        LABVEPI - Laboratório de Vigilância de Epizootias - UFPI
    </h1>
    """,
    unsafe_allow_html=True
)

# Inicialização do objeto de login
__login__obj = __login__(
    company_name="UFPI",
    width=200, height=250,
    logout_button_name='Logout',
    hide_menu_bool=False,
    hide_footer_bool=False,
)

# Construindo a interface de login
LOGGED_IN = __login__obj.build_login_ui()
username = __login__obj.get_username()


def connect_to_mongo():
    uri = ("mongodb+srv://emiliods79:uD5A2J4o38dpk0hX@cluster0.ufpae.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    client = MongoClient(uri)
    db = client['pibit_app']  # Ou já especificado na URI, se preferir.
    return db


if LOGGED_IN:
    # Armazenando o usuário no estado da sessão
    if 'username' not in st.session_state:
        st.session_state['username'] = username

    # Alertas na sidebar
    with st.sidebar:
        # Criar expander para os alertas
        with st.expander("📊 Sistema de Alertas", expanded=True):
            # Conexão com o banco
            db = connect_to_mongo()
            reagentes_col = db['reagentes']

            # Buscar reagentes com quantidade <= 2
            reagentes_baixo_estoque = list(
                reagentes_col.find({"quantidade": {"$lte": 2}}))

            # Buscar reagentes que vencem em 30 dias
            data_limite = (datetime.now() + timedelta(days=30)
                           ).strftime('%Y-%m-%d')
            reagentes_vencendo = list(reagentes_col.find({
                "data_validade": {
                    "$lte": data_limite,
                    "$gte": datetime.now().strftime('%Y-%m-%d')
                }
            }))

            if not reagentes_baixo_estoque and not reagentes_vencendo:
                st.info("Nenhum alerta pendente! 👍")
            else:
                # Exibir alertas se houver reagentes com baixo estoque
                if reagentes_baixo_estoque:
                    st.markdown(
                        f"""
                        <div style='background-color: #fff3cd; padding: 10px; border-radius: 5px; border-left: 5px solid #ffc107;'>
                        <h4 style='color: #856404;'>⚠️ Reagentes com Baixo Estoque ({len(reagentes_baixo_estoque)})</h4>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    for reagente in reagentes_baixo_estoque:
                        st.markdown(
                            f"""
                            - **{reagente.get('nome', 'Sem nome')}**
                                - Quantidade: {reagente.get('quantidade', 0)} {reagente.get('unidade', '')}
                                - Local: {reagente.get('local_armazenamento', 'Não informado')}
                            """
                        )

                # Exibir alertas se houver reagentes próximos do vencimento
                if reagentes_vencendo:
                    st.markdown(
                        f"""
                        <div style='background-color: #f8d7da; padding: 10px; border-radius: 5px; border-left: 5px solid #dc3545;'>
                        <h4 style='color: #721c24;'>⚠️ Reagentes Próximos do Vencimento ({len(reagentes_vencendo)})</h4>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    for reagente in reagentes_vencendo:
                        st.markdown(
                            f"""
                            - **{reagente.get('nome', 'Sem nome')}**
                                - Vence em: {reagente.get('data_validade', 'Data não informada')}
                                - Local: {reagente.get('local_armazenamento', 'Não informado')}
                            """
                        )

                # Botão para ir para a página de reagentes
                if st.button("Ver Todos os Reagentes"):
                    st.switch_page("pages/Registros.py")

else:
    st.write("Por favor, faça login para acessar a aplicação.")

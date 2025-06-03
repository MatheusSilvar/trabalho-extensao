import streamlit as st




# Configurar a página
st.set_page_config(
    page_title="ChatBot PUC Campinas",
    page_icon="🎓",
    layout="wide"
)

# Verificar estado de login
if "usuario_logado" not in st.session_state:
    # Se não estiver logado, mostrar página de login
    with open("trabalho.py", "r", encoding="utf-8") as f:
        exec(f.read())
else:
    # Se estiver logado, mostrar chat
    with open("chatUI.py", "r", encoding="utf-8") as f:
        exec(f.read())
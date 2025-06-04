# app.py - Sistema de Cadastro de Usuários para Chatbot PUC Campinas
import streamlit as st
import pymongo
import hashlib
import datetime
import re
import os
from dotenv import load_dotenv


load_dotenv()
url = os.getenv("MONGO_URL")
print(f"URL: {url}")

# Configuração da conexão com MongoDB
def conectar_mongodb():
    client = pymongo.MongoClient(url)
    db = client["chatbot_puc"]
    return db

# Função para validar email institucional
def validar_email(email):
    padrao = r'^[a-zA-Z0-9._%+-]+@(puc-campinas\.edu\.br|puccampinas\.edu\.br)$'
    return bool(re.match(padrao, email))

# Função para criar hash de senha
def criar_hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Função principal de cadastro
def cadastrar_usuario(nome, email, senha, tipo_usuario, ra=None, curso=None, departamento=None):
    db = conectar_mongodb()
    colecao_usuarios = db["usuarios"]
    
    # Verifica se usuário já existe
    if colecao_usuarios.find_one({"email": email}):
        return False, "Email já cadastrado no sistema"
    
    # Validação de email institucional
    if not validar_email(email):
        return False, "Use um email institucional válido (@puc-campinas.edu.br)"
    
    # Prepara documento de usuário
    novo_usuario = {
        "nome_completo": nome,
        "email": email,
        "senha_hash": criar_hash_senha(senha),
        "tipo_usuario": tipo_usuario,
        "data_cadastro": datetime.datetime.now(),
        "ultimo_acesso": datetime.datetime.now(),
        "status": "ativo"
    }
    
    # Adiciona campos específicos por tipo de usuário
    if tipo_usuario == "estudante" and ra:
        novo_usuario["ra"] = ra
        novo_usuario["curso"] = curso
    elif tipo_usuario == "professor":
        novo_usuario["departamento"] = departamento
        novo_usuario["curso"] = curso
    elif tipo_usuario == "funcionario":
        novo_usuario["departamento"] = departamento
    
    # Insere no banco de dados
    try:
        resultado = colecao_usuarios.insert_one(novo_usuario)
        return True, str(resultado.inserted_id)
    except Exception as e:
        return False, f"Erro no banco de dados: {str(e)}"

# Função de autenticação
def autenticar_usuario(email, senha):
    db = conectar_mongodb()
    colecao_usuarios = db["usuarios"]
    
    usuario = colecao_usuarios.find_one({
        "email": email,
        "senha_hash": criar_hash_senha(senha)
    })
    
    if usuario:
        # Atualiza último acesso
        colecao_usuarios.update_one(
            {"_id": usuario["_id"]},
            {"$set": {"ultimo_acesso": datetime.datetime.now()}}
        )
        return True, usuario
    
    return False, None

# Interface Streamlit
# REMOVIDO: st.set_page_config (já está no gerenciador)

# Título e descrição
st.title("ChatBot PUC Campinas")
st.subheader("Sistema de Cadastro e Login")

# Abas de Login e Cadastro
tab1, tab2 = st.tabs(["Login", "Novo Cadastro"])

# Aba de Login
with tab1:
    st.header("Acesse sua conta")
    
    email_login = st.text_input("Email:", key="login_email")
    senha_login = st.text_input("Senha:", type="password", key="login_senha")
    
    if st.button("Entrar", type="primary", key="btn_login"):
        if email_login and senha_login:
            sucesso, usuario = autenticar_usuario(email_login, senha_login)
            if sucesso:
                st.success(f"✅ Login realizado com sucesso!")
                st.info(f"Bem-vindo, {usuario['nome_completo']}! 🔄 Carregando chat...")
                st.session_state.usuario_logado = usuario
                st.balloons()
                # O gerenciador automaticamente vai trocar para o chat
                st.rerun()
            else:
                st.error("❌ Email ou senha incorretos.")
        else:
            st.warning("⚠️ Preencha todos os campos.")

# Aba de Cadastro
with tab2:
    st.header("Crie sua conta")
    
    nome = st.text_input("Nome completo:")
    email = st.text_input("Email institucional:")
    
    col1, col2 = st.columns(2)
    with col1:
        senha = st.text_input("Senha:", type="password")
    with col2:
        confirma_senha = st.text_input("Confirme a senha:", type="password")
    
    # Campos específicos para estudante (fixo)
    ra = st.text_input("RA (Registro Acadêmico):")
    curso = st.selectbox(
        "Curso:",
        options=[
            "Administração", "Ciência da Computação", "Direito", 
            "Engenharia de Computação", "Sistemas de Informação"
        ]
    )
    
    if st.button("Cadastrar", type="primary"):
        if not nome or not email or not senha:
            st.error("Preencha todos os campos obrigatórios.")
        elif senha != confirma_senha:
            st.error("As senhas não coincidem.")
        else:
            sucesso, mensagem = cadastrar_usuario(
                nome, email, senha, "estudante",
                ra=ra, curso=curso, departamento=None
            )
            
            if sucesso:
                st.success("✅ Cadastro realizado com sucesso! Você já pode fazer login.")
            else:
                st.error(f"❌ Erro no cadastro: {mensagem}")

# SEÇÃO SUBSTITUÍDA - Exibição após login simplificada
if "usuario_logado" in st.session_state:
    # Mostrar sucesso e aguardar o gerenciador fazer a troca
    st.success(f"✅ Usuário autenticado: {st.session_state.usuario_logado['nome_completo']}")
    st.info("🔄 Redirecionando para o chat...")
    
    # Opcional: mostrar dados do usuário brevemente
    with st.expander("👤 Seus dados"):
        st.write(f"**Nome:** {st.session_state.usuario_logado['nome_completo']}")
        st.write(f"**Email:** {st.session_state.usuario_logado['email']}")
        st.write(f"**Tipo:** {st.session_state.usuario_logado['tipo_usuario'].title()}")
    
    # Botão de logout caso precise
    if st.button("🚪 Fazer Logout"):
        st.session_state.clear()
        st.rerun()
    
    # O gerenciador já vai automaticamente para o chat
    st.stop()  # Para não processar mais nada
import streamlit as st
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime
import pymongo
import asyncio
from agent import ConversaComMemoria, setup_agent  # Importar a nova classe e função

# Carregar variáveis de ambiente
load_dotenv()

url_mongo = os.getenv("MONGO_URL")

# Configuração da conexão com MongoDB
def conectar_mongodb():
    client = pymongo.MongoClient(url_mongo)
    db = client["chatbot_puc"]
    return db

# Função para salvar mensagem no histórico
def salvar_mensagem_historico(chat_id, user_id, user_message, ai_message):
    try:
        db = conectar_mongodb()
        colecao_historico = db["historico_conversas"]
        
        documento_historico = {
            "timestamp": datetime.utcnow(),
            "chatId": chat_id,
            "userId": user_id,
            "userMessage": user_message,
            "AiMessage": ai_message,
            "deleted": False
        }
        
        resultado = colecao_historico.insert_one(documento_historico)
        return True, str(resultado.inserted_id)
    except Exception as e:
        st.error(f"Erro ao salvar histórico: {str(e)}")
        return False, str(e)

# Função para carregar histórico de chats do usuário
def carregar_chats_usuario(user_id):
    try:
        db = conectar_mongodb()
        colecao_historico = db["historico_conversas"]
        
        # Buscar todas as conversas do usuário que não foram deletadas
        conversas = colecao_historico.find({
            "userId": user_id,
            "$or": [
                {"deleted": {"$exists": False}},
                {"deleted": False}
            ]
        }).sort("timestamp", 1)
        
        chats_recuperados = {}
        
        for conversa in conversas:
            chat_id = conversa["chatId"]
            
            # Se o chat ainda não existe, criar estrutura
            if chat_id not in chats_recuperados:
                chats_recuperados[chat_id] = {
                    "id": chat_id,
                    "name": f"Chat {len(chats_recuperados) + 1}",
                    "messages": [],
                    "created_at": conversa["timestamp"].strftime("%d/%m/%Y %H:%M")
                }
            
            # Adicionar mensagens na ordem cronológica
            chat_messages = chats_recuperados[chat_id]["messages"]
            
            # Adicionar mensagem do usuário
            chat_messages.append({
                "role": "user", 
                "content": conversa["userMessage"]
            })
            
            # Adicionar resposta da IA
            chat_messages.append({
                "role": "assistant", 
                "content": conversa["AiMessage"]
            })
        
        # Renomear chats baseado no primeiro título de cada conversa
        for i, (chat_id, chat_data) in enumerate(chats_recuperados.items()):
            if chat_data["messages"]:
                # Usar primeiras palavras da primeira mensagem como nome
                primeira_mensagem = chat_data["messages"][0]["content"]
                nome_chat = primeira_mensagem[:30] + "..." if len(primeira_mensagem) > 30 else primeira_mensagem
                chat_data["name"] = nome_chat
            else:
                chat_data["name"] = f"Chat {i + 1}"
        
        return chats_recuperados
        
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {str(e)}")
        return {}

# Função para criar novo chat
def create_new_chat():
    chat_id = str(uuid.uuid4())[:8]
    chat_name = f"Chat {len(st.session_state.chats) + 1}"
    new_chat = {
        "id": chat_id,
        "name": chat_name,
        "messages": [],
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    st.session_state.chats[chat_id] = new_chat
    st.session_state.current_chat_id = chat_id
    
    # Limpar histórico do bot para novo chat
    if "conversa_bot" in st.session_state:
        st.session_state.conversa_bot.limpar_historico()
    
    return chat_id

# Função para deletar chat
def delete_chat(chat_id):
    try:
        db = conectar_mongodb()
        colecao_historico = db["historico_conversas"]
        
        # Mark all messages of this chat as deleted
        colecao_historico.update_many(
            {"chatId": chat_id},
            {"$set": {"deleted": True}}
        )
        
        # Remove from local session state
        if len(st.session_state.chats) > 1:
            del st.session_state.chats[chat_id]
            # If deleted chat was current, switch to another
            if st.session_state.current_chat_id == chat_id:
                st.session_state.current_chat_id = list(st.session_state.chats.keys())[0]
        else:
            # If it's the last chat, just clear messages and mark as deleted
            st.session_state.chats[chat_id]["messages"] = []
            
        # Limpar histórico do bot quando deletar chat
        if "conversa_bot" in st.session_state:
            st.session_state.conversa_bot.limpar_historico()
            
    except Exception as e:
        st.error(f"Erro ao deletar conversa: {str(e)}")

st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:hidden;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
        
        .chat-item {
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            border: 1px solid #ddd;
            cursor: pointer;
        }
        
        .chat-item-active {
            background-color: #e6f3ff;
            border-color: #4CAF50;
        }
        
        .chat-item:hover {
            background-color: #f5f5f5;
        }
        
        .chat-delete-btn {
            float: right;
            color: #ff4444;
            font-size: 12px;
        }
    </style>
""", unsafe_allow_html=True)

if "usuario_logado" not in st.session_state:
    st.error("❌ Erro: Usuário não autenticado!")
    st.stop()

# Inicializar estado dos chats
if "chats" not in st.session_state:
    # Tentar carregar chats existentes do usuário
    user_id = str(st.session_state.usuario_logado['_id'])
    chats_carregados = carregar_chats_usuario(user_id)
    
    if chats_carregados:
        st.session_state.chats = chats_carregados
        # Definir o chat mais recente como atual
        st.session_state.current_chat_id = list(chats_carregados.keys())[-1]
        st.success(f"✅ {len(chats_carregados)} conversa(s) recuperada(s)!")
    else:
        st.session_state.chats = {}
    
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# Se não há chats, criar o primeiro
if not st.session_state.chats:
    create_new_chat()
    st.info("💬 Nova conversa criada!")

# Inicializar o agent usando a nova classe
if "conversa_bot" not in st.session_state:
    st.session_state.conversa_bot = setup_agent(st.session_state.usuario_logado)

bot = st.session_state.conversa_bot

# ÚNICA seção de sidebar - consolidar tudo aqui
with st.sidebar:
    # Informações do usuário logado
    st.success(f"👤 **{st.session_state.usuario_logado['nome_completo']}**")
    st.caption(f"📧 {st.session_state.usuario_logado['email']}")
    st.caption(f"👨‍🎓 {st.session_state.usuario_logado['tipo_usuario'].title()}")
    
    if st.button("🚪 Logout", use_container_width=True, type="secondary"):
        st.session_state.clear()
        st.success("Logout realizado com sucesso!")
        st.rerun()
    
    st.markdown("---")
    
    # Gerenciamento de conversas
    st.header("💬 Conversas")
    
    # Botão para criar novo chat
    if st.button("➕ Nova Conversa", use_container_width=True):
        create_new_chat()
        st.rerun()
    
    st.markdown("---")
    
    # Lista de chats
    for chat_id, chat_data in st.session_state.chats.items():
        is_current = chat_id == st.session_state.current_chat_id
        
        chat_container = st.container()
        
        with chat_container:
            col1, col2 = st.columns([4, 1])
            
            with col1:
                if st.button(
                    chat_data["name"], 
                    key=f"select_{chat_id}",
                    use_container_width=True,
                    type="primary" if is_current else "secondary"
                ):
                    st.session_state.current_chat_id = chat_id
                    # Limpar histórico do bot ao trocar de chat
                    st.session_state.conversa_bot.limpar_historico()
                    st.rerun()
            
            with col2:
                if st.button(
                    "🗑️", 
                    key=f"delete_{chat_id}",
                    help="Deletar conversa"
                ):
                    delete_chat(chat_id)
                    st.rerun()
        
        st.caption(f"📅 {chat_data['created_at']}")
        st.markdown("---")
    
    # Seção de informações
    st.header("ℹ️ Sobre")
    st.write("Este assistente pode ajudar com:")
    st.write("• Informações do manual do aluno")
    st.write("• Perguntas frequentes")

# Área principal do chat
st.title("🤖 Assistente da PUC Campinas")

# Obter chat atual
current_chat = st.session_state.chats.get(st.session_state.current_chat_id, {})
current_messages = current_chat.get("messages", [])

# Mostrar nome do chat atual
if current_chat:
    st.write(f"💬 **{current_chat['name']}**")
    
    # Opção para renomear chat
    with st.expander("✏️ Renomear conversa"):
        new_name = st.text_input("Novo nome:", value=current_chat['name'])
        if st.button("Salvar nome"):
            st.session_state.chats[st.session_state.current_chat_id]["name"] = new_name
            st.rerun()

st.write("Olá! Sou seu assistente. Como posso ajudar?")

# Exibir mensagens do chat atual
for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input do usuário
if prompt := st.chat_input("Digite sua pergunta sobre a PUC Campinas..."):
    # Adicionar mensagem do usuário ao histórico do chat atual
    current_messages.append({"role": "user", "content": prompt})
    st.session_state.chats[st.session_state.current_chat_id]["messages"] = current_messages
    
    # Exibir mensagem do usuário
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Gerar resposta do assistente
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                # Chamada síncrona simples - SEM asyncio.run() ou await
                response = bot.conversar(prompt)
                st.markdown(response)
                
                # Adicionar resposta ao histórico do chat atual
                current_messages.append({"role": "assistant", "content": response})
                st.session_state.chats[st.session_state.current_chat_id]["messages"] = current_messages
                
                # Salvar no banco de dados
                user_id = str(st.session_state.usuario_logado['_id'])
                chat_id = st.session_state.current_chat_id
                
                sucesso, resultado = salvar_mensagem_historico(
                    chat_id=chat_id,
                    user_id=user_id,
                    user_message=prompt,
                    ai_message=response
                )
                
                if not sucesso:
                    st.warning("Mensagem salva localmente, mas houve problema ao sincronizar com o servidor.")
                
            except Exception as e:
                error_msg = f"Desculpe, ocorreu um erro: {str(e)}"
                st.error(error_msg)
                current_messages.append({"role": "assistant", "content": error_msg})
                st.session_state.chats[st.session_state.current_chat_id]["messages"] = current_messages
                
                # Salvar erro no banco também
                user_id = str(st.session_state.usuario_logado['_id'])
                chat_id = st.session_state.current_chat_id
                
                salvar_mensagem_historico(
                    chat_id=chat_id,
                    user_id=user_id,
                    user_message=prompt,
                    ai_message=error_msg
                )

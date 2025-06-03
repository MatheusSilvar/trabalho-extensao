# 🎓 ChatBot PUC Campinas

Um assistente virtual inteligente desenvolvido para responder dúvidas frequentes sobre a **PUC Campinas**, oferecendo informações sobre cursos, vestibular, estrutura, localização, formas de ingresso e serviços da universidade.

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Como Executar](#-como-executar)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [APIs e Integrações](#-apis-e-integrações)
- [Contribuição](#-contribuição)

## ✨ Funcionalidades

### 🔐 Sistema de Autenticação
- **Cadastro de usuários** com validação de email institucional
- **Login seguro** com hash de senhas
- **Sessão persistente** com informações do usuário

### 💬 Chat Inteligente
- **Assistente IA** especializado em informações da PUC Campinas
- **Múltiplas conversas** - criação, gerenciamento e histórico
- **Personalização** - respostas adaptadas ao perfil do usuário
- **Histórico persistente** - conversas salvas no banco de dados

### 🎯 Especialidades do Assistente
- Informações sobre **cursos e vestibular**
- **Manual do aluno** e regulamentos
- **Estrutura e localização** dos campi
- **Formas de ingresso** e processos seletivos
- **Serviços oferecidos** pela universidade

## 🛠 Tecnologias Utilizadas

### Frontend
- **Streamlit** - Interface web interativa
- **streamlit-chat** - Componentes de chat

### Backend & IA
- **Python 3.8+** - Linguagem principal
- **Pydantic AI** - Framework para agentes de IA
- **Google Gemini** - Modelo de linguagem (gemini-2.0-flash)
- **OpenAI** - Embeddings para RAG (opcional)
- **Pinecone** - Banco vetorial para RAG (opcional)

### Banco de Dados
- **MongoDB** - Armazenamento de usuários e conversas
- **PyMongo** - Driver Python para MongoDB

### Outras Dependências
- **python-dotenv** - Gerenciamento de variáveis de ambiente
- **logfire** - Monitoramento e logging

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Python 3.8 ou superior**
- **pip** (gerenciador de pacotes Python)
- **MongoDB** (local ou na nuvem)
- **Git** (para clonar o repositório)

### Contas e APIs Necessárias
- **Google AI Studio** - Para obter a chave da API do Gemini
- **MongoDB Atlas** ou instância local do MongoDB

## 🚀 Instalação

### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/projeto-integrador.git
cd projeto-integrador
```

### 2. Crie um Ambiente Virtual
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instale as Dependências
```bash
pip install -r requirements.txt
```

## ⚙️ Configuração

### 1. Configurar Variáveis de Ambiente

Copie o arquivo de exemplo e configure suas variáveis:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# API do Google Gemini
GEMINI_API_KEY=sua_chave_do_gemini_aqui

# MongoDB (local ou Atlas)
MONGO_URL=mongodb://localhost:27017/
# OU para MongoDB Atlas:
# MONGO_URL=mongodb+srv://usuario:senha@cluster.mongodb.net/

# Opcional: Para funcionalidades RAG
OPENAI_API_KEY=sua_chave_openai_aqui
PINECONE_API_KEY=sua_chave_pinecone_aqui
```

### 2. Como Obter as Chaves de API

#### Google Gemini API Key
1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada

#### MongoDB (Opções)

**Opção A: MongoDB Local**
```bash
# Instalar MongoDB localmente
# Windows: Baixe do site oficial
# Ubuntu/Debian:
sudo apt-get install mongodb

# Iniciar serviço
sudo systemctl start mongodb
```

**Opção B: MongoDB Atlas (Recomendado)**
1. Acesse [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Crie uma conta gratuita
3. Crie um cluster
4. Configure acesso de rede (0.0.0.0/0 para desenvolvimento)
5. Crie um usuário de banco de dados
6. Copie a string de conexão

### 3. Configurar MongoDB

O sistema criará automaticamente:
- Database: `chatbot_puc`
- Collections: `usuarios`, `historico_conversas`

## ▶️ Como Executar

### 1. Ativar Ambiente Virtual
```bash
# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

### 2. Executar a Aplicação
```bash
streamlit run gerenciador.py
```

### 3. Acessar a Aplicação
- Abra seu navegador
- Acesse: `http://localhost:8501`

## 📁 Estrutura do Projeto

```
projeto-integrador/
├── 📄 gerenciador.py          # Ponto de entrada principal
├── 🔐 trabalho.py             # Sistema de autenticação
├── 💬 chatUI.py               # Interface do chat
├── 🤖 agent.py                # Agente de IA e lógica de conversação
├── 🗄️ banco.py                # Configuração do banco (simples)
├── 🎯 rag.txt                 # Sistema RAG (opcional)
├── 🎨 UI.py                   # Componentes de UI (teste)
├── 📋 requirements.txt        # Dependências Python
├── ⚙️ .env.example            # Exemplo de configuração
├── 🚫 .env                    # Suas configurações (não commitado)
├── 📖 README.md               # Este arquivo
└── 🗂️ __pycache__/            # Cache Python
```

### Descrição dos Arquivos Principais

#### `gerenciador.py`
- **Função**: Orquestrador principal da aplicação
- **Responsabilidade**: Gerencia o fluxo entre login e chat

#### `trabalho.py`
- **Função**: Sistema completo de autenticação
- **Funcionalidades**: Cadastro, login, validação de emails institucionais

#### `chatUI.py`
- **Função**: Interface principal do chat
- **Funcionalidades**: Conversas múltiplas, histórico, sidebar

#### `agent.py`
- **Função**: Núcleo da inteligência artificial
- **Responsabilidade**: Processamento de mensagens, memória de conversação

## 🔗 APIs e Integrações

### Google Gemini
- **Modelo**: `gemini-2.0-flash`
- **Uso**: Processamento de linguagem natural
- **Configuração**: Via `GoogleGLAProvider`

### MongoDB
- **Database**: `chatbot_puc`
- **Collections**:
  - `usuarios`: Dados de cadastro e autenticação
  - `historico_conversas`: Mensagens e conversas

### Logfire (Monitoramento)
- **Função**: Logging e observabilidade
- **Instrumentação**: Automática para Pydantic AI

## 🎯 Fluxo de Uso

### 1. Primeiro Acesso
1. Usuário acessa a aplicação
2. Sistema exibe tela de login/cadastro
3. Usuário se cadastra com email institucional
4. Sistema valida e salva no MongoDB

### 2. Login e Chat
1. Usuário faz login
2. Sistema carrega histórico de conversas
3. Usuário pode criar novas conversas ou continuar existentes
4. Assistente responde com base no contexto da PUC Campinas

### 3. Funcionalidades do Chat
- **Nova conversa**: Cria uma nova thread de chat
- **Histórico**: Todas as mensagens são salvas
- **Personalização**: Respostas adaptadas ao perfil do usuário
- **Múltiplas conversas**: Gerenciamento de várias threads

## 🐛 Solução de Problemas

### Erro de Conexão com MongoDB
```bash
# Verificar se MongoDB está rodando
mongo --version

# Para MongoDB Atlas, verificar:
# 1. String de conexão correta
# 2. Whitelist de IP configurado
# 3. Usuário e senha corretos
```

### Erro de API Key do Gemini
```bash
# Verificar se a chave está no .env
cat .env | grep GEMINI

# Testar a chave diretamente
curl -H "Content-Type: application/json" \
     -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' \
     "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=SUA_CHAVE"
```

### Problemas com Dependências
```bash
# Atualizar pip
python -m pip install --upgrade pip

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

## 🚀 Como Executar em Produção

### 1. Usando Docker (Recomendado)
```dockerfile
# Dockerfile básico
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "gerenciador.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 2. Deploy Manual
```bash
# Configurar variáveis de produção
export GEMINI_API_KEY="sua_chave_producao"
export MONGO_URL="sua_url_producao"

# Executar com configurações de produção
streamlit run gerenciador.py --server.port=8501 --server.address=0.0.0.0
```

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👥 Equipe

- **Desenvolvedor Principal**: [Seu Nome]
- **Universidade**: PUC Campinas
- **Projeto**: Integrador

## 📞 Suporte

Para dúvidas ou problemas:
- 📧 Email: seu.email@puc-campinas.edu.br
- 🌐 Site: [PUC Campinas](https://www.puc-campinas.edu.br/)

---

⭐ **Se este projeto foi útil, considere dar uma estrela no GitHub!**

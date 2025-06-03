from dotenv import load_dotenv
import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from pydantic_ai.messages import ModelMessagesTypeAdapter
from pydantic_core import to_jsonable_python
import logfire
import json
from datetime import datetime

import asyncio

# Load environment variables
load_dotenv()

#inicializacao do logfire
logfire.configure()  
logfire.instrument_pydantic_ai()

# Prompt do assistente
PROMPT = '''
Você é um assistente virtual especializado em responder dúvidas frequentes sobre a **PUC Campinas**. Forneça respostas claras, objetivas e atualizadas sobre:  

- Cursos  
- Vestibular  
- Estrutura  
- Localização  
- Formas de ingresso  
- Contato  
- Serviços oferecidos pela universidade  

Caso a pergunta seja fora do escopo ou você não saiba a resposta, oriente o usuário a consultar o site oficial da PUC Campinas ou entrar em contato com a central de atendimento, enviando o seguinte link:  
 https://www.puc-campinas.edu.br/

Forneça uma experiência personalizada, utilize as informações que você tem do usuário ao seu favor. Chame o usuário pelo nome quando possível e utilizando uma linguagem amigável.

---

## Perguntas frequentes e respostas:

### 1. Qual é a frequência mínima exigida para aprovação nas disciplinas?  
A frequência mínima obrigatória é de **75%** das aulas ministradas e/ou atividades realizadas em cada disciplina.  

---

### 2. Como posso solicitar aproveitamento de estudos ou dispensa de disciplinas?  
Você pode solicitar o aproveitamento de estudos ou a dispensa de disciplinas por meio da **Central de Atendimento ao Aluno (CAA)**, acessando a **Área Logada do Aluno** no Portal da Universidade.  

---

### 3. Onde encontro o calendário acadêmico e informações sobre o cotidiano universitário?  
O **Manual do Aluno da Graduação** contém o calendário acadêmico e diversas informações sobre o cotidiano na PUC-Campinas. Ele está disponível no **site oficial da universidade**.  

---

## Educação Digital (EAD)

### 4. Os cursos de Educação Digital da PUC-Campinas são totalmente a distância?  
Sim, os cursos de Educação Digital são **totalmente a distância**, sem encontros presenciais.  

---

### 5. O diploma de um curso EAD tem a mesma validade que o presencial?  
Sim, os diplomas de cursos a distância reconhecidos possuem a **mesma validade** que os presenciais, conforme legislação vigente.  

---

### 6. Qual é a dedicação exigida em um curso de Educação Digital?  
Os cursos a distância exigem **muita dedicação**, demandando tempo e comprometimento semelhantes ou até maiores que os cursos presenciais.  

---

## Pós-Graduação e Certificados

### 7. Após o pagamento, em quanto tempo recebo acesso ao Ambiente Virtual de Aprendizagem?  
Em até **2 horas** após o pagamento, você receberá os dados de acesso à plataforma de estudos pelo **e-mail cadastrado**. Se o pagamento for via **boleto**, os dados serão enviados em até **48 horas**.  

---

### 8. Como é o certificado dos cursos de Pós-Graduação oferecidos em parceria com a PUCPR?  
Os certificados dos cursos de Pós-Graduação em parceria com a **PUCPR** seguem os **padrões de qualidade e reconhecimento** das instituições envolvidas.  

---

## Infraestrutura e Serviços

### 9. Posso utilizar os espaços físicos da PUC-Campinas sendo aluno de curso a distância?  
Sim, os **campi da PUC-Campinas** estão disponíveis para **todos os alunos**, proporcionando experiências de aprendizagem e oportunidades de networking.  

---

### 10. Quais serviços posso solicitar na Central de Atendimento ao Aluno (CAA)?  
Na **CAA**, você pode solicitar:  

- Atualização cadastral  
- Aproveitamento de estudos  
- Emissão de documentos acadêmicos e financeiros  
- Entre outros serviços  

'''

class ConversaComMemoria:
    """Gerenciador de conversa com memória usando pydantic-ai"""
    
    def __init__(self, estado_sessao: dict):
        self.estado_sessao = estado_sessao
        self.historico_mensagens = []
        self.agent = self._criar_agente()
        self._loop = None
    
    def _criar_agente(self):
        """Cria o agente com prompt personalizado"""
        prompt_personalizado = self._criar_prompt_personalizado()
        
        modelo = GeminiModel(
            'gemini-2.0-flash', 
            provider=GoogleGLAProvider(api_key=os.getenv("GEMINI_API_KEY"))
        )
        
        return Agent(  
            model=modelo,
            output_retries=2,
            output_type=str,
            system_prompt=prompt_personalizado,
        )
    
    def _criar_prompt_personalizado(self):
        """Cria prompt personalizado com informações do usuário"""
        nome = self.estado_sessao.get('nome_completo', 'Usuário')
        tipo_usuario = self.estado_sessao.get('tipo_usuario', 'estudante')
        curso = self.estado_sessao.get('curso', 'Não informado')
        ra = self.estado_sessao.get('ra', 'Não informado')
        
        prompt_personalizado = f"""{PROMPT}

        Informações do usuário:
        - Nome: {nome}
        - Tipo de usuário: {tipo_usuario.title()}
        - RA: {ra}
        - Curso: {curso}
        """
        return prompt_personalizado
    
    def _get_or_create_loop(self):
        """Obtém ou cria um loop de eventos"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("Loop is closed")
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop
    
    def conversar(self, mensagem_usuario: str):
        """Processa mensagem do usuário mantendo o histórico"""
        try:
            loop = self._get_or_create_loop()
            
            # Executa o agente de forma síncrona
            resultado = loop.run_until_complete(
                self.agent.run(
                    mensagem_usuario, 
                    message_history=self.historico_mensagens,
                )
            )
            
            # Usa o histórico atualizado do resultado
            self.historico_mensagens = resultado.all_messages()
            
            return resultado.data
        
        except Exception as e:
            return f"Erro ao processar mensagem: {str(e)}"
    
    def limpar_historico(self):
        """Limpa o histórico de mensagens"""
        self.historico_mensagens = []
    
    def obter_historico_formatado(self):
        """Retorna o histórico formatado para exibição"""
        if not self.historico_mensagens:
            return "📝 Nenhuma mensagem no histórico"
        
        historico_formatado = []
        for i, msg in enumerate(self.historico_mensagens, 1):
            # Verifica o tipo de mensagem de forma mais robusta
            if hasattr(msg, 'content'):
                # Determina o papel baseado no tipo da mensagem ou role
                if hasattr(msg, 'role'):
                    if msg.role == 'user':
                        papel = "Usuário"
                    elif msg.role == 'assistant':
                        papel = "Assistente"
                    else:
                        papel = "Sistema"
                else:
                    # Fallback baseado no tipo
                    tipo_msg = type(msg).__name__.lower()
                    if 'user' in tipo_msg:
                        papel = "Usuário"
                    elif 'model' in tipo_msg or 'assistant' in tipo_msg:
                        papel = "Assistente"
                    else:
                        papel = "Sistema"
                
                conteudo = str(msg.content)
                if len(conteudo) > 100:
                    conteudo = conteudo[:100] + "..."
                historico_formatado.append(f"{i}. {papel}: {conteudo}")
        
        return "\n".join(historico_formatado)

def setup_agent(usuario_logado):
    """Função para configurar e retornar uma instância da ConversaComMemoria"""
    return ConversaComMemoria(usuario_logado)
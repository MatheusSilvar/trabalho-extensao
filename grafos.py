import networkx as nx
import matplotlib.pyplot as plt
import re
from collections import Counter
import streamlit as st

# Lista de palavras-chave específicas para PUC Campinas
LISTA_PALAVRAS_CHAVES = [
    # Cursos e áreas acadêmicas
    "curso", "cursos", "graduação", "pós-graduação", "mestrado", "doutorado",
    "engenharia", "direito", "medicina", "psicologia", "administração", "economia",
    "arquitetura", "design", "comunicação", "jornalismo", "publicidade", "marketing",
    
    # Processo seletivo e ingresso
    "vestibular", "enem", "sisu", "prouni", "fies", "nota", "notas", "prova", "provas",
    "inscrição", "inscrições", "matrícula", "rematrícula", "transferência", "transferências",
    
    # Estrutura acadêmica
    "campus", "laboratório", "laboratórios", "biblioteca", "sala", "salas", "auditório",
    "restaurante", "cantina", "estacionamento", "quadra", "ginásio",
    
    # Ensino e aprendizagem
    "disciplina", "disciplinas", "matéria", "matérias", "professor", "professores",
    "aula", "aulas", "presencial", "ead", "online", "distância", "híbrido",
    "nota", "média", "frequência", "aprovação", "reprovação", "dp",
    
    # Documentos e serviços
    "histórico", "diploma", "certificado", "declaração", "atestado", "comprovante",
    "boleto", "mensalidade", "taxa", "desconto", "bolsa", "financiamento",
    
    # Apoio ao estudante
    "caa", "atendimento", "secretaria", "ouvidoria", "monitoria", "estágio", "tcc",
    "iniciação", "científica", "pesquisa", "extensão", "intercâmbio",
    
    # Tecnologia e sistemas
    "portal", "sistema", "login", "senha", "email", "plataforma", "ambiente", "virtual",
    
    # Localização e contato
    "campinas", "endereço", "telefone", "contato", "horário", "funcionamento",
    
    # Outros termos relevantes
    "aluno", "aluna", "estudante", "universitário", "acadêmico", "semestre", "período"
]

def limpar_texto(texto):
    """Remove pontuações e transforma em minúsculas"""
    return re.sub(r"[^\w\s]", "", texto.lower())

def extrair_palavras_chave(texto, lista_palavras):
    """Extrai palavras-chave do texto que estão na lista"""
    texto_limpo = limpar_texto(texto)
    palavras_texto = texto_limpo.split()
    return [palavra for palavra in palavras_texto if palavra in lista_palavras]

def criar_grafo_conversa(mensagens_chat, lista_palavras_chaves=None):
    """
    Cria um grafo a partir das mensagens do chat atual.
    Cada nó é uma palavra-chave e as arestas representam coocorrência na mesma mensagem.
    
    Args:
        mensagens_chat: lista de dicionários com 'role' e 'content'
        lista_palavras_chaves: lista de palavras-chave para filtrar (opcional)
    
    Returns:
        tuple: (grafo networkx.Graph, lista de palavras encontradas)
    """
    if lista_palavras_chaves is None:
        lista_palavras_chaves = LISTA_PALAVRAS_CHAVES
    
    G = nx.Graph()
    todas_palavras = []
    
    # Processar cada mensagem
    for mensagem in mensagens_chat:
        conteudo = mensagem.get("content", "")
        palavras_encontradas = extrair_palavras_chave(conteudo, lista_palavras_chaves)
        todas_palavras.extend(palavras_encontradas)
        
        # Adicionar nós e arestas baseados na coocorrência
        for i, palavra1 in enumerate(palavras_encontradas):
            G.add_node(palavra1)
            for j in range(i + 1, len(palavras_encontradas)):
                palavra2 = palavras_encontradas[j]
                if palavra1 != palavra2:
                    if G.has_edge(palavra1, palavra2):
                        G[palavra1][palavra2]['weight'] += 1
                    else:
                        G.add_edge(palavra1, palavra2, weight=1)
    
    return G, todas_palavras

def plotar_grafo_conversa(chat_messages):
    """
    Plota o grafo das palavras-chave da conversa atual usando Streamlit
    
    Args:
        chat_messages: lista de mensagens do chat atual
    """
    if not chat_messages:
        st.warning("⚠️ Nenhuma mensagem encontrada no chat atual!")
        return
    
    # Criar grafo
    G, palavras_encontradas = criar_grafo_conversa(chat_messages)
    
    if not G.nodes():
        st.warning("⚠️ Nenhuma palavra-chave relevante encontrada na conversa!")
        return
    
    # Estatísticas
    contador_palavras = Counter(palavras_encontradas)
    
    # Criar visualização
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Grafo de palavras-chave
    pos = nx.spring_layout(G, k=1, iterations=50)
    
    # Tamanho dos nós baseado na frequência
    node_sizes = [contador_palavras[node] * 300 for node in G.nodes()]
    
    # Espessura das arestas baseada no peso
    edge_weights = [G[u][v].get('weight', 1) for u, v in G.edges()]
    
    nx.draw(G, pos, ax=ax1, 
            with_labels=True, 
            node_color='lightblue',
            node_size=node_sizes,
            font_size=8,
            font_weight='bold',
            edge_color='gray',
            width=[w * 0.5 for w in edge_weights])
    
    ax1.set_title(f"Grafo de Palavras-chave\n({len(G.nodes())} termos encontrados)", 
                  fontsize=12, fontweight='bold')
    
    # Gráfico de barras das palavras mais frequentes
    palavras_top = contador_palavras.most_common(10)
    if palavras_top:
        palavras, frequencias = zip(*palavras_top)
        ax2.barh(range(len(palavras)), frequencias, color='lightcoral')
        ax2.set_yticks(range(len(palavras)))
        ax2.set_yticklabels(palavras)
        ax2.set_xlabel('Frequência')
        ax2.set_title('Top 10 Palavras-chave', fontsize=12, fontweight='bold')
        ax2.invert_yaxis()
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Mostrar estatísticas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Palavras-chave únicas", len(G.nodes()))
    with col2:
        st.metric("Conexões", len(G.edges()))
    with col3:
        st.metric("Total de ocorrências", len(palavras_encontradas))
    
    # Mostrar palavras mais relevantes
    if palavras_top:
        st.subheader("🔍 Palavras-chave mais relevantes:")
        for palavra, freq in palavras_top[:5]:
            st.write(f"• **{palavra}**: {freq} ocorrência(s)")

def obter_estatisticas_conversa(chat_messages):
    """
    Retorna estatísticas básicas da conversa
    
    Args:
        chat_messages: lista de mensagens do chat atual
    
    Returns:
        dict: dicionário com estatísticas
    """
    if not chat_messages:
        return {}
    
    G, palavras_encontradas = criar_grafo_conversa(chat_messages)
    contador_palavras = Counter(palavras_encontradas)
    
    return {
        "total_mensagens": len(chat_messages),
        "palavras_unicas": len(G.nodes()),
        "total_palavras_chave": len(palavras_encontradas),
        "conexoes": len(G.edges()),
        "palavra_mais_frequente": contador_palavras.most_common(1)[0] if contador_palavras else None,
        "top_5_palavras": contador_palavras.most_common(5)
    }

def exportar_dados_grafo(chat_messages, formato="json"):
    """
    Exporta dados do grafo em diferentes formatos
    
    Args:
        chat_messages: lista de mensagens do chat atual
        formato: "json", "csv" ou "txt"
    
    Returns:
        str: dados formatados
    """
    G, palavras_encontradas = criar_grafo_conversa(chat_messages)
    contador_palavras = Counter(palavras_encontradas)
    
    if formato == "json":
        import json
        dados = {
            "nos": list(G.nodes()),
            "arestas": list(G.edges()),
            "frequencias": dict(contador_palavras),
            "estatisticas": obter_estatisticas_conversa(chat_messages)
        }
        return json.dumps(dados, indent=2, ensure_ascii=False)
    
    elif formato == "csv":
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Palavra", "Frequencia"])
        for palavra, freq in contador_palavras.most_common():
            writer.writerow([palavra, freq])
        return output.getvalue()
    
    elif formato == "txt":
        resultado = "ANÁLISE DA CONVERSA\n"
        resultado += "=" * 50 + "\n\n"
        resultado += f"Total de palavras-chave únicas: {len(G.nodes())}\n"
        resultado += f"Total de conexões: {len(G.edges())}\n"
        resultado += f"Total de ocorrências: {len(palavras_encontradas)}\n\n"
        resultado += "PALAVRAS MAIS FREQUENTES:\n"
        resultado += "-" * 30 + "\n"
        for palavra, freq in contador_palavras.most_common(10):
            resultado += f"{palavra}: {freq} ocorrência(s)\n"
        return resultado
    
    return ""
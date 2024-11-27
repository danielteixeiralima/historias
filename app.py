import os
import openai
import requests
from docx import Document
from PIL import Image
from io import BytesIO
import pdfkit
import base64
import time
import html
import re
import tiktoken
import json
import logging

# Configurações da API da OpenAI
# Obtém a chave da API a partir da variável de ambiente

if not openai.api_key:
    raise ValueError("A chave da API da OpenAI não está definida. Defina a variável de ambiente 'OPENAI_API_KEY' com sua chave.")

# Configurações do wkhtmltopdf
caminho_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'  # Atualize este caminho se necessário
config = pdfkit.configuration(wkhtmltopdf=caminho_wkhtmltopdf)

# Pasta de saída para os PDFs
PASTA_PDFS = 'pdfs_gerados'
os.makedirs(PASTA_PDFS, exist_ok=True)

# Arquivo para armazenar o progresso
ARQUIVO_PROGRESSO = 'progresso.json'

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('processamento.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)


# Carregar o progresso anterior
if os.path.exists(ARQUIVO_PROGRESSO):
    with open(ARQUIVO_PROGRESSO, 'r', encoding='utf-8') as f:
        progresso = json.load(f)
        logging.info("Progresso carregado com sucesso.")
else:
    progresso = {}
    logging.info("Nenhum progresso anterior encontrado. Iniciando novo processamento.")

# Função para sanitizar nomes de arquivos
def sanitizar_nome_arquivo(nome):
    return re.sub(r'[\\/*?:"<>|]', "", nome)

# Função para carregar e converter imagens em base64
def carregar_imagem_base64(caminho_imagem):
    try:
        with open(caminho_imagem, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        logging.info(f"Imagem carregada: {caminho_imagem} (Base64 length: {len(encoded_string)})")
        return encoded_string
    except Exception as e:
        logging.error(f"Erro ao carregar a imagem {caminho_imagem}: {e}")
        return ""

# Função para carregar a logo em base64
def carregar_logo_base64(caminho_logo):
    try:
        logo_base64 = carregar_imagem_base64(caminho_logo)
        if not logo_base64:
            logging.warning(f"Logo {caminho_logo} não foi carregada corretamente.")
        else:
            logging.info(f"Logo carregada com sucesso: {caminho_logo}")
        return logo_base64
    except Exception as e:
        logging.error(f"Erro ao carregar a logo {caminho_logo}: {e}")
        return ""

# **Carregar as logos e converter para Base64**
# Atualize os caminhos das logos conforme necessário
caminho_logo_mopi = r'C:\Users\User\Downloads\livros\logo_Mopi_cor.png'
caminho_logo_inovai = r'C:\Users\User\Downloads\livros\logo.png'


logo_mopi_base64 = carregar_logo_base64(caminho_logo_mopi)
logo_inovai_base64 = carregar_logo_base64(caminho_logo_inovai)

# Usaremos a logo do Mopi como logo principal
logo_base64 = logo_mopi_base64

# Função para contar tokens usando tiktoken
def contar_tokens(texto, modelo="gpt-4o"):
    encoding = tiktoken.encoding_for_model(modelo)
    return len(encoding.encode(texto))








# Função para converter imagem PIL em base64
def image_to_base64(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    image_data = buffer.getvalue()
    buffer.close()
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    return image_base64















import os
import logging
import json
from docx import Document
import openai

# Configuração básica do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Dicionário para acompanhar o progresso do processamento
progresso = {}

ARQUIVO_PROGRESSO = "progresso.json"

def salvar_progresso(progresso):
    with open(ARQUIVO_PROGRESSO, 'w', encoding='utf-8') as f:
        json.dump(progresso, f, ensure_ascii=False, indent=4)
    logging.info("Progresso salvo com sucesso.")



def criar_estrutura_pastas(origem, destino):
    print(f"Origem: {origem}")
    print(f"Destino: {destino}")
    
    if not os.path.exists(origem):
        logging.error(f"O caminho de origem não existe: {origem}")
        print(f"Erro: O caminho de origem não existe: {origem}")
        return
    
    try:
        turmas = os.listdir(origem)
    except Exception as e:
        logging.error(f"Erro ao listar o diretório de origem: {e}")
        print(f"Erro ao listar o diretório de origem: {e}")
        return
    
    for turma in turmas:
        print(f"Turma encontrada: {turma}")
        caminho_turma_origem = os.path.join(origem, turma)
        caminho_turma_destino = os.path.join(destino, turma)
        print(f"Caminho de origem da turma: {caminho_turma_origem}")
        print(f"Caminho de destino da turma: {caminho_turma_destino}")
        
        if os.path.isdir(caminho_turma_origem):
            if not os.path.exists(caminho_turma_destino):
                try:
                    print(f"Criando diretório para a turma: {caminho_turma_destino}")
                    os.makedirs(caminho_turma_destino)
                    logging.info(f"Criada a pasta: {caminho_turma_destino}")
                except Exception as e:
                    logging.error(f"Erro ao criar a pasta {caminho_turma_destino}: {e}")
                    print(f"Erro ao criar a pasta {caminho_turma_destino}: {e}")

def processar_arquivos_na_pasta(origem, destino):
    pasta_historias = origem
    pasta_pdfs = destino
    print("CCC")
    
    criar_estrutura_pastas(pasta_historias, pasta_pdfs)
    print("DDD")
    
    logging.info(f"Processando arquivos Word na pasta: {pasta_historias}")
    try:
        turmas_historias = os.listdir(pasta_historias)
    except Exception as e:
        logging.error(f"Erro ao listar as turmas em {pasta_historias}: {e}")
        return

    for turma in turmas_historias:
        caminho_turma = os.path.join(pasta_historias, turma)
        if not os.path.isdir(caminho_turma):
            continue
        try:
            arquivos = os.listdir(caminho_turma)
        except Exception as e:
            logging.error(f"Erro ao listar arquivos na turma {turma}: {e}")
            continue
        for arquivo in arquivos:
            if arquivo.endswith('.docx'):
                caminho_completo = os.path.join(caminho_turma, arquivo)
                nome_arquivo = os.path.basename(caminho_completo)
                student_name = os.path.splitext(nome_arquivo)[0]
                nome_pdf = f"{student_name}.pdf"
                caminho_pasta_pdf = os.path.join(pasta_pdfs, turma)
                caminho_pdf = os.path.join(caminho_pasta_pdf, nome_pdf)
                if not os.path.exists(caminho_pasta_pdf):
                    try:
                        os.makedirs(caminho_pasta_pdf)
                    except Exception as e:
                        logging.error(f"Erro ao criar a pasta {caminho_pasta_pdf}: {e}")
                        continue
                try:
                    turmas_pdfs = os.listdir(pasta_pdfs)
                except Exception as e:
                    logging.error(f"Erro ao listar as turmas em {pasta_pdfs}: {e}")
                    continue
                for turma_pdf in turmas_pdfs:
                    caminho_turma_pdf = os.path.join(pasta_pdfs, turma_pdf)
                    if os.path.exists(os.path.join(caminho_turma_pdf, nome_pdf)):
                        logging.info(f"O arquivo PDF '{nome_pdf}' já existe. Pulando o processamento.")
                        break
                else:
                    status = progresso.get(nome_arquivo, 'pendente')
                    if status == 'concluído':
                        logging.info(f"Arquivo '{nome_arquivo}' já processado. Pulando para o próximo.")
                        continue
                    elif status == 'em_progresso':
                        logging.info(f"Retomando processamento do arquivo '{nome_arquivo}'.")
                    else:
                        logging.info(f"Iniciando processamento do arquivo '{nome_arquivo}'.")
                    progresso[nome_arquivo] = 'em_progresso'
                    salvar_progresso(progresso)
                    try:
                        logging.info(f"Processando o arquivo '{nome_arquivo}'.")
                        titulo, partes_historia, imagens_base64 = formatar_como_livro_infantil(
                            arquivo_word=caminho_completo,
                            student_name=student_name,
                            caminho_pdf=caminho_pdf
                        )
                        if titulo:
                            logging.info(f"Livro '{titulo}' processado com sucesso. PDF gerado.")
                            progresso[nome_arquivo] = 'concluído'
                        else:
                            logging.error(f"Falha ao processar o arquivo '{arquivo}'.")
                            progresso[nome_arquivo] = 'erro'
                        salvar_progresso(progresso)
                    except Exception as e:
                        logging.error(f"Erro ao processar o arquivo '{arquivo}': {e}")
                        progresso[nome_arquivo] = 'erro'
                        salvar_progresso(progresso)
    logging.info("Processamento de todos os arquivos Word concluído.")



################################################################################################

# Função para gerar título e estilo das imagens usando GPT-4
def gerar_titulo_descricao_estilo(historia_texto):
    logging.info("Gerando título e estilo das imagens...")
    try:
        # Parte 1: Gerar Título
        prompt_titulo = (
            "Com base na história fornecida, crie um título cativante para um livro infantil. "
            "O título deve ser curto, direto e não deve incluir números. **Não use aspas ao redor do título.**\n\n"
            "História:\n"
            f"{historia_texto}\n\n"
            "Forneça apenas o título."
        )

        response_titulo = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system",
                 "content": "Você é um assistente especializado em criar títulos para histórias infantis."},
                {"role": "user",
                 "content": prompt_titulo}
            ],
            max_tokens=60
        )
        titulo = response_titulo['choices'][0]['message']['content'].strip().strip('"').strip("'")

        # Parte 2: Definir Estilo Visual
        prompt_estilo = (
            "Com base no título gerado e na história fornecida, defina um estilo visual apropriado para as ilustrações do livro infantil. "
            "O estilo deve ser totalmente animado, adequado para crianças de 6 a 8 anos e deve refletir o tom da história.\n\n"
            "Título:\n"
            f"{titulo}\n\n"
            "História:\n"
            f"{historia_texto}\n\n"
            "Descreva o estilo visual em poucas palavras."
        )

        response_estilo = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system",
                 "content": "Você é um assistente especializado em definir estilos visuais para ilustrações de livros infantis."},
                {"role": "user",
                 "content": prompt_estilo}
            ],
            max_tokens=60
        )
        estilo_imagem = response_estilo['choices'][0]['message']['content'].strip()

        logging.info(f"Título: {titulo}\nEstilo: {estilo_imagem}")
        return titulo, estilo_imagem
    except openai.error.APIError as e:
        logging.error(f"Erro na API: {e}")
        raise
    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado: {e}")
        raise


def gerar_html_capa(titulo, imagem_base64, logo_base64):
    logging.info(f"Gerando HTML da capa: {titulo}...")
    titulo_escapado = html.escape(titulo)
    html_content = f"""
    <div class='pagina-capa'>
        <style>
            @page {{
                size: A5;
                margin: 0.8in;
            }}
            body {{
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
            }}
            .pagina-capa {{
                page-break-after: always;
                position: relative;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100%;
            }}
            .conteudo-capa {{
                width: 100%;
                max-width: 595px;
                margin: 0 auto;
                position: relative;
                padding: 20px;
            }}
            .imagem-container-capa {{
                position: relative;
            }}
            .imagem-capa {{
                width: 100%;
                height: auto;
                display: block;
            }}
            .texto-sobre-imagem-capa {{
                position: absolute;
                top: 10%;
                width: 70%;
                left: 15%;
                text-align: center;
                font-size: 24px;
                color: #fff;
                background-color: rgba(0, 0, 0, 0.5);
                padding: 10px;
                border-radius: 10px;
            }}
            .logo-capa {{
                position: absolute;
                bottom: 10px;
                right: 10px;
                width: 35px;
                opacity: 1;
                z-index: 2;
            }}
        </style>
        <div class='conteudo-capa'>
            <div class='imagem-container-capa'>
                <img class='imagem-capa' src='data:image/png;base64,{imagem_base64}' alt='Capa'>
                <div class='texto-sobre-imagem-capa'>
                    <h1>{titulo_escapado}</h1>
                </div>
                <img class='logo-capa' src='data:image/png;base64,{logo_base64}' alt='Logo'>
            </div>
        </div>
    </div>
    """
    return html_content




def gerar_html_agradecimento(imagem_base64, logo_base64):
    logging.info("Gerando HTML da página de agradecimento com imagem de fundo...")

    texto_agradecimento = """
Querida família,

Recebam este mimo de fim de ano, preparado com muito carinho pela equipe do Mopi, especialmente para você e sua família. Esta história foi criada com o apoio da inteligência artificial, que nos ajudou a concentrar, organizar e formatar de forma mais rápida e eficiente as informações preciosas que vocês compartilharam conosco, junto com os dados que temos sobre nossos alunos, trazendo detalhes únicos que deram vida a cada narrativa.

Por ser uma ferramenta nova, a inteligência artificial ainda pode apresentar algumas inconsistências, e pedimos que levem isso em consideração. Esta é apenas uma degustação de um universo de possibilidades que o Mopi está enxergando com a chegada dessa revolução tecnológica.
Estamos empenhados em usar essas inovações para proporcionar jornadas cada vez mais customizadas e individualizadas, respeitando as necessidades de cada aluno e trazendo à tona sua melhor versão todos os dias.

Esperamos que essa história encha seus corações de alegria e reforce o nosso compromisso em oferecer experiências educacionais significativas e personalizadas.

Que em 2025 possamos viver experiências ainda mais especiais, únicas e, claro, individualizadas.

Obrigado por acreditar no nosso Jeito de Transformar Vidas.

Aproveitem e boa aventura!

Com carinho,
Família Mopi
    """

    # Processar o texto de agradecimento em parágrafos
    paragraphs = texto_agradecimento.strip().split('\n\n')
    formatted_text = ''.join(f'<p>{html.escape(paragraph.strip())}</p>' for paragraph in paragraphs)

    html_content = f"""
    <div class='pagina-agradecimento'>
        <style>
            @page {{
                size: A5;
                margin: 0.8in;
            }}
            body {{
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
            }}
            .pagina-agradecimento {{
                page-break-after: always;
                position: relative;
                display: flex;
                flex-direction: column;
                justify-content: flex-end;
                height: 100%;
            }}
            .conteudo-agradecimento {{
                width: 100%;
                max-width: 595px;
                margin: 0 auto;
                position: relative;
                padding: 20px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100%;
                text-align: center;
            }}
            .imagem-agradecimento {{
                position: absolute;
                bottom: 0;
                width: 100%;
                height: auto;
                opacity: 0.6;
            }}
            .texto-agradecimento {{
                position: absolute;
                bottom: 4%;
                left: 15%;
                width: 70%;
                text-align: center;
                font-size: 12px;
                color: #000;
                background-color: rgba(255, 255, 255, 0.8);
                padding: 10px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
                z-index: 1;
            }}
            .logo-mopi-agradecimento {{
                position: absolute;
                bottom: 10px;
                left: 10px;
                width: 35px;
                opacity: 1;
                z-index: 2;
            }}
        </style>
        <div class='conteudo-agradecimento'>
            <div class='imagem-container-agradecimento'>
                <img class='imagem-agradecimento' src='data:image/jpeg;base64,{imagem_base64}' alt='Agradecimento'>
                <div class='texto-agradecimento'>
                    {formatted_text}
                </div>
                <img class='logo-mopi-agradecimento' src='data:image/png;base64,{logo_base64}' alt='Logo Mopi'>
            </div>
        </div>
    </div>
    """
    return html_content





# Função para gerar a história infantil usando GPT-4
def gerar_historia(preferencias, interesses, caracteristicas, comprimento_max=3000):
    logging.info("Gerando a história infantil com base nas informações fornecidas...")

    prompt = (
        "Crie uma história encantadora e imaginativa de pelo menos duas páginas, voltada para uma criança, "
        "que seja rica em curiosidade e lições de vida. A narrativa deve ser lúdica e cheia de aventuras, "
        "aproveitando as informações específicas sobre a vida da criança, como suas preferências, interesses e "
        "características pessoais. É importante que a história traga mensagens inspiradoras e positivas, "
        "ensinando valores como amizade, coragem, empatia e resiliência. "
        "**Certifique-se de que a história tenha um início cativante, um meio envolvente e um final claro, satisfatório e coerente, que resolva todos os conflitos apresentados e não deixe pontas soltas.**\n\n"
        "Descreva a história com o máximo de detalhes, tornando-a rica e envolvente, e **escreva a história completa do começo ao fim**. "
        "No final da história, inclua uma conclusão que amarre todas as pontas soltas e ofereça um fechamento emocional satisfatório para a criança.\n\n"
        f"Preferências da criança: {preferencias}\n"
        f"Interesses da criança: {interesses}\n"
        f"Características pessoais: {caracteristicas}\n\n"
        "Certifique-se de que a narrativa não mencione os pais ou mães da criança, mantendo o foco nas aventuras e "
        "lições vividas pelos personagens da história. Crie um mundo cheio de cores, lugares mágicos e personagens "
        "divertidos para estimular a imaginação e o aprendizado da criança, de forma divertida e envolvente."

        
    )

    
    # Contar tokens do prompt
    tokens_prompt = contar_tokens(prompt)
    tokens_disponiveis = 8192 - tokens_prompt - 500  # Reservando 500 tokens de margem
    if comprimento_max > tokens_disponiveis:
        comprimento_max = tokens_disponiveis
        logging.info(f"Ajustando max_tokens para {comprimento_max} devido ao tamanho do prompt.")

    max_retries = 5
    retry_delay = 5  # Segundos

    for attempt in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system",
                     "content": "Você é um autor criativo especializado em histórias infantis personalizadas."},
                    {"role": "user",
                     "content": prompt}
                ],
                max_tokens=comprimento_max,
                temperature=0.7
            )
            historia = response['choices'][0]['message']['content'].strip()
            tokens_resposta = contar_tokens(historia)
            logging.info(f"Tokens na resposta: {tokens_resposta}")
            # Verificar e concluir a história, se necessário
            historia = verificar_final(historia)
            logging.info("História gerada com sucesso.")
            return historia
        except openai.error.RateLimitError as e:
            logging.error(f"Limite de taxa atingido: {e}")
            if attempt < max_retries - 1:
                logging.info(f"Tentando novamente em {retry_delay} segundos...")
                time.sleep(retry_delay)
                continue
            else:
                logging.error("Máximo de tentativas atingido. Abortando.")
                return ""
        except openai.error.APIError as e:
            logging.error(f"Erro na API da OpenAI: {e}")
            return ""
        except Exception as e:
            logging.error(f"Ocorreu um erro inesperado: {e}")
            return ""
        


# Função para verificar e concluir a história
def verificar_final(historia_texto):
    finais_satisfatorios = [
        'fim.',
        'final.',
        'conclusão.',
        'E viveram felizes para sempre.',
        'E assim terminaram suas aventuras.',
        'E todos viveram em harmonia.'
    ]
    if any(historia_texto.lower().strip().endswith(final.lower()) for final in finais_satisfatorios):
        return historia_texto
    else:
        logging.info("Final não satisfatório detectado. Solicitando conclusão ao modelo...")
        prompt_final = (
            "A história abaixo não possui um final claro e satisfatório. Por favor, conclua a história de forma que resolva todos os conflitos e ofereça um fechamento emocional para o leitor.\n\n"
            f"História:\n{historia_texto}\n\n"
            "Final:"
        )
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system",
                     "content": "Você é um autor de histórias infantis especializado em concluir narrativas de forma satisfatória."},
                    {"role": "user",
                     "content": prompt_final}
                ],
                max_tokens=500,
                temperature=0.7
            )
            finalizacao = response['choices'][0]['message']['content'].strip()
            return historia_texto + "\n" + finalizacao
        except Exception as e:
            logging.error(f"Erro ao tentar concluir a história: {e}")
            return historia_texto



# Função para quebrar a história em partes
def quebrar_historia_em_partes(historia_texto, num_partes=14):
    logging.info("Quebrando a história em partes sem quebrar frases...")
    # Divide o texto em sentenças usando expressões regulares
    sentence_endings = re.compile(r'(?<=[.!?])\s+')
    sentences = sentence_endings.split(historia_texto)
    total_sentences = len(sentences)
    sentences_per_part = total_sentences // num_partes
    extra_sentences = total_sentences % num_partes
    partes = []
    i = 0

    for parte_num in range(num_partes):
        inicio = i
        fim = i + sentences_per_part
        if extra_sentences > 0:
            fim += 1
            extra_sentences -= 1
        parte_sentences = sentences[inicio:fim]
        bloco = ' '.join(parte_sentences)
        partes.append(bloco)
        i = fim

    logging.info(f"História dividida em {len(partes)} partes.")
    return partes



def gerar_html_pagina(texto, imagem_base64, pagina_numero, logo_base64):
    logging.info(f"Gerando HTML da página interna {pagina_numero}...")

    # Processar o texto da história em parágrafos
    paragraphs = texto.strip().split('\n\n')
    formatted_text = ''.join(f'<p>{html.escape(paragraph.strip())}</p>' for paragraph in paragraphs)

    html_content = f"""
    <div class='pagina-interna'>
        <style>
            @page {{
                size: A5;
                margin: 0.8in;
            }}
            body {{
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
            }}
            .pagina-interna {{
                page-break-after: always;
                position: relative;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100%;
            }}
            .conteudo-interna {{
                width: 100%;
                max-width: 595px;
                margin: 0 auto;
                position: relative;
                padding: 20px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100%;
                text-align: center;
            }}
            .imagem-container-interna {{
                position: relative;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }}
            .imagem-interna {{
                width: 100%;
                height: auto;
                display: block;
            }}
            .texto-historia-interna {{
                position: absolute;
                bottom: 5%;
                width: 70%;
                left: 15%;
                text-align: center;
                font-size: 12px;
                color: #000;
                background-color: rgba(255, 255, 255, 0.7);
                padding: 10px;
                border-radius: 10px;
            }}
            .logo-mopi-interna {{
                position: absolute;
                bottom: 10px;
                left: 10px;
                width: 35px;
                opacity: 1;
                z-index: 2;
            }}
        </style>
        <div class='conteudo-interna'>
            <div class='imagem-container-interna'>
                <img class='imagem-interna' src='data:image/png;base64,{imagem_base64}' alt='Página {pagina_numero}'>
                <div class='texto-historia-interna'>
                    {formatted_text}
                </div>
                <img class='logo-mopi-interna' src='data:image/png;base64,{logo_base64}' alt='Logo Mopi'>
            </div>
        </div>
    </div>
    """
    return html_content



# Função para gerar prompts para imagens com base em partes da história e estilo
def gerar_prompt_para_parte(parte, estilo):
    logging.info(f"Gerando prompt para parte da história...")
    try:
        # Usar o GPT-4 para gerar uma descrição da cena
        prompt_gpt = (
            "Com base na seguinte parte da história, descreva detalhadamente uma cena para ser ilustrada em um livro infantil. "
            "A descrição deve ser visual, rica em detalhes e 100% animada, sem incluir qualquer texto ou diálogos.\n\n"
            "Parte da história:\n"
            f"{parte}\n\n"
            f"Estilo visual desejado: {estilo}\n\n"
            "Instruções:\n"
            "- A descrição deve focar exclusivamente nas paisagens, cenários e elementos naturais ou arquitetônicos presentes na cena.\n"
            "- Evite mencionar qualquer tipo de personagem ou ação específica.\n"
            "- A descrição deve ser adequada para gerar uma imagem totalmente animada sem textos escritos.\n\n"
            "Forneça a descrição da cena em um único parágrafo."
        )

        # Chamada à API do OpenAI para gerar a descrição da cena
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system",
                 "content": "Você é um assistente que cria descrições visuais detalhadas de cenas para ilustrações de livros infantis totalmente animadas."},
                {"role": "user",
                 "content": prompt_gpt}
            ],
            max_tokens=150
        )
        descricao_cena = response['choices'][0]['message']['content'].strip()

        # Criar o prompt final para geração da imagem
        prompt_imagem = (
            f"{descricao_cena} "
            f"Estilo da imagem: {estilo}. "
            f"A imagem deve ser 100% animada e não deve conter nenhum texto ou escrita."
        )

        logging.info(f"Prompt gerado para imagem.")
        return prompt_imagem
    except Exception as e:
        logging.error(f"Erro ao gerar prompt para a parte da história: {e}")
        return ""



# Função para gerar e salvar a imagem com o DALL·E 3 a partir de um prompt
def gerar_e_salvar_imagem_sem_texto(prompt, image_number):
    max_retries = 5
    retry_delay = 5  # Segundos

    for attempt in range(max_retries):
        try:
            logging.info(f"Gerando imagem para o prompt...")
            response = openai.Image.create(
                model="dall-e-3",  # Modelo DALL·E 3
                prompt=prompt,
                n=1,
                size="1024x1024",
                response_format="url"
            )
            if 'data' in response and len(response['data']) > 0:
                image_url = response['data'][0]['url']
                r = requests.get(image_url)
                if r.status_code == 200:
                    logging.info("Imagem obtida com sucesso.")
                    image = Image.open(BytesIO(r.content))

                    buffer = BytesIO()
                    image_format = image.format if image.format else "PNG"
                    image.save(buffer, format=image_format)
                    image_data = buffer.getvalue()
                    buffer.close()
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                    return image_base64
                else:
                    logging.error(f"Falha ao baixar a imagem do URL: {image_url}")
                    return gerar_imagem_placeholder()
            else:
                logging.error("A resposta da API não contém dados de imagem.")
                return gerar_imagem_placeholder()
        except openai.error.APIError as e:
            logging.error(f"Erro na API (tentativa {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                logging.info(f"Tentando novamente em {retry_delay} segundos...")
                time.sleep(retry_delay)
                continue
            else:
                logging.error("Máximo de tentativas atingido. Usando imagem placeholder.")
                return gerar_imagem_placeholder()
        except Exception as e:
            logging.error(f"Erro durante a geração da imagem: {e}")
            if attempt < max_retries - 1:
                logging.info(f"Tentando novamente em {retry_delay} segundos...")
                time.sleep(retry_delay)
                continue
            else:
                logging.error("Máximo de tentativas atingido. Usando imagem placeholder.")
                return gerar_imagem_placeholder()
            


# Função para gerar uma imagem placeholder
def gerar_imagem_placeholder():
    logging.info("Gerando imagem placeholder...")
    img = Image.new('RGB', (1024, 1024), color=(255, 127, 80))  # Coral como placeholder
    return image_to_base64(img)


# Função para gerar imagem de agradecimento personalizada
def gerar_agradecimento(titulo, historia_texto, estilo):
    logging.info("Gerando imagem de agradecimento personalizada...")
    prompt = (
        "Com base no seguinte título e história de um livro infantil, crie uma descrição visual para a página de agradecimento. "
        "A imagem deve ser harmoniosa, inspiradora e refletir os temas e emoções da história. "
        "O estilo visual deve ser consistente com o restante do livro.\n\n"
        f"Título: {titulo}\n\n"
        f"História:\n{historia_texto}\n\n"
        "Descrição da Imagem de Agradecimento (apenas paisagem, sem personagens):"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system",
                 "content": "Você é um assistente especializado em criar descrições visuais para páginas de agradecimento em livros infantis, mantendo uma linguagem amigável e apropriada para crianças."},
                {"role": "user",
                 "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        descricao_imagem = response['choices'][0]['message']['content'].strip()
        logging.info("Descrição da imagem de agradecimento gerada com sucesso.")

        # Criar o prompt final para geração da imagem
        prompt_imagem = (
            f"{descricao_imagem} "
            f"Estilo da imagem: {estilo}. "
            f"A imagem deve ser 100% animada e adequada para crianças, sem incluir nenhum personagem, texto ou escrita."
        )

        # Gerar a imagem usando DALL·E 3
        imagem_base64_agradecimento = gerar_e_salvar_imagem_sem_texto(prompt_imagem, 'agradecimento')
        return imagem_base64_agradecimento
    except openai.error.APIError as e:
        logging.error(f"Erro na API: {e}")
        return gerar_imagem_placeholder()
    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado: {e}")
        return gerar_imagem_placeholder()
    


def gerar_html_contracapa(imagem_base64, logo_mopi_base64, logo_inovai_base64):
    logging.info("Gerando HTML da contracapa com texto de despedida e pequenos logos...")

    texto_despedida = """
Esta história foi cuidadosamente desenvolvida com o auxílio de inteligência artificial, fruto de uma colaboração inovadora entre o Colégio Mopi e a Inovai.lab.

Agradecemos profundamente a todos que contribuíram para este projeto inovador e estamos entusiasmados em continuar trazendo soluções que encantam, inspiram e transformam a educação.
    """

    # Processar o texto de despedida em parágrafos
    paragraphs = texto_despedida.strip().split('\n\n')
    formatted_text = ''.join(f'<p>{html.escape(paragraph.strip())}</p>' for paragraph in paragraphs)

    html_content = f"""
    <div class='pagina-contracapa'>
        <style>
            @page {{
                size: A5;
                margin: 0.8in;
            }}
            body {{
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
            }}
            .pagina-contracapa {{
                page-break-after: always;
                position: relative;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100%;
            }}
            .conteudo-contracapa {{
                width: 100%;
                max-width: 595px;
                margin: 0 auto;
                position: relative;
                padding: 20px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100%;
                text-align: center;
            }}
            .imagem-container-contracapa {{
                position: relative;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }}
            .imagem-contracapa {{
                width: 100%;
                height: auto;
                display: block;
            }}
            .texto-despedida-contracapa {{
                font-size: 12px;
                color: #000;
                line-height: 1.4;
                margin-top: 20px;
                padding: 10px;
                background-color: rgba(255, 255, 255, 0.7);
                border-radius: 10px;
            }}
            .logos-container-contracapa {{
                margin-top: 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 30px;
            }}
            .logo-pequena-contracapa {{
                max-width: 100px;
                max-height: 50px;
                object-fit: contain;
            }}
            .logo-mopi-contracapa {{
                width: 35px;
                opacity: 1;
                z-index: 2;
            }}
        </style>
        <div class='conteudo-contracapa'>
            <div class='imagem-container-contracapa'>
                <img class='imagem-contracapa' src='data:image/png;base64,{imagem_base64}' alt='Contracapa'>
                <div class='texto-despedida-contracapa'>
                    {formatted_text}
                    <div class='logos-container-contracapa'>
                        <img class='logo-pequena-contracapa logo-mopi-contracapa' src='data:image/png;base64,{logo_mopi_base64}' alt='Logo Mopi'>
                        <img class='logo-pequena-contracapa' src='data:image/png;base64,{logo_inovai_base64}' alt='Logo Inovai.lab'>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    return html_content





# Função para resumir a história, se necessário
def resumir_historia(historia_texto):
    logging.info("Resumindo a história para uso no prompt...")
    max_retries = 5
    retry_delay = 5  # Segundos
    for attempt in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system",
                     "content": "Você é um assistente que resume histórias infantis de forma concisa, capturando os principais temas e emoções."},
                    {"role": "user",
                     "content": f"Resuma a seguinte história infantil em até 500 palavras, destacando os principais temas e emoções envolvidas:\n\n{historia_texto}"}
                ],
                max_tokens=500
            )
            resumo = response['choices'][0]['message']['content'].strip()
            logging.info(f"Resumo da história obtido.")
            return resumo
        except openai.error.APIError as e:
            logging.error(f"Erro na API: {e}")
            if attempt < max_retries - 1:
                logging.info(f"Tentando novamente em {retry_delay} segundos...")
                time.sleep(retry_delay)
                continue
            else:
                logging.error("Máximo de tentativas atingido. Abortando.")
                return historia_texto
        except Exception as e:
            logging.error(f"Ocorreu um erro inesperado: {e}")
            return historia_texto
        





def formatar_como_livro_infantil(arquivo_word=None, student_name=None, preferencias=None, interesses=None, caracteristicas=None, caminho_pdf=None):
    print("formatar_como_livro_infantil")
    try:
        historia_texto = ""
        titulo = ""
        estilo_imagem = ""
        partes_historia = []
        imagens_base64 = []

        if preferencias and interesses and caracteristicas:
            historia_texto = gerar_historia(preferencias, interesses, caracteristicas)
        elif arquivo_word:
            logging.info(f"Processando o arquivo Word: {arquivo_word}...")
            try:
                doc = Document(arquivo_word)
                historia_texto = "\n".join([p.text for p in doc.paragraphs])
            except Exception as e:
                logging.error(f"Erro ao abrir o arquivo Word {arquivo_word}: {e}")
                return None, None, None
        else:
            logging.error("Nenhuma fonte de história fornecida.")
            return None, None, None

        if not historia_texto:
            logging.error("História não gerada ou vazia.")
            return None, None, None

        titulo, estilo_imagem = gerar_titulo_descricao_estilo(historia_texto)
        titulo_sanitizado = sanitizar_nome_arquivo(titulo)
        nome_pdf = f"{student_name}.pdf"
        partes_historia = quebrar_historia_em_partes(historia_texto, num_partes=14)
        imagens_base64 = []

        historia_resumo = historia_texto
        if len(historia_texto) > 2000:
            historia_resumo = resumir_historia(historia_texto)

        # Gerar descrição da capa
        descricao_capa_prompt = (
            "Com base na história resumida abaixo, descreva detalhadamente uma paisagem ou cenário que represente o ambiente principal da história para ser usada como imagem de capa de um livro infantil. "
            "A descrição deve ser visual, rica em detalhes e adequada para uma ilustração 100% animada, sem incluir personagens, textos ou diálogos.\n\n"
            f"História Resumida:\n{historia_resumo}\n\n"
            f"Estilo visual desejado: {estilo_imagem}\n\n"
            "Instruções:\n"
            "- Foque exclusivamente na descrição de paisagens, cenários e elementos naturais ou arquitetônicos presentes na história.\n"
            "- Não inclua personagens, ações específicas ou textos escritos.\n"
            "- A descrição deve ser apropriada para gerar uma imagem totalmente animada sem textos.\n\n"
            "Forneça apenas a descrição visual da paisagem em um único parágrafo."
        )

        try:
            response_capa = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system",
                     "content": "Você é um assistente que cria descrições visuais detalhadas para capas de livros infantis, focando em paisagens e cenários sem personagens."},
                    {"role": "user",
                     "content": descricao_capa_prompt}
                ],
                max_tokens=150
            )
            descricao_capa = response_capa['choices'][0]['message']['content'].strip()
        except Exception as e:
            logging.error(f"Erro ao gerar descrição da capa: {e}")
            descricao_capa = "Descrição padrão da capa."

        prompt_capa = (
            f"{descricao_capa} "
            f"Estilo da imagem: {estilo_imagem}. "
            f"A imagem deve ser 100% animada e não deve conter nenhum texto ou escrita."
        )
        imagem_base64_capa = gerar_e_salvar_imagem_sem_texto(prompt_capa, 0)
        imagens_base64.append(imagem_base64_capa)

        # Gerar imagens e prompts para cada parte da história
        for idx, parte in enumerate(partes_historia):
            prompt = gerar_prompt_para_parte(parte, estilo_imagem)
            if prompt:
                imagem_base64 = gerar_e_salvar_imagem_sem_texto(prompt, idx + 1)
                imagens_base64.append(imagem_base64)
            else:
                logging.warning(f"Prompt vazio para a parte {idx + 1}. Usando imagem placeholder.")
                imagens_base64.append(gerar_imagem_placeholder())

        # Gerar imagem para a contracapa
        descricao_contracapa_prompt = (
            "Crie uma descrição visual para a contracapa de um livro infantil baseada nas cenas finais da história resumida. "
            "A descrição deve ser encantadora, visualmente atraente, 100% animada e focar exclusivamente nas paisagens e cenários finais da história.\n\n"
            f"História Resumida:\n{historia_resumo}\n\n"
            f"Estilo visual desejado: {estilo_imagem}\n\n"
            "Instruções:\n"
            "- A descrição deve focar exclusivamente na descrição de paisagens, cenários e elementos naturais ou arquitetônicos presentes na história.\n"
            "- Não inclua personagens, ações específicas ou textos escritos.\n"
            "- A descrição deve ser apropriada para gerar uma imagem totalmente animada sem textos.\n\n"
            "Forneça apenas a descrição visual da paisagem em um único parágrafo."
        )

        try:
            response_contracapa = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system",
                     "content": "Você é um assistente que cria descrições visuais detalhadas para contracapas de livros infantis, focando em paisagens e cenários sem personagens."},
                    {"role": "user",
                     "content": descricao_contracapa_prompt}
                ],
                max_tokens=150
            )
            descricao_contracapa = response_contracapa['choices'][0]['message']['content'].strip()
        except Exception as e:
            logging.error(f"Erro ao gerar descrição da contracapa: {e}")
            descricao_contracapa = "Descrição padrão da contracapa."

        prompt_contracapa_final = (
            f"{descricao_contracapa} "
            f"Estilo da imagem: {estilo_imagem}. "
            f"A imagem deve ser 100% animada e não deve conter nenhum texto ou escrita."
        )
        imagem_base64_contracapa = gerar_e_salvar_imagem_sem_texto(prompt_contracapa_final, len(partes_historia) + 1)
        imagens_base64.append(imagem_base64_contracapa)

        # Verificar se todas as imagens foram geradas com sucesso
        logging.info("Verificando imagens geradas...")
        for idx, img in enumerate(imagens_base64):
            if not img:
                logging.warning(f"Imagem {idx} não foi gerada corretamente. Usando imagem placeholder.")
                imagens_base64[idx] = gerar_imagem_placeholder()

        # Gerar PDF do livro
        gerar_pdf_livro(
            titulo,                # titulo_capa
            partes_historia,       # historias
            imagens_base64,        # imagens_base64
            nome_pdf,              # nome_pdf (CORRETO)
            logo_base64,           # logo_base64 (CORRETO)
            logo_mopi_base64,      # logo_mopi_base64 (CORRETO)
            logo_inovai_base64     # logo_inovai_base64 (CORRETO)
        )

        return titulo, partes_historia, imagens_base64
    except Exception as e:
        logging.error(f"Erro ao formatar o livro infantil: {e}")
        return None, None, None
    
def gerar_pdf_livro(titulo_capa, historias, imagens_base64, nome_pdf, logo_base64, logo_mopi_base64, logo_inovai_base64):
    logging.info("Gerando o conteúdo HTML completo...")

    # Gerar HTML da capa
    html_capa = gerar_html_capa(titulo_capa, imagens_base64[0], logo_base64)

    # Gerar HTML da página de agradecimento personalizada
    html_agradecimento = gerar_html_agradecimento(imagens_base64[1], logo_base64)

    # Gerar HTML das páginas internas
    html_paginas = ""
    for i, (texto, imagem_base64) in enumerate(zip(historias, imagens_base64[2:-1]), start=1):
        html_paginas += gerar_html_pagina(texto, imagem_base64, i, logo_base64)

    # Gerar HTML da contracapa
    html_contracapa = gerar_html_contracapa(imagens_base64[-1], logo_mopi_base64, logo_inovai_base64)

    # Combinar HTML completo
    html_completo = f"""
    <html lang='pt-BR'>
    <head>
        <meta charset='UTF-8'>
    </head>
    <body>
        {html_capa}
        {html_agradecimento}
        {html_paginas}
        {html_contracapa}
    </body>
    </html>
    """

    # Salvar como PDF
    try:
        logging.info(f"Convertendo HTML para PDF: {nome_pdf}...")
        options = {
            'page-size': 'A5',
            'margin-top': '0.8in',
            'margin-right': '0.8in',
            'margin-bottom': '0.8in',
            'margin-left': '0.8in',
            'encoding': "UTF-8",
            'enable-local-file-access': None,
            'zoom': '1.0',
            'no-outline': None
        }
        # Definir o caminho para o wkhtmltopdf
        caminho_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config_pdfkit = pdfkit.configuration(wkhtmltopdf=caminho_wkhtmltopdf)
        
        # Definir o caminho para salvar o PDF (pasta especificada)
        caminho_pdf = os.path.join(PASTA_PDFS, nome_pdf)
        pdfkit.from_string(html_completo, caminho_pdf, configuration=config_pdfkit, options=options)
        logging.info(f"PDF '{nome_pdf}' gerado com sucesso na pasta '{PASTA_PDFS}'!")
    except Exception as e:
        logging.error(f"Erro ao gerar o PDF: {e}")



if __name__ == "__main__":
    caminho_origem = "C:\\Users\\User\\Downloads\\historias\\"
    caminho_destino = "C:\\Users\\User\\Downloads\\livros\\pdfs_gerados"
    processar_arquivos_na_pasta(caminho_origem, caminho_destino)


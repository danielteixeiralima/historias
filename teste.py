from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import openai
import requests
import base64
import logging
import re



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
            "Lembrando que a imagem não pode ter nenhum tipo de escrita"

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






def gerar_imagem_dalle(prompt):
    try:
        logging.info("Gerando imagem com DALL-E...")
        response = openai.Image.create(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="url"
        )
        image_url = response['data'][0]['url']
        r = requests.get(image_url)
        if r.status_code == 200:
            logging.info("Imagem obtida com sucesso.")
            return Image.open(BytesIO(r.content))
        else:
            logging.error(f"Erro ao baixar a imagem do DALL-E. Status: {r.status_code}")
            raise ValueError("Não foi possível baixar a imagem gerada.")
    except Exception as e:
        logging.error(f"Erro durante a geração da imagem com DALL-E: {e}")
        raise

def criar_capa(img, draw, font, titulo, estilo):
    # Gerar imagem de fundo usando DALL-E
    prompt_dalle = f"Ilustração de livro infantil no estilo: {estilo}. Deve ser vibrante, amigável e adequado para crianças de 6 a 8 anos."
    fundo = gerar_imagem_dalle(prompt_dalle).resize((1024, 1024))
    img.paste(fundo, (0, 0))

    # Configurar largura e altura da div para o título
    div_width = int(1024 * 0.7)
    div_height = 200  # Altura ajustável
    div_x = (1024 - div_width) // 2
    div_y = (1024 - div_height) // 2

    # Criar a div preta semi-transparente
    div_color = Image.new("RGBA", (div_width, div_height), (0, 0, 0, int(0.7 * 255)))
    img.paste(div_color, (div_x, div_y), div_color)

    # Configurar o texto com fonte de tamanho 24px
    title_font = ImageFont.truetype("arial.ttf", 24)  # Definindo explicitamente o tamanho como 24px
    text = titulo  # Título gerado dinamicamente
    text_bbox = draw.textbbox((0, 0), text, font=title_font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    text_x = div_x + (div_width - text_width) // 2
    text_y = div_y + (div_height - text_height) // 2
    draw.text((text_x, text_y), text, fill="white", font=title_font)



# Função para converter imagem PIL em base64
def image_to_base64(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    image_data = buffer.getvalue()
    buffer.close()
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    return image_base64



# Função para gerar uma imagem placeholder
def gerar_imagem_placeholder():
    logging.info("Gerando imagem placeholder...")
    img = Image.new('RGB', (1024, 1024), color=(255, 127, 80))  # Coral como placeholder
    return image_to_base64(img)



def criar_agradecimento(img, draw, font, logo, titulo, historia_texto, estilo):
    # Gerar imagem de fundo personalizada para o agradecimento
    fundo = gerar_agradecimento(titulo, historia_texto, estilo).resize((1024, 1024))
    img.paste(fundo, (0, 0))

    # Configurar o texto
    text = """Querida família,

Recebam este mimo de fim de ano, preparado com muito carinho pela equipe do Mopi, especialmente para você e sua família. Esta história foi criada com o apoio da inteligência artificial, que nos ajudou a concentrar, organizar e formatar de forma mais rápida e eficiente as informações preciosas que vocês compartilharam conosco, junto com os dados que temos sobre nossos alunos, trazendo detalhes únicos que deram vida a cada narrativa.

Por ser uma ferramenta nova, a inteligência artificial ainda pode apresentar algumas inconsistências, e pedimos que levem isso em consideração. Esta é apenas uma degustação de um universo de possibilidades que o Mopi está enxergando com a chegada dessa revolução tecnológica.
Estamos empenhados em usar essas inovações para proporcionar jornadas cada vez mais customizadas e individualizadas, respeitando as necessidades de cada aluno e trazendo à tona sua melhor versão todos os dias.

Esperamos que essa história encha seus corações de alegria e reforce o nosso compromisso em oferecer experiências educacionais significativas e personalizadas.

Com carinho,
Família Mopi"""

    # Ajustar largura da div branca para 70% da largura total
    div_width = int(1024 * 0.7)
    div_x = (1024 - div_width) // 2

    # Dividir o texto em múltiplas linhas para caber dentro da largura da div
    wrapped_lines = []
    max_line_width = div_width - 40  # Considerando margem interna de 20px de cada lado
    for paragraph in text.split("\n"):
        if paragraph.strip():
            words = paragraph.split()
            line = ""
            for word in words:
                test_line = f"{line} {word}".strip()
                test_line_width = draw.textbbox((0, 0), test_line, font=font)[2]
                if test_line_width <= max_line_width:
                    line = test_line
                else:
                    wrapped_lines.append(line)
                    line = word
            if line:
                wrapped_lines.append(line)
        else:
            wrapped_lines.append("")  # Adicionar linha em branco para parágrafos separados

    # Calcular a altura necessária para a div
    line_height = draw.textbbox((0, 0), "A", font=font)[3]
    total_text_height = len(wrapped_lines) * (line_height + 5)  # Inclui espaçamento entre linhas
    div_height = total_text_height + 40  # Margem superior e inferior
    div_y = (1024 - div_height) // 2

    # Criar a div branca semi-transparente com altura ajustável
    div_color = Image.new("RGBA", (div_width, div_height), (255, 255, 255, int(0.7 * 255)))
    img.paste(div_color, (div_x, div_y), div_color)

    # Escrever o texto dentro da div, respeitando margens laterais e espaçamento
    text_y = div_y + 20  # Margem superior
    for line in wrapped_lines:
        line_width = draw.textbbox((0, 0), line, font=font)[2]
        text_x = div_x + (div_width - line_width) // 2  # Centralizar horizontalmente
        draw.text((text_x, text_y), line, fill="black", font=font)
        text_y += line_height + 5  # Espaçamento entre linhas

    # Reduzir tamanho da logo e posicionar no canto inferior esquerdo
    resized_logo = logo.resize((int(logo.width * 0.8), int(logo.height * 0.8)))  # Reduz para 80%
    logo_position = (10, 1024 - resized_logo.size[1] - 10)  # Margem de 10px
    img.paste(resized_logo, logo_position, resized_logo)



def criar_paginas_historia(historia, total_paginas):
    # Dividir a história em sentenças baseadas no ponto final
    sentencas = historia.split('. ')
    total_sentencas = len(sentencas)
    paginas = []
    buffer = []
    
    # Calcular o número mínimo de sentenças por página, ajustando para cobrir toda a história
    base_sentencas_por_pagina = total_sentencas // total_paginas
    extra_sentencas = total_sentencas % total_paginas  # Sentenças extras a distribuir

    current_page_sentences = base_sentencas_por_pagina + (1 if extra_sentencas > 0 else 0)

    for i, sentenca in enumerate(sentencas):
        buffer.append(sentenca if sentenca.endswith('.') else sentenca + '.')
        
        if len(buffer) >= current_page_sentences and len(paginas) < total_paginas - 1:
            # Adicionar a página atual quando atingir o limite
            if buffer[-1].endswith('.'):
                paginas.append(" ".join(buffer).strip())
                buffer = []
                # Ajustar o número de sentenças para as páginas restantes
                extra_sentencas = max(0, extra_sentencas - 1)
                current_page_sentences = base_sentencas_por_pagina + (1 if extra_sentencas > 0 else 0)

    # Adicionar as sentenças restantes na última página
    if buffer:
        paginas.append(" ".join(buffer).strip())

    # Garantir exatamente 14 páginas (adicionando páginas vazias, se necessário)
    while len(paginas) < total_paginas:
        paginas.append("")

    return paginas

# Função para gerar imagem de agradecimento personalizada
def gerar_agradecimento(titulo, historia_texto, estilo):
    logging.info("Gerando imagem de agradecimento personalizada...")
    prompt = (
        "Com base no seguinte título e história de um livro infantil, crie uma descrição visual para a página de agradecimento. "
        "A imagem deve ser harmoniosa, inspiradora e refletir os temas e emoções da história. "
        "Lembrando que a imagem não pode ter nenhum tipo de escrita"
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
        return gerar_imagem_dalle(prompt_imagem)
    except openai.error.APIError as e:
        logging.error(f"Erro na API: {e}")
        return gerar_imagem_placeholder()
    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado: {e}")
        return gerar_imagem_placeholder()


    


def criar_pagina(img, draw, font, logo, texto):
    # Configurar imagem de fundo
    fundo = Image.open("fundo.jpg").resize((1024, 1024))
    img.paste(fundo, (0, 0))

    # Configurar largura da div
    div_width = int(1024 * 0.7)
    div_x = (1024 - div_width) // 2

    # Dividir o texto em múltiplas linhas para caber dentro da largura da div
    wrapped_lines = []
    max_line_width = div_width - 40  # Considerando margens laterais de 20px
    for paragraph in texto.split("\n"):
        if paragraph.strip():
            words = paragraph.split()
            line = ""
            for word in words:
                test_line = f"{line} {word}".strip()
                test_line_width = draw.textbbox((0, 0), test_line, font=font)[2]
                if test_line_width <= max_line_width:
                    line = test_line
                else:
                    wrapped_lines.append(line)
                    line = word
            if line:
                wrapped_lines.append(line)
        else:
            wrapped_lines.append("")  # Adicionar linha em branco para parágrafos separados

    # Calcular a altura necessária para a div
    line_height = draw.textbbox((0, 0), "A", font=font)[3]
    total_text_height = len(wrapped_lines) * (line_height + 5)  # Inclui espaçamento entre linhas
    div_height = total_text_height + 40  # Margem superior e inferior

    # Fixar a margem inferior da div em relação à imagem de fundo
    bottom_margin = 80  # Margem fixa de 50px entre a div e o final da imagem
    div_y = 1024 - div_height - bottom_margin  # Posicionar a div para crescer para cima

    # Criar a div branca semi-transparente com altura ajustável
    div_color = Image.new("RGBA", (div_width, div_height), (255, 255, 255, int(0.7 * 255)))
    img.paste(div_color, (div_x, div_y), div_color)

    # Escrever o texto dentro da div, alinhado à esquerda
    text_y = div_y + 20  # Margem superior
    for line in wrapped_lines:
        draw.text((div_x + 20, text_y), line, fill="black", font=font)  # Alinhado à esquerda
        text_y += line_height + 5  # Espaçamento entre linhas

    # Adicionar logo no canto inferior esquerdo
    resized_logo = logo.resize((int(logo.width * 0.8), int(logo.height * 0.8)))  # Reduz para 80%
    logo_position = (10, 1024 - resized_logo.size[1] - 10)  # Margem de 10px
    img.paste(resized_logo, logo_position, resized_logo)



def criar_contracapa(img, draw, font, logo1, logo2):
    # Configurar imagem de fundo
    fundo = Image.open("fundo.jpg").resize((1024, 1024))
    img.paste(fundo, (0, 0))

    # Configurar largura da div branca para 70% da largura total
    div_width = int(1024 * 0.7)
    div_x = (1024 - div_width) // 2

    # Texto da contracapa
    text = """
    Esta história foi cuidadosamente desenvolvida com o auxílio de inteligência artificial, fruto de uma colaboração inovadora entre o Colégio Mopi e a Inovai.lab.

Agradecemos profundamente a todos que contribuíram para este projeto inovador e estamos entusiasmados em continuar trazendo soluções que encantam, inspiram e transformam a educação.
    """

    # Dividir o texto em múltiplas linhas para caber dentro da largura da div
    wrapped_lines = []
    max_line_width = div_width - 40  # Considerando margens internas de 20px de cada lado
    for paragraph in text.strip().split("\n"):
        if paragraph.strip():
            words = paragraph.split()
            line = ""
            for word in words:
                test_line = f"{line} {word}".strip()
                test_line_width = draw.textbbox((0, 0), test_line, font=font)[2]
                if test_line_width <= max_line_width:
                    line = test_line
                else:
                    wrapped_lines.append(line)
                    line = word
            if line:
                wrapped_lines.append(line)
        else:
            wrapped_lines.append("")  # Adicionar linha em branco para parágrafos separados

    # Calcular a altura necessária para o texto na div
    line_height = draw.textbbox((0, 0), "A", font=font)[3]
    total_text_height = len(wrapped_lines) * (line_height + 5)  # Inclui espaçamento entre linhas

    # Configurar tamanho das logos
    logo1_resized = logo1.resize((80, 40))  # Redimensionar logo1
    logo2_resized = logo2.resize((70, 50))  # Ajustar altura para maior proporcionalidade
    logo_height = max(logo1_resized.height, logo2_resized.height)

    # Altura da div ajustada para incluir o texto e as logos
    div_height = total_text_height + logo_height + 60  # Margem superior/inferior
    div_y = (1024 - div_height) // 2

    # Criar a div branca semi-transparente
    div_color = Image.new("RGBA", (div_width, div_height), (255, 255, 255, int(0.7 * 255)))
    img.paste(div_color, (div_x, div_y), div_color)

    # Escrever o texto dentro da div
    text_y = div_y + 20  # Margem superior
    for line in wrapped_lines:
        line_width = draw.textbbox((0, 0), line, font=font)[2]
        text_x = div_x + (div_width - line_width) // 2  # Centralizar horizontalmente
        draw.text((text_x, text_y), line, fill="black", font=font)
        text_y += line_height + 5  # Espaçamento entre linhas

    # Posicionar as logos dentro da div, abaixo do texto
    logo_spacing = 20  # Espaço entre as logos
    logos_total_width = logo1_resized.width + logo2_resized.width + logo_spacing
    logos_x = div_x + (div_width - logos_total_width) // 2
    logos_y = text_y + 20  # Margem acima das logos

    # Retornar as logos e suas posições
    return logo1_resized, (logos_x, logos_y), logo2_resized, (logos_x + logo1_resized.width + logo_spacing, logos_y)

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

def criar_pagina_historia(img, draw, font, logo, texto, estilo):
    # Gerar imagem de fundo para a página da história usando DALL-E
    prompt_dalle = f"Ilustração animada para um livro infantil no estilo: {estilo}. Deve refletir o seguinte trecho da história: {texto}. A imagem deve ser vibrante, amigável e adequada para crianças de 6 a 8 anos, sem incluir nenhum texto ou escrita."
    fundo = gerar_imagem_dalle(prompt_dalle).resize((1024, 1024))
    img.paste(fundo, (0, 0))

    # Configurar largura da div branca semi-transparente para o texto
    div_width = int(1024 * 0.7)
    div_x = (1024 - div_width) // 2

    # Dividir o texto em múltiplas linhas para caber dentro da largura da div
    wrapped_lines = []
    max_line_width = div_width - 40  # Considerando margens laterais de 20px
    for paragraph in texto.split("\n"):
        if paragraph.strip():
            words = paragraph.split()
            line = ""
            for word in words:
                test_line = f"{line} {word}".strip()
                test_line_width = draw.textbbox((0, 0), test_line, font=font)[2]
                if test_line_width <= max_line_width:
                    line = test_line
                else:
                    wrapped_lines.append(line)
                    line = word
            if line:
                wrapped_lines.append(line)
        else:
            wrapped_lines.append("")  # Adicionar linha em branco para parágrafos separados

    # Calcular a altura necessária para o texto na div
    line_height = draw.textbbox((0, 0), "A", font=font)[3]
    total_text_height = len(wrapped_lines) * (line_height + 5)  # Inclui espaçamento entre linhas
    div_height = total_text_height + 40  # Margem superior e inferior

    # Posicionar a div para crescer para cima
    bottom_margin = 80  # Margem fixa de 80px entre a div e o final da imagem
    div_y = 1024 - div_height - bottom_margin  # Posicionar a div para crescer para cima

    # Criar a div branca semi-transparente com altura ajustável
    div_color = Image.new("RGBA", (div_width, div_height), (255, 255, 255, int(0.7 * 255)))
    img.paste(div_color, (div_x, div_y), div_color)

    # Escrever o texto dentro da div, alinhado à esquerda
    text_y = div_y + 20  # Margem superior
    for line in wrapped_lines:
        draw.text((div_x + 20, text_y), line, fill="black", font=font)  # Alinhado à esquerda
        text_y += line_height + 5  # Espaçamento entre linhas

    # Adicionar logo no canto inferior esquerdo
    resized_logo = logo.resize((int(logo.width * 0.8), int(logo.height * 0.8)))  # Reduz para 80%
    logo_position = (10, 1024 - resized_logo.size[1] - 10)  # Margem de 10px
    img.paste(resized_logo, logo_position, resized_logo)


def criar_pdf():
    # Configurações
    font = ImageFont.truetype("arial.ttf", 16)
    logo = Image.open("logo_mopi_cor.png").resize((100, 50))
    logo2 = Image.open("logo.png").resize((100, 50))
    historia = """
    Era uma vez um menino chamado Gael Curcio Gonçalves Dufrayer, um garoto tão radiante quanto o próprio sol. Com seus cabelos claros que balançavam ao vento como feixes de luz, e olhinhos verdinhos que brilhavam de curiosidade, Gael tinha o poder mágico de alegrar a todos com seu sorriso contagiante.

    (História completa aqui)
    """  # História completa aqui

    # Gerar título e estilo
    titulo, estilo = gerar_titulo_descricao_estilo(historia)

    # Dividir a história em 14 partes
    paginas_historia = criar_paginas_historia(historia, 14)
    
    # Lista de imagens do PDF
    pdf_images = []

    # Gerar capa
    img = Image.new("RGBA", (1024, 1024), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    criar_capa(img, draw, font, titulo, estilo)  # Passa o título e estilo gerados
    pdf_images.append(img.convert("RGB"))

    # Gerar agradecimento
    img = Image.new("RGBA", (1024, 1024), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    criar_agradecimento(img, draw, font, logo, titulo, historia, estilo)
    pdf_images.append(img.convert("RGB"))

    # Gerar páginas da história
    for texto in paginas_historia:
        img = Image.new("RGBA", (1024, 1024), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)
        criar_pagina_historia(img, draw, font, logo, texto, estilo)
        pdf_images.append(img.convert("RGB"))

    # Gerar contracapa
    img = Image.new("RGBA", (1024, 1024), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    logo1, pos1, logo2, pos2 = criar_contracapa(img, draw, font, logo, logo2)
    img.paste(logo1, pos1, logo1)
    img.paste(logo2, pos2, logo2)
    pdf_images.append(img.convert("RGB"))

    # Salvar PDF
    pdf_images[0].save("documento.pdf", save_all=True, append_images=pdf_images[1:])
    print("PDF gerado com sucesso!")
    

def gerar_pdf():
    # Configurações
    font = ImageFont.truetype("arial.ttf", 16)
    logo = Image.open("logo_mopi_cor.png").resize((100, 50))
    logo2 = Image.open("logo.png").resize((100, 50))
    historia = """
    Era uma vez um menino chamado Gael Curcio Gonçalves Dufrayer, um garoto tão radiante quanto o próprio sol. Com seus cabelos claros que balançavam ao vento como feixes de luz, e olhinhos verdinhos que brilhavam de curiosidade, Gael tinha o poder mágico de alegrar a todos com seu sorriso contagiante.

Gael vivia em uma charmosa vila costeira chamada Vila das Brasas, conhecida por suas areias douradas e belas praias onde o mar cantava canções de ninar. Ele adorava andar por ali descalço, sentindo a areia fofa e quente sob os pés, sempre acompanhado de sua amiga inseparável, Luiza, uma cachorrinha falante que parecia ter saído de um conto de fadas.

Um dia, enquanto corria pelo jardim, Gael encontrou um mapa mágico escondido debaixo de uma das flores coloridas. O mapa prometia levá-lo a um lugar encantado chamado Mini Mundo das Maravilhas, onde todos os seus sonhos podiam se tornar realidade. Gael, que sempre amou a aventura e tudo que é elétrico, mal podia esperar para iniciar essa jornada.

Antes de partir, Gael chamou seus amigos, Benjamin e Rafael, dois irmãos corajosos e divertidos. Benjamin adorava desenhar carros e caminhões, e Rafael era fã de histórias de bombeiros e policiais. Juntos, eles formavam o trio perfeito para explorar o desconhecido. Animados, cada um pegou seu paninho de estimação - não importa a aventura, o conforto era sempre bem-vindo.

Para chegar ao Mini Mundo das Maravilhas, eles precisariam viajar em uma máquina especial. Gael ativou seu talento para máquinas e, com a ajuda de Rodinhas, um helicóptero falante com hélices coloridas e luzes piscantes, construiu um carro mágico. Aquele carro era grande, forte, com rodas imensas, cheio de luzes que piscavam como estrelas em uma noite clara, e o som do motor ressoava como música em seus ouvidos. Ele até soltava fumaça sempre que se movia, e o papel principal do comando era dizer "Vamos lá, Exploradores!" seguido de ruídos divertidos que faziam todos rirem.

Após alguns ajustes, o carro-carruagem começou a rodar sozinho, como se possuísse vida própria. Gael e seus amigos embarcaram na aventura, com Luiza, a cachorrinha que adorava aventuras, liderando o caminho. O carro era veloz, mas seguro, e seguia o curso traçado no mapa, como se já soubesse o caminho.

No percurso, eles enfrentaram desafios mágicos, incluindo a Floresta dos Sussurros, onde o medo do escuro de Gael foi posto à prova. No início, Gael se sentiu inseguro, mas ao lembrar das palavras de encorajamento de sua mãe, dizendo que ele era especial e único, encontrou a coragem. Raphael, que sempre gostou de salvar o dia, usou uma lanterna de cristais de arco-íris do carro para iluminar a passagem. Essa luz afastava os medos e fazia desabrochar flores luminosas pelo caminho.

Benjamin, inspirado por suas invenções de papel, desenhou um imenso mural de personagens que acalmou e inspirou Gael, que percebeu não estar sozinho e que seus amigos sempre estariam por perto. Enfrentando diferentes criaturas divertidas, aprenderam a importância da paciência e a confiança em si mesmos e uns nos outros.

Finalmente, chegaram ao Mini Mundo das Maravilhas. Lá, Gael ficou fascinado ao encontrar uma cidade inteira em miniatura, como aquela que tinha visto em sua viagem a Gramado. As casinhas, os carros, e até mesmo uma maria-fumaça em miniatura, funcionavam como mágica, chamando Gael para explorar cada detalhe. Era um lugar onde tudo que ele amava estava ao alcance de suas mãos.

A lição mais valiosa daquela aventura era que amizades e coragem fazem cada sonho parecer mais próximo. Gael também aprendeu que não precisa ter medo do escuro ou do desconhecido, pois sempre há uma luz ou um amigo por perto para guiá-lo.

Quando retornaram a Vila das Brasas, Gael, Benjamin, Rafael e Luiza prometeram nunca esquecer essa aventura mágica e continuaram a explorar, sabendo que juntos eram mais fortes e que não havia sonho grande demais para realizar. E assim, na companhia de seus amigos, Gael continuou a criar mundos encantados, onde cada dia era uma nova página em branco, pronta para ser preenchida com novas aventuras e descobertas.
"""  # História completa aqui

    # Gerar título e estilo
    titulo, estilo = gerar_titulo_descricao_estilo(historia)

    # Dividir a história em 14 partes
    paginas_historia = criar_paginas_historia(historia, 14)
    
    # Lista de imagens do PDF
    pdf_images = []

    # Gerar capa
    img = Image.new("RGBA", (1024, 1024), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    criar_capa(img, draw, font, titulo, estilo)  # Passa o título e estilo gerados
    pdf_images.append(img.convert("RGB"))

    # Gerar agradecimento
    img = Image.new("RGBA", (1024, 1024), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    criar_agradecimento(img, draw, font, logo, titulo, historia, estilo)
    pdf_images.append(img.convert("RGB"))

    # Gerar páginas da história
    for texto in paginas_historia:
        img = Image.new("RGBA", (1024, 1024), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)
        criar_pagina(img, draw, font, logo, texto)
        pdf_images.append(img.convert("RGB"))

    # Gerar contracapa
    img = Image.new("RGBA", (1024, 1024), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    logo1, pos1, logo2, pos2 = criar_contracapa(img, draw, font, logo, logo2)
    img.paste(logo1, pos1, logo1)
    img.paste(logo2, pos2, logo2)
    pdf_images.append(img.convert("RGB"))

    # Salvar PDF
    pdf_images[0].save("documento.pdf", save_all=True, append_images=pdf_images[1:])
    print("PDF gerado com sucesso!")


# Gerar PDF
gerar_pdf()
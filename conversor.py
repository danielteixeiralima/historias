import os
from docx import Document
from reportlab.pdfgen import canvas

def convert_docx_to_pdf(source_file, target_file):
    try:
        # Carregar o documento DOCX
        doc = Document(source_file)
        pdf = canvas.Canvas(target_file)
        
        # Adicionar conteúdo do documento no PDF
        for paragraph in doc.paragraphs:
            pdf.drawString(50, 800, paragraph.text)  # Ajuste de margem
            pdf.showPage()
        
        pdf.save()
        print(f"Convertido: {source_file} -> {target_file}")
    except Exception as e:
        print(f"Erro ao converter {source_file}: {e}")

def create_pdf_structure(source_dir, target_dir):
    # Cria a pasta destino se não existir
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    for root, dirs, files in os.walk(source_dir):
        # Recria a estrutura de pastas na pasta de destino
        relative_path = os.path.relpath(root, source_dir)
        target_path = os.path.join(target_dir, relative_path)
        if not os.path.exists(target_path):
            os.makedirs(target_path)

        for file in files:
            if file.endswith('.docx') and not file.startswith('~$'):  # Ignora arquivos temporários
                source_file = os.path.join(root, file)
                target_file = os.path.join(target_path, file.replace('.docx', '.pdf'))
                convert_docx_to_pdf(source_file, target_file)

# Caminhos das pastas
source_directory = r"C:\Users\User\Downloads\historias"  # Pasta original
target_directory = r"C:\Users\User\Downloads\historias_pdf"  # Pasta destino

# Executa a conversão
create_pdf_structure(source_directory, target_directory)

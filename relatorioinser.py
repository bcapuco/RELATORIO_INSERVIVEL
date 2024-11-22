import pandas as pd
import glob
import os
import requests
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Função para baixar imagem
def download_image(image_url, output_path):
    try:
        response = requests.get(image_url, stream=True, timeout=10)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return output_path
    except Exception as e:
        print(f"Erro ao baixar imagem {image_url}: {e}")
        return None

# Coletar arquivos CSV
csv_files = [file for file in glob.glob('/home/capuco/VSCODE/SRC/Arquivocsv/*.csv') if os.path.isfile(file)]

# Concatenar os DataFrames
df = pd.concat((pd.read_csv(file, delimiter=';') for file in csv_files), ignore_index=True)

# Remover espaços em branco dos nomes das colunas
df.columns = [col.strip() for col in df.columns]

total_bens = len(df)
total_valor_liquido = df['valor_atual'].sum()

# Configurar o PDF em paisagem
output_pdf = "inventario.pdf"
pdf = SimpleDocTemplate(output_pdf, pagesize=landscape(letter))
estilos = getSampleStyleSheet()
elements = []

# Título do documento
elements.append(Paragraph("Inventário Patrimonial 2024", estilos['Title']))
elements.append(Spacer(1, 10))

# Cabeçalho da tabela
data = [["PATRIMONIO", "PLAQUETA", "QRCODE", "LOCALIZAÇÃO", "RESPONSÁVEL", "CONSERVAÇÃO", "VALOR LÍQUIDO", "STATUS", "IMAGEM PLAQUETA", "IMAGEM PATRIMÔNIO"]]

# Estilo de parágrafo para texto longo
# Estilo de parágrafo para texto longo, ajustado para quebra de linha
wrap_style = ParagraphStyle(name="Wrap", fontSize=7, leading=9, alignment=1, wordWrap='CJK', maxWidth=100)

# Adicionar dados do CSV à tabela
for _, row in df.iterrows():
    # Formatação de plaqueta_unicode
    plaqueta_unicode = row.get('plaqueta_unicode', '')
    if pd.isna(plaqueta_unicode) or not plaqueta_unicode:
        plaqueta_unicode_formatado = 'S/T'
    else:
        try:
            # Verifica se o valor é numérico e tenta formatar
            plaqueta_unicode = str(plaqueta_unicode)  # Converte para string, se necessário
            plaqueta_unicode_formatado = f"CON-{int(plaqueta_unicode):04d}"
        except ValueError:
            # Caso não seja numérico, retorna o valor original
            plaqueta_unicode_formatado = plaqueta_unicode.strip() if isinstance(plaqueta_unicode, str) else 'S/T'

    # Formatação de plaqueta_qrcode
    plaqueta_qrcode = row.get('plaqueta_qrcode', None)
    if pd.isna(plaqueta_qrcode):
        plaqueta_qrcode_formatado = 'S/T'
    else:
        plaqueta_qrcode_formatado = str(int(float(plaqueta_qrcode))).zfill(5)

    # Formatação de valor líquido
    valor_liquido_formatado = f"R$ {float(row.get('valor_atual', 0)):,.2f}"

    # Quebra de texto para colunas longas
    patrimonio = Paragraph(row.get('patrimonio_unicode', 'S/T'), wrap_style)
    responsavel = Paragraph(row.get('responsavel_unicode', 'S/T'), wrap_style)
    localizacao = Paragraph(row.get('localizacao_unicode', 'S/T'), wrap_style)
    conservacao = Paragraph(row.get('conservacao_display', 'S/T'), wrap_style)
    status = Paragraph(row.get('status_display', 'S/T'), wrap_style)

    # Baixar imagens
    plaqueta_image_path = download_image(row.get('imagem_plaqueta', ''), f"plaqueta_{row['pk']}.jpg") if pd.notna(row.get('imagem_plaqueta')) else None
    patrimonio_image_path = download_image(row.get('imagem_patrimonio', ''), f"patrimonio_{row['pk']}.jpg") if pd.notna(row.get('imagem_patrimonio')) else None

    # Preparar imagens para a tabela
    if plaqueta_image_path and os.path.exists(plaqueta_image_path):
        plaqueta_image = Image(plaqueta_image_path, width=50, height=50)
    else:
        plaqueta_image = "S/T"

    if patrimonio_image_path and os.path.exists(patrimonio_image_path):
        patrimonio_image = Image(patrimonio_image_path, width=50, height=50)
    else:
        patrimonio_image = "S/T"
    
    # Adicionar dados formatados à tabela
    data.append([
        patrimonio,  # Usar o Paragraph que já cuida da quebra de linha
        plaqueta_unicode_formatado,
        plaqueta_qrcode_formatado,
        localizacao,
        responsavel,
        conservacao,
        valor_liquido_formatado,
        status,
        plaqueta_image,
        patrimonio_image
    ])

# Configurar uma tabela
col_widths = [70, 70, 60, 120, 100, 60, 60, 70, 80, 80]  # Ajuste a largura da coluna "PATRIMÔNIO" conforme necessário
table = Table(data, colWidths=col_widths, repeatRows=1)
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 7),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
]))

elements.append(table)

# Salvar o PDF
pdf.build(elements)
print(f"PDF gerado com sucesso: {output_pdf}")












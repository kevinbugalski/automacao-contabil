import os
from pdf2image import convert_from_path
from PIL import Image
import imagehash

padroes_recorte = {
    "ASAAS":         (1650, 50, 2050, 230),
    "BRADESCO":      (80, 60, 580, 210),
    "BTG":           (250, 130, 750, 280),
    "C6BANK":        (1300, 110, 1700, 260),
    "CAIXA":         (250, 80, 750, 230),
    "CORA":          (1600, 130, 2100, 300),
    "BB_MODELO1":    (1450, 100, 1950, 230),
    "BB_MODELO2":    (80, 150, 580, 280),
    "INTER":         (80, 100, 580, 250),
    "ITAU":          (1090, 80, 1530, 230),
    "NUBANK":        (130, 250, 630, 400),
    "PAGSEGURO":     (80, 180, 580, 330),
    "SANTANDER":     (150, 180, 650, 330),
    "SICOOB":        (260, 30, 760, 180),
    "SICREDI":       (80, 60, 480, 180),
    "STONE":         (-300, 30, -10, 130),
}

LOGOS_PATH = os.path.join(os.path.dirname(__file__), "bancos", "logos")

def identificar_banco_por_imagem(caminho_pdf):
    imagem = convert_from_path(caminho_pdf, dpi=300, first_page=1, last_page=1)[0]
    largura, altura = imagem.size
    imagem_resultados = {}

    for banco, (x1, y1, x2, y2) in padroes_recorte.items():
        x1_final = largura + x1 if x1 < 0 else x1
        x2_final = largura + x2 if x2 < 0 else x2
        cropped = imagem.crop((x1_final, y1, x2_final, y2))

        caminho_logo_ref = os.path.join(LOGOS_PATH, f"{banco}.png")
        if not os.path.exists(caminho_logo_ref):
            continue

        logo_ref = Image.open(caminho_logo_ref)
        hash_crop = imagehash.phash(cropped.resize((128, 128)).convert("L"))
        hash_ref = imagehash.phash(logo_ref.resize((128, 128)).convert("L"))
        distancia = abs(hash_crop - hash_ref)

        imagem_resultados[banco] = distancia

    banco_detectado = min(imagem_resultados, key=imagem_resultados.get)
    confianca = imagem_resultados[banco_detectado]
    return banco_detectado if confianca < 20 else "Nao identificado"

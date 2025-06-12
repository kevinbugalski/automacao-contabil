import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np

# Definindo o caminho do executável Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extrair_texto_pdf(caminho_pdf):
    imagens = convert_from_path(caminho_pdf, dpi=300)
    texto_total = ""
    for imagem in imagens:
        imagem_cv = cv2.cvtColor(np.array(imagem), cv2.COLOR_RGB2GRAY)
        texto = pytesseract.image_to_string(imagem_cv, lang='por')
        texto_total += texto + "\n"
    return texto_total

def identificar_banco(texto):
    texto = texto.lower()
    if "itaú" in texto or "itau" in texto:
        return "ITAÚ"
    elif "bradesco" in texto:
        return "BRADESCO"
    elif "caixa" in texto or "cef" in texto:
        return "CAIXA ECONÔMICA"
    elif "santander" in texto:
        return "SANTANDER"
    elif "nubank" in texto:
        return "NUBANK"
    elif "inter" in texto:
        return "INTER"
    elif "btg" in texto:
        return "BTG PACTUAL"
    elif "cora" in texto:
        return "CORA"
    elif "sicredi" in texto:
        return "SICREDI"
    elif "sicoob" in texto:
        return "SICOOB"
    elif "asaas" in texto:
        return "ASAAS"
    elif "pagseguro" in texto:
        return "PAGSEGURO"
    elif "stone" in texto:
        return "STONE"
    else:
        return "BANCO NÃO IDENTIFICADO"
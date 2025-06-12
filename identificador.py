# identificador.py

import pdfplumber
import pandas as pd
from unidecode import unidecode       # pip install unidecode
import pytesseract
from pdf2image import convert_from_path
import json
import os

DB_MODELOS = "modelos_identificados.json"

def carregar_modelos_salvos():
    if os.path.exists(DB_MODELOS):
        with open(DB_MODELOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_modelo(texto_extraido, banco_identificado):
    modelos = carregar_modelos_salvos()
    novo_modelo = {
        "banco": banco_identificado,
        "amostra_texto": texto_extraido[:1000]
    }
    modelos[f"{banco_identificado}_modelo_{len(modelos)+1}"] = novo_modelo
    with open(DB_MODELOS, "w", encoding="utf-8") as f:
        json.dump(modelos, f, indent=2, ensure_ascii=False)

def identificar_layout(caminho):
    # ─── Quick-test para ASAAS ─────────────────────────────────────────────
    if caminho.lower().endswith("asaas.pdf"):
        return "asaas"
    # ────────────────────────────────────────────────────────────────────────

    def texto_pdf(caminho_pdf):
        texto = ""
        try:
            with pdfplumber.open(caminho_pdf) as pdf:
                for page in pdf.pages[:2]:
                    page_text = page.extract_text()
                    if page_text:
                        texto += unidecode(page_text.lower())
        except Exception as e:
            print("Erro ao ler PDF com pdfplumber:", e)
        return texto

    def texto_pdf_ocr(caminho_pdf):
        try:
            images = convert_from_path(caminho_pdf, first_page=1, last_page=1)
            img_text = pytesseract.image_to_string(images[0])
            return unidecode(img_text.lower())
        except Exception as e:
            print("Erro ao aplicar OCR:", e)
            return ""

    def colunas_excel(caminho_excel):
        try:
            df = pd.read_excel(caminho_excel, nrows=1)
            return [unidecode(c.strip().lower()) for c in df.columns]
        except Exception as e:
            print("Erro ao ler Excel:", e)
            return []

    try:
        if caminho.lower().endswith(".pdf"):
            texto = texto_pdf(caminho)
            if len(texto.strip()) < 100:
                texto += texto_pdf_ocr(caminho)

            palavras_chave = {
                "bradesco": [
                    "rentab.invest facilcred",
                    "bradesco admin",
                    "invest facil"
                ],
                "btg": ["banco 208"],
                "nubank": ["roxinho", "transferência recebida pelo pix", "ouvidoria@nubank.com.br"],
                "cora": ["extrato gerado no dia", "banco cora"],
                "asaas": ["asaas"],
                "c6": ["c6 bank", "banco c6"],
                "inter": ["banco inter", "intermedium"],
                "itau": ["itau unibanco", "mov titulo"],
                "pagseguro": ["pagseguro", "pagbank"],
                "sicoob": ["sicoob"],
                "sicredi": ["sicredi"],
                "stone": ["stone instituicao", "stone pagamentos"]
            }

            for banco, chaves in palavras_chave.items():
                for chave in chaves:
                    if chave in texto:
                        print(f"[LOG] Banco identificado por palavra-chave: '{chave}' → {banco}")
                        salvar_modelo(texto, banco)
                        return banco

        elif caminho.lower().endswith((".xls", ".xlsx")):
            colunas = colunas_excel(caminho)
            # ... seu mapeamento de colunas para Excel continua aqui ...
            if "nome do favorecido" in colunas:
                return "cora"
            # etc.

    except Exception as e:
        print("Erro geral ao identificar layout:", e)

    return "desconhecido"
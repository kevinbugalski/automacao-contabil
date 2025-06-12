import os
import re
import pandas as pd
from ocr_utils import extrair_texto_pdf, identificar_banco

# Diretório base e de entrada
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_PDFS = os.path.join(BASE_DIR, "exemplos")

# Regex para mês/ano
PADRAO_MES_ANO = re.compile(r"(janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)[^\d]{0,5}(20\d{2})", re.IGNORECASE)

resultados = []

for nome_arquivo in os.listdir(PASTA_PDFS):
    if nome_arquivo.lower().endswith(".pdf"):
        caminho_pdf = os.path.join(PASTA_PDFS, nome_arquivo)
        try:
            texto = extrair_texto_pdf(caminho_pdf)
        except MemoryError:
            resultados.append([nome_arquivo, "Erro", "Erro: Memória insuficiente"])
            print(f"[ERRO] {nome_arquivo}: Arquivo muito grande (MemoryError)")
            continue

        try:
            banco = identificar_banco(texto)

            # Procurar mês e ano no texto
            mes_ano_match = PADRAO_MES_ANO.search(texto)
            if mes_ano_match:
                mes = mes_ano_match.group(1).strip().capitalize()
                ano = mes_ano_match.group(2)
                referencia = f"{mes.upper()}/{ano}"
            else:
                referencia = "Não localizado"

            resultados.append([nome_arquivo, banco, referencia])
            print(f"[OK] {nome_arquivo} → {banco} ({referencia})")

        except Exception as e:
            resultados.append([nome_arquivo, "Erro", "Erro", str(e)])
            print(f"[ERRO] {nome_arquivo}: {e}")


# Exportar para Excel
df = pd.DataFrame(resultados, columns=["Arquivo", "Banco", "Mês/Ano"])
saida = os.path.join(BASE_DIR, "resultado_bancos_ocr.xlsx")
df.to_excel(saida, index=False)

print(f"\n✅ Resultado salvo em: {saida}")
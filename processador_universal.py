import os
import pandas as pd
from processadores.asaas import extrair_dados_pdf_asaas

def processar_excel(caminho_arquivo: str, banco: str) -> pd.DataFrame:
    """
    Pipeline mínimo para Asaas:
    - ignora o parâmetro banco, sempre chama extrair_dados_pdf_asaas
    - retorna DataFrame com as colunas padronizadas e duas colunas em branco
    """
    # 1) Extrai a lista de transações
    raw = extrair_dados_pdf_asaas(caminho_arquivo)

    # 2) Monta o DataFrame
    df = pd.DataFrame(
        raw,
        columns=[
            "Data de Ocorrência",
            "Fornecedor/Cliente",
            "Complemento Histórico",
            "Valor"
        ]
    )

    # 3) Colunas de classificação (vazias)
    df["Conta Fornecedor"] = ""
    df["Conta Cliente"]    = ""

    return df
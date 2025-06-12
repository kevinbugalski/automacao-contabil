import os
import io
import streamlit as st
import pandas as pd

from processador_universal import processar_excel
from gerar_txt import gera_txt_dominio_fix

BASE_DIR = os.path.dirname(__file__)
TXT_DIR  = os.path.join(BASE_DIR, "txt_saida")
os.makedirs(TXT_DIR, exist_ok=True)

st.set_page_config(page_title="Extrato → Excel → .txt Domínio", layout="wide")
st.title("📘 Extrato → Excel classificado → .txt para Domínio")

etapa = st.sidebar.radio(
    "Escolha a etapa:",
    ["PDF → Excel", "Excel classificado → TXT Domínio"]
)

if etapa == "PDF → Excel":
    st.info("Envie o PDF do extrato para gerar o Excel para classificação.")
    pdf = st.file_uploader("📄 Envie o PDF", type="pdf")
    if pdf:
        pdf_path = os.path.join(BASE_DIR, "temp_extrato.pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf.read())

        try:
            df = processar_excel(pdf_path, banco=None)
        except Exception as e:
            st.error(f"❌ Erro ao processar PDF: {e}")
            st.stop()

        st.success("✅ PDF processado com sucesso!")
        st.dataframe(df, use_container_width=True)

        # gera download do Excel para classificação
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        st.download_button(
            label="📥 Baixar Excel para classificação",
            data=buffer,
            file_name="lancamentos_para_classificar.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.info("Envie o Excel já classificado (preencha Conta Cliente ou Conta Fornecedor e Complemento).")
    excel = st.file_uploader("📁 Envie o Excel (.xlsx)", type="xlsx")
    conta = st.text_input("Conta contábil do banco (ex: 009)")

    if excel and conta:
        caminho_xlsx = os.path.join(BASE_DIR, excel.name)
        with open(caminho_xlsx, "wb") as f:
            f.write(excel.read())

        # lê sem dayfirst
        try:
            df2 = pd.read_excel(
                caminho_xlsx,
                engine="openpyxl",
                dtype={
                    "Fornecedor/Cliente": str,
                    "Complemento Histórico": str,
                    "Conta Fornecedor": str,
                    "Conta Cliente": str
                },
                parse_dates=["Data de Ocorrência"],
                errors="ignore"
            )
            # corrige Data de Ocorrência com dayfirst
            df2["Data de Ocorrência"] = pd.to_datetime(
                df2["Data de Ocorrência"], dayfirst=True, errors="coerce"
            )
            if df2["Data de Ocorrência"].isna().any():
                raise ValueError("Há datas inválidas no Excel.")
        except Exception as e:
            st.error(f"❌ Erro ao ler Excel: {e}")
            st.stop()

        st.success("✅ Excel classificado lido com sucesso!")
        st.dataframe(df2, use_container_width=True)

        if st.button("🚀 Gerar .txt final para Domínio"):
            try:
                caminho_txt = gera_txt_dominio_fix(df2, conta, TXT_DIR)
                with open(caminho_txt, "rb") as fp:
                    st.download_button(
                        label="📥 Baixar .txt Domínio",
                        data=fp,
                        file_name=os.path.basename(caminho_txt),
                        mime="text/plain"
                    )
            except Exception as e:
                st.error(f"❌ Erro ao gerar .txt: {e}")
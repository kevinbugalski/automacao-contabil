import streamlit as st
import pandas as pd
from pathlib import Path
from processador_universal import detecta_banco_e_processa

st.title("Automação de Extratos Bancários")

uploaded = st.file_uploader("Anexe PDF ou Excel", type=['pdf','xlsx'])
if uploaded is None:
    st.warning("Por favor, anexe um arquivo PDF ou Excel para continuar.")
    st.stop()

# agora uploaded é garantido
temp = Path("temp") / uploaded.name
temp.parent.mkdir(exist_ok=True)
with open(temp, "wb") as f:
    f.write(uploaded.getbuffer())

df = detecta_banco_e_processa(str(temp))
df_edit = st.experimental_data_editor(df, num_rows="dynamic")

# salva temporário
temp = Path("temp") / uploaded.name
temp.parent.mkdir(exist_ok=True)
with open(temp, "wb") as f: f.write(uploaded.getbuffer())

# processa
df = detecta_banco_e_processa(str(temp))

# edita in-place (Streamlit 1.24+)
df_edit = st.experimental_data_editor(df, num_rows="dynamic")

# exporta Excel
if st.button("Exportar Excel"):
    out = Path("output") / f"padronizado_{uploaded.name}.xlsx"
    out.parent.mkdir(exist_ok=True)
    df_edit.to_excel(out, index=False)
    st.success(f"Excel salvo em {out}")

# gera TXT Domínio
def gera_txt_dominio(df: pd.DataFrame) -> str:
    """
    Gera o .txt seguindo o seu template de Domínio Sistemas.
    (Aqui você injeta header, body e trailer)
    """
    header = "00HEADER..."  # adapte conforme seu modelo
    trailer = "99TRAILER..."
    linhas = [header]
    for i, row in df.iterrows():
        data = row["Data de Ocorrência"]
        valor = abs(row["Valor"])
        # se for saída:
        if row["Valor"] < 0:
            debito  = row["Conta Fornecedor"]
            credito = ""  # sua conta do banco
        else:
            debito  = ""
            credito = row["Conta Cliente"]
        # formata segmentos:
        seg02 = f"02{(i+1):06d}{data}"
        seg03 = f"03{(i+1):06d}{debito:6}{credito:6}{valor:014.2f}{row['Complemento Histórico'][:50].ljust(50)}"
        linhas += [seg02, seg03]

    linhas.append(trailer)
    return "\r\n".join(linhas)

if st.button("Gerar TXT Domínio"):
    txt = gera_txt_dominio(df_edit)
    st.download_button("Baixar .txt", txt, file_name="dominio_import.txt")
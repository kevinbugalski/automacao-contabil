import os
import pandas as pd

def gera_txt_dominio_fix(df: pd.DataFrame, conta_banco: str, output_dir: str) -> str:
    """
    Gera o .txt no leiaute fixo do Domínio Sistemas.
    Usa sempre a PRIMEIRA linha do template como cabeçalho
    e a ÚLTIMA como rodapé, evitando StopIteration.
    """

    tpl_path = os.path.join(os.path.dirname(__file__), "dominio_format.txt")
    with open(tpl_path, "r", encoding="latin-1") as f:
        tpl_lines = [l.rstrip("\n") for l in f]

    header  = tpl_lines[0]
    trailer = tpl_lines[-1]
    width   = len(header)

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"saida_dominio_{conta_banco}.txt")

    with open(out_path, "w", encoding="latin-1") as out:
        # cabeçalho
        out.write(header + "\n")

        for idx, row in df.iterrows():
            seq = str(idx + 1).zfill(9)

            # valida data
            data = pd.to_datetime(row["Data de Ocorrência"], errors="coerce")
            if pd.isna(data):
                raise ValueError(f"Data inválida na linha {idx+1}: {row['Data de Ocorrência']}")
            datastr = data.strftime("%d/%m/%Y")

            # registro 02
            rec02 = f"02{seq}X{datastr}"
            out.write(rec02.ljust(width, " ") + "\n")

            # registro 03
            tipo     = "1" if row["Valor"] < 0 else "2"
            contra   = str(conta_banco).zfill(9)
            cod_hist = "0000014000"
            cents    = abs(int(round(row["Valor"] * 100)))
            val_s    = str(cents).zfill(13)
            histo    = str(row["Complemento Histórico"] or "")[:50].ljust(50, " ")

            rec03 = (
                "03"
                + seq
                + contra
                + cod_hist
                + val_s
                + histo
            )
            out.write(rec03.ljust(width, " ") + "\n")

        # rodapé
        out.write(trailer + "\n")

    return out_path
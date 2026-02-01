import pandas as pd
import os

# Coloque seus arquivos .xlsx na mesma pasta deste script
files = [f for f in os.listdir('.') if f.endswith('.xlsx')]

for file in files:
    try:
        # Lê todas as abas da planilha
        xls = pd.ExcelFile(file)
        for sheet_name in xls.sheet_names:
            # Lê a aba
            df = pd.read_excel(xls, sheet_name=sheet_name)
            
            # Salva como CSV separado
            csv_name = f"{file.replace('.xlsx', '')}_{sheet_name}.csv"
            df.to_csv(csv_name, index=False)
            print(f"Criado: {csv_name}")
            
    except Exception as e:
        print(f"Erro em {file}: {e}")
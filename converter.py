import pandas as pd
import os

def limpar_planilhas():
    # Pega todos os arquivos .xlsx da pasta
    files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    
    print(f"Encontrados {len(files)} arquivos para processar...")

    for file in files:
        try:
            xls = pd.ExcelFile(file)
            for sheet_name in xls.sheet_names:
                # 1. Lê a aba inteira crua
                df_raw = pd.read_excel(xls, sheet_name=sheet_name, header=None)
                
                # 2. PROCURA A LINHA MÁGICA: Onde está a palavra "Vinho" ou "Safra"?
                # Isso descobre onde a tabela começa, ignorando os logos do topo
                start_row = None
                for idx, row in df_raw.iterrows():
                    # Converte a linha para string para procurar a palavra chave
                    row_str = row.astype(str).str.lower().values
                    if any('vinho' in str(x).lower() for x in row_str) and any('safra' in str(x).lower() for x in row_str):
                        start_row = idx
                        break
                
                if start_row is None:
                    print(f"⚠️  Pulei a aba '{sheet_name}' de {file} (Não achei tabela de vinhos)")
                    continue

                # 3. Recarrega a planilha usando a linha certa como cabeçalho
                df_clean = pd.read_excel(xls, sheet_name=sheet_name, header=start_row)
                
                # 4. Remove colunas vazias ou inúteis (Unamed)
                df_clean = df_clean.loc[:, ~df_clean.columns.str.contains('^Unnamed')]
                df_clean = df_clean.dropna(how='all') # Remove linhas vazias
                
                # 5. Salva o CSV Limpo
                clean_name = f"LIMPO_{file.replace('.xlsx', '')}_{sheet_name}.csv"
                df_clean.to_csv(clean_name, index=False, encoding='utf-8-sig')
                print(f"✅ Sucesso: {clean_name}")
                
        except Exception as e:
            print(f"❌ Erro crítico em {file}: {e}")

if __name__ == "__main__":
    limpar_planilhas()
    input("\nPressione ENTER para sair...")
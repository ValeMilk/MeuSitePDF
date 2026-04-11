import streamlit as st
import pandas as pd
import pdfplumber
import re
import io
import pyodbc
import warnings

warnings.filterwarnings("ignore")
st.set_page_config(page_title="Leitor e Validador ERP", page_icon="🧪", layout="wide")

st.title("🧪 Motor de Validação: Pedidos Vale Milk")
st.write("Versão 10.6: Corrigido filtro A00_ATIVO para aceitar NULL.")

CNPJ_FORNECEDOR_GRUPO = "02518353000294"

@st.cache_data(ttl=600)
def buscar_dados_erp():
    try:
        server = r'10.1.0.3\SQLSTANDARD'
        database = 'dbactions'
        username = 'analistarpt'
        password = 'mM=DU9lUd3C$qb@'
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        conn = pyodbc.connect(conn_str)

        df_produtos = pd.read_sql("SELECT CAST(E02_GTIN AS VARCHAR) AS ean, E02_ID AS id_produto, E02_DESC AS descricao FROM E02 WHERE E02_TIPO = 4 AND E02_ATIVO = 1 AND E02_ID <> 58", conn).drop_duplicates(subset=['ean'])

        # CORREÇÃO: A00_ATIVO = 1 OR A00_ATIVO IS NULL
        df_clientes = pd.read_sql("""
            SELECT 
                CAST(A00_CNPJ_CPF AS VARCHAR) AS cnpj,
                A00_ID AS id_cliente,
                A00_FANTASIA AS nome,
                A00_ID_A16 AS id_rede,
                A16.A16_DESC AS rede
            FROM A00
            LEFT JOIN A16 ON A00.A00_ID_A16 = A16.A16_ID
            WHERE (A00.A00_ATIVO = 1 OR A00.A00_ATIVO IS NULL)
              AND A00.A00_STATUS = 1
        """, conn).drop_duplicates(subset=['cnpj'])

        df_precos = pd.read_sql("SELECT E08_ID_A16 AS id_rede, E08_ID_E02 AS id_produto, E08_PRECO_01 AS preco_esperado FROM E08 WHERE E08_ATIVO = 1", conn).drop_duplicates(subset=['id_rede', 'id_produto'])

        for df in [df_produtos, df_clientes, df_precos]:
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.strip()

        df_clientes['cnpj'] = df_clientes['cnpj'].str.replace(r'\D', '', regex=True)

        conn.close()
        return df_clientes, df_produtos, df_precos
    except Exception as e:
        st.error(f"Erro na comunicação com o banco de dados: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_clientes_db, df_produtos_db, df_precos_db = buscar_dados_erp()

pedidos_pdf = st.file_uploader("Suba os arquivos PDF para validação", type="pdf", accept_multiple_files=True)

if st.button("EXECUTAR AUDITORIA", type="primary", width='stretch'):
    if not pedidos_pdf:
        st.warning("⚠️ Por favor, anexe os arquivos PDF.")
    elif df_precos_db.empty:
        st.error("❌ Base de dados offline.")
    else:
        with st.spinner("Auditando itens..."):
            dados_brutos = []

            for arquivo in pedidos_pdf:
                with pdfplumber.open(arquivo) as pdf:
                    cnpj_acumulado = "00000000000000"

                    for num_pag, pagina in enumerate(pdf.pages, start=1):
                        texto_pag = pagina.extract_text()
                        if not texto_pag:
                            continue

                        # =========================================================
                        # CAPTURA CIRÚRGICA: lê apenas linhas com "CNPJ:"
                        # =========================================================
                        cnpj_encontrado_na_pagina = None
                        for linha in texto_pag.split('\n'):
                            if 'CNPJ:' in linha:
                                matches = re.findall(r'\d{2}[\.\s]*\d{3}[\.\s]*\d{3}[\/\s]*\d{4}[-\s]*\d{2}', linha)
                                for m in matches:
                                    c_limpo = re.sub(r'\D', '', m)
                                    if c_limpo != CNPJ_FORNECEDOR_GRUPO:
                                        cnpj_encontrado_na_pagina = c_limpo

                        if cnpj_encontrado_na_pagina:
                            cnpj_acumulado = cnpj_encontrado_na_pagina
                        # =========================================================

                        for linha in texto_pag.split('\n'):
                            match_ean = re.search(r'\b(789\d{10})\b', linha)
                            if match_ean:
                                ean = str(match_ean.group(1)).strip()
                                l_limpa = linha.replace('.', '')
                                monetarios = re.findall(r'\d+,\d+', l_limpa)

                                if len(monetarios) >= 2:
                                    pr_unit_txt = monetarios[-2]
                                    parte_antes = l_limpa.split(pr_unit_txt)[0].strip()
                                    clean_parte = re.sub(r'[A-Za-z]+/?\d*', '', parte_antes)
                                    numeros = re.findall(r'\b\d+\b', clean_parte)

                                    try:
                                        qtd = int(numeros[-1])
                                    except:
                                        qtd = 0

                                    pr_unit = float(pr_unit_txt.replace(',', '.'))
                                    vl_total = float(monetarios[-1].replace(',', '.'))

                                    dados_brutos.append({
                                        "ARQUIVO": arquivo.name,
                                        "PÁGINA": num_pag,
                                        "CNPJ": cnpj_acumulado,
                                        "ean_key": ean,
                                        "QUANTIDADE": qtd,
                                        "PRECO PDF": pr_unit,
                                        "VALOR TT PDF": vl_total
                                    })

            if dados_brutos:
                df_base = pd.DataFrame(dados_brutos)

                df_v = pd.merge(df_base, df_produtos_db, left_on="ean_key", right_on="ean", how="left")
                df_v = pd.merge(df_v, df_clientes_db, left_on="CNPJ", right_on="cnpj", how="left")
                df_v = pd.merge(df_v, df_precos_db, on=["id_rede", "id_produto"], how="left")
                df_v = df_v.drop_duplicates()

                df_v['preco_esperado'] = pd.to_numeric(df_v['preco_esperado'], errors='coerce').fillna(0)
                df_v['VALOR TT CALCULADO'] = df_v['QUANTIDADE'] * df_v['preco_esperado']
                df_v['STATUS'] = df_v.apply(lambda r: "✅ OK" if r['preco_esperado'] > 0 and abs(r['PRECO PDF'] - r['preco_esperado']) < 0.01 else f"❌ DIF (TAB: {r['preco_esperado']})", axis=1)
                df_v['STATUS_FINAL'] = df_v.apply(lambda r: "✅ OK" if abs(r['VALOR TT CALCULADO'] - r['VALOR TT PDF']) < 0.05 else "❌ ERRO SOMA", axis=1)

                df_v = df_v.rename(columns={
                    "rede": "REDE", "id_cliente": "ID_CLIENTE", "nome": "CLIENTE",
                    "id_produto": "ID_PRODUTO", "descricao": "PRODUTO", "preco_esperado": "PRECO TABELA",
                    "ean_key": "EAN 13", "ARQUIVO": "PDF_ORIGEM"
                })

                cols = ["PDF_ORIGEM", "PÁGINA", "CNPJ", "REDE", "ID_CLIENTE", "CLIENTE", "EAN 13", "ID_PRODUTO", "PRODUTO", "QUANTIDADE", "PRECO PDF", "PRECO TABELA", "STATUS", "VALOR TT PDF", "VALOR TT CALCULADO", "STATUS_FINAL"]
                st.session_state['df_final'] = df_v[cols].sort_values(by=["PDF_ORIGEM", "PÁGINA", "REDE", "CLIENTE", "ID_PRODUTO"])

if 'df_final' in st.session_state:
    st.divider()
    col_busca, _ = st.columns([2, 2])
    with col_busca:
        termo_busca = st.text_input("🔍 Digite para filtrar (Cliente, Produto, EAN ou Status):", "")

    df_exibir = st.session_state['df_final']
    if termo_busca:
        mask = df_exibir.astype(str).apply(lambda x: x.str.contains(termo_busca, case=False)).any(axis=1)
        df_exibir = df_exibir[mask]

    st.success(f"✅ Exibindo {len(df_exibir)} itens na auditoria.")

    st.dataframe(
        df_exibir,
        use_container_width=True,
        hide_index=True,
        column_config={
            "PÁGINA": st.column_config.NumberColumn(format="%d"),
            "PRECO PDF": st.column_config.NumberColumn(format="R$ %.2f"),
            "PRECO TABELA": st.column_config.NumberColumn(format="R$ %.2f"),
            "VALOR TT PDF": st.column_config.NumberColumn(format="R$ %.2f"),
            "VALOR TT CALCULADO": st.column_config.NumberColumn(format="R$ %.2f"),
        }
    )

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_exibir.to_excel(writer, index=False, sheet_name='Auditoria')
    st.download_button("📥 BAIXAR EXCEL LIMPO", buffer.getvalue(), "auditoria_vale_milk.xlsx", width='stretch')
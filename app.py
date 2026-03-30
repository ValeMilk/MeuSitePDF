import streamlit as st
from pypdf import PdfReader, PdfWriter
import io
import base64
import re
from datetime import datetime, timedelta

# 1. Configuração da página
st.set_page_config(
    page_title="Agrupador Inteligente de PDFs",
    page_icon="logo.png",
    layout="wide"
)

# 2. Injeção de Design (CSS)
def set_background(image_file):
    try:
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        
        css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .stApp > header {{ background-color: transparent; }}
        h1, .subtitulo {{
            color: #ffffff !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.9);
        }}
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: #F8FAFC !important; 
            border-radius: 12px !important;
            border: 2px solid #CBD5E1 !important;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4) !important;
            padding: 15px;
        }}
        .texto-escuro {{
            color: #0F172A !important; 
            font-weight: 700 !important;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"] h3 {{
            color: #0F172A !important;
            font-weight: 800 !important;
            margin-bottom: -10px !important; 
        }}
        .status-header {{
            background-color: #1E40AF !important; 
            color: #FFFFFF !important;
            padding: 10px; text-align: center; font-weight: bold; border-radius: 8px; margin-bottom: 15px;
        }}
        .stButton > button {{
            background-color: #16A34A !important; 
            color: white !important;
            border-radius: 8px !important;
            font-weight: bold;
            padding: 12px !important;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except:
        pass

set_background("fundo.png")

# 3. Cabeçalho
st.markdown("<h1>Agrupador Inteligente de PDFs 📄</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitulo'>O sistema cruza os dados automaticamente e monta: Pedido > Nota > Boleto (por cliente).</p>", unsafe_allow_html=True)

# 4. Bloco de Identificação
with st.container(border=True):
    col_mot, col_carga = st.columns(2)
    with col_mot:
        st.markdown("<h3>🚚 Nome do Motorista:</h3>", unsafe_allow_html=True)
        motorista = st.text_input("", key="mot", label_visibility="collapsed")
    with col_carga:
        st.markdown("<h3>📦 Nº da Carga:</h3>", unsafe_allow_html=True)
        carga = st.text_input("", key="car", label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)

# 5. Colunas de Upload (Agora aceita múltiplos ou arquivo único)
col1, col2, col3 = st.columns(3)
with col1:
    with st.container(border=True):
        st.markdown("<h3>1. Pedidos</h3>", unsafe_allow_html=True)
        arq_pedidos = st.file_uploader("Pedidos", type="pdf", accept_multiple_files=True, key="ped", label_visibility="collapsed")
with col2:
    with st.container(border=True):
        st.markdown("<h3>2. Notas Fiscais</h3>", unsafe_allow_html=True)
        arq_notas = st.file_uploader("Notas", type="pdf", accept_multiple_files=True, key="nf", label_visibility="collapsed")
with col3:
    with st.container(border=True):
        st.markdown("<h3>3. Boletos</h3>", unsafe_allow_html=True)
        arq_boletos = st.file_uploader("Boletos", type="pdf", accept_multiple_files=True, key="bol", label_visibility="collapsed")

# 6. Lógica de Processamento Inteligente
agrupamentos = {}

def extrair_e_agrupar(lista_arquivos, tipo_doc):
    if not lista_arquivos: return
    
    for arquivo in lista_arquivos:
        leitor = PdfReader(arquivo)
        numero_ativo = None
        
        for pagina in leitor.pages:
            texto = pagina.extract_text() or ""
            numero_encontrado = None
            
            if tipo_doc == 'pedido':
                match = re.search(r'(\d+)\s*\d*Doc\.:', texto, re.IGNORECASE)
                if not match: match = re.search(r'Doc\.?:\s*(\d+)', texto, re.IGNORECASE)
                if match: numero_encontrado = match.group(1)
            
            elif tipo_doc == 'nota':
                match = re.search(r'(\d+)\s*S[ÉE]RIE', texto, re.IGNORECASE)
                if not match: match = re.search(r'NF-e\s*(\d+)', texto, re.IGNORECASE)
                if match: numero_encontrado = match.group(1)
            
            elif tipo_doc == 'boleto':
                # Busca por chaves já existentes (Pedidos/Notas)
                chaves_conhecidas = list(agrupamentos.keys())
                for chave in chaves_conhecidas:
                    if re.search(r'\b' + re.escape(chave) + r'\b', texto):
                        numero_encontrado = chave
                        break
                # Plano B: Nr. do Documento
                if not numero_encontrado:
                    match = re.search(r'Nr\.?\s*do\s*Documento\D*(\d+)', texto, re.IGNORECASE)
                    if match: numero_encontrado = match.group(1)

            if numero_encontrado:
                numero_ativo = numero_encontrado
            
            if numero_ativo:
                if numero_ativo not in agrupamentos:
                    agrupamentos[numero_ativo] = {'pedido': [], 'nota': [], 'boleto': []}
                agrupamentos[numero_ativo][tipo_doc].append(pagina)

# 7. Interface de Status e Botão
faltam_dados = motorista.strip() == "" or carga.strip() == ""
btn_disabled = faltam_dados or (not arq_pedidos and not arq_notas and not arq_boletos)

if st.button("PROCESSAR E JUNTAR PDFs", use_container_width=True, disabled=btn_disabled):
    with st.spinner("Analisando documentos e cruzando chaves..."):
        # Processa na ordem para garantir que o Pedido crie a chave primeiro
        extrair_e_agrupar(arq_pedidos, 'pedido')
        extrair_e_agrupar(arq_notas, 'nota')
        extrair_e_agrupar(arq_boletos, 'boleto')
        
        if not agrupamentos:
            st.error("Nenhuma chave de ligação encontrada nos PDFs.")
        else:
            merger = PdfWriter()
            # Ordena as chaves para que o PDF final tenha uma ordem lógica de clientes
            for num in sorted(agrupamentos.keys()):
                docs = agrupamentos[num]
                for p in docs['pedido']: merger.add_page(p)
                for p in docs['nota']: merger.add_page(p)
                for p in docs['boleto']: merger.add_page(p)
            
            output = io.BytesIO()
            merger.write(output)
            merger.close()
            output.seek(0)
            
            st.balloons()
            st.success(f"Sucesso! {len(agrupamentos)} grupos (Pedido>NF>Boleto) organizados.")
            
            agora = (datetime.utcnow() - timedelta(hours=3)).strftime("%d-%m-%Y-%Hh%M")
            nome_final = f"{motorista.strip().upper()} (CARGA {carga.strip()}) - {agora}.pdf"
            
            st.download_button(
                label=f"📥 BAIXAR: {nome_final}",
                data=output,
                file_name=nome_final,
                mime="application/pdf",
                use_container_width=True
            )

if faltam_dados:
    st.info("💡 Preencha o motorista e a carga para liberar o processamento.")
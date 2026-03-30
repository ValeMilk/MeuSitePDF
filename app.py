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

# 2. Injeção de Design (CSS Original Restaurado)
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
            background-color: rgba(248, 250, 252, 0.15) !important; 
            border-radius: 12px !important;
            border: 1px solid rgba(203, 213, 225, 0.3) !important;
            backdrop-filter: blur(10px);
            padding: 15px;
        }}

        /* Inputs Brancos conforme imagem */
        div[data-testid="stTextInput"] input {{
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border-radius: 6px !important;
            font-weight: bold !important;
        }}

        .status-header {{
            background-color: #1E40AF !important; 
            color: #FFFFFF !important;
            padding: 10px; 
            text-align: center; 
            font-weight: bold; 
            border-radius: 8px; 
            margin-bottom: 15px;
        }}

        .stButton > button {{
            background-color: #16A34A !important; 
            color: white !important;
            border-radius: 8px !important;
            font-weight: bold;
            padding: 12px !important;
        }}
        
        .texto-branco {{ color: #ffffff !important; font-weight: 600; }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except:
        pass

set_background("fundo.png")

# 3. Cabeçalho
st.markdown("<h1>Agrupador Inteligente de PDFs 📄</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitulo'>Envie os ficheiros completos. O sistema vai montar o PDF final na ordem: Pedido > Nota Fiscal > Boleto.</p>", unsafe_allow_html=True)

# 4. Bloco de Identificação
with st.container(border=True):
    col_mot, col_carga = st.columns(2)
    with col_mot:
        st.markdown("<h3 style='color:white;'>🚚 Nome do Motorista:</h3>", unsafe_allow_html=True)
        motorista = st.text_input("", key="mot", label_visibility="collapsed")
    with col_carga:
        st.markdown("<h3 style='color:white;'>📦 Nº da Carga:</h3>", unsafe_allow_html=True)
        carga = st.text_input("", key="car", label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)

# 5. Colunas de Upload
col1, col2, col3 = st.columns(3)
with col1:
    with st.container(border=True):
        st.markdown("<h3 style='color:white;'>1. Pedidos</h3>", unsafe_allow_html=True)
        pedidos = st.file_uploader("Upload Pedidos", type="pdf", accept_multiple_files=True, key="ped", label_visibility="collapsed")
with col2:
    with st.container(border=True):
        st.markdown("<h3 style='color:white;'>2. Notas Fiscais</h3>", unsafe_allow_html=True)
        notas = st.file_uploader("Upload Notas", type="pdf", accept_multiple_files=True, key="nf", label_visibility="collapsed")
with col3:
    with st.container(border=True):
        st.markdown("<h3 style='color:white;'>3. Boletos</h3>", unsafe_allow_html=True)
        boletos = st.file_uploader("Upload Boletos", type="pdf", accept_multiple_files=True, key="bol", label_visibility="collapsed")

# 6. Status de Processamento (Barra Azul da Imagem)
qtd_ped = len(pedidos) if pedidos else 0
qtd_nf = len(notas) if notas else 0
qtd_bol = len(boletos) if boletos else 0
progresso = int(((1 if qtd_ped > 0 else 0) + (1 if qtd_nf > 0 else 0) + (1 if qtd_bol > 0 else 0)) / 3 * 100)

st.markdown("<br>", unsafe_allow_html=True)
with st.container(border=True):
    st.markdown('<div class="status-header">Processing Status</div>', unsafe_allow_html=True)
    sc1, sc2 = st.columns([2, 1])
    with sc1:
        st.progress(progresso)
        st.markdown(f"<span class='texto-branco'>{progresso}%</span>", unsafe_allow_html=True)
    with sc2:
        st.markdown(f"""<div style='color:white; font-size:12px;'>
            • Pedidos: {'Recebido' if qtd_ped > 0 else 'Aguardando...'}<br>
            • Notas: {'Recebido' if qtd_nf > 0 else 'Aguardando...'}<br>
            • Boletos: {'Recebido' if qtd_bol > 0 else 'Aguardando...'}
        </div>""", unsafe_allow_html=True)

# 7. Alertas e Botão
faltam_dados = motorista.strip() == "" or carga.strip() == ""
if faltam_dados:
    st.warning("⚠️ Atenção: Preencha o Nome do Motorista e o Nº da Carga.")

if st.button("PROCESSAR E JUNTAR PDFs", use_container_width=True, disabled=faltam_dados):
    agrupamentos = {}
    
    def processar(files, tipo):
        if not files: return
        for f in files:
            reader = PdfReader(f)
            num_ativo = None
            for page in reader.pages:
                txt = page.extract_text() or ""
                num = None
                if tipo == 'pedido':
                    m = re.search(r'(\d+)\s*\d*Doc\.:', txt, re.IGNORECASE) or re.search(r'Doc\.?:\s*(\d+)', txt, re.IGNORECASE)
                    if m: num = m.group(1)
                elif tipo == 'nota':
                    m = re.search(r'(\d+)\s*S[ÉE]RIE', txt, re.IGNORECASE) or re.search(r'NF-e\s*(\d+)', txt, re.IGNORECASE)
                    if m: num = m.group(1)
                elif tipo == 'boleto':
                    for c in list(agrupamentos.keys()):
                        if re.search(r'\b' + re.escape(c) + r'\b', txt):
                            num = c; break
                    if not num:
                        m = re.search(r'Nr\.?\s*do\s*Documento\D*(\d+)', txt, re.IGNORECASE)
                        if m: num = m.group(1)
                
                if num: num_ativo = num
                if num_ativo:
                    if num_ativo not in agrupamentos: agrupamentos[num_ativo] = {'pedido':[], 'nota':[], 'boleto':[]}
                    agrupamentos[num_ativo][tipo].append(page)

    processar(pedidos, 'pedido')
    processar(notas, 'nota')
    processar(boletos, 'boleto')

    if agrupamentos:
        merger = PdfWriter()
        for k in sorted(agrupamentos.keys()):
            for p in agrupamentos[k]['pedido']: merger.add_page(p)
            for p in agrupamentos[k]['nota']: merger.add_page(p)
            for p in agrupamentos[k]['boleto']: merger.add_page(p)
        
        out = io.BytesIO()
        merger.write(out)
        merger.close()
        out.seek(0)
        
        st.success("Agrupamento concluído!")
        agora = (datetime.utcnow() - timedelta(hours=3)).strftime("%d-%m-%Y-%Hh%M")
        nome = f"{motorista.upper()} ({carga}) - {agora}.pdf"
        st.download_button(f"📥 BAIXAR {nome}", out, nome, "application/pdf", use_container_width=True)
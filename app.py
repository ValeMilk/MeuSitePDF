import streamlit as st
from pypdf import PdfWriter
import io
import base64
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

        .texto-escuro, .texto-escuro p, .texto-escuro span, .texto-escuro li, .texto-escuro b {{
            color: #0F172A !important; 
            font-weight: 700 !important;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"] h3 {{
            color: #0F172A !important;
            font-weight: 800 !important;
            margin-bottom: -10px !important; 
        }}

        div[data-testid="stTextInput"] input {{
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #94A3B8 !important;
            border-radius: 6px !important;
            font-weight: bold !important;
        }}

        div[data-testid="stFileUploader"] {{
            background-color: #F1F5F9 !important;
            border: 2px dashed #64748B !important;
            border-radius: 8px;
            margin-top: 15px;
        }}

        div[data-testid="stFileUploader"] button {{
            background-color: #2563EB !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: bold;
        }}
        div[data-testid="stFileUploader"] button:hover {{ background-color: #1D4ED8 !important; }}

        .status-header {{
            background-color: #1E40AF !important; 
            color: #FFFFFF !important;
            padding: 10px; 
            text-align: center; 
            font-weight: bold; 
            border-radius: 8px; 
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}

        .stButton > button {{
            background-color: #16A34A !important; 
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: bold;
            padding: 12px !important;
            font-size: 16px !important;
        }}
        .stButton > button:hover {{ background-color: #15803D !important; }}
        .stButton > button:disabled {{ background-color: #94A3B8 !important; color: #F8FAFC !important; }}
        
        .stProgress > div > div > div {{ background-color: #2563EB !important; }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ Imagem 'fundo.png' não encontrada.")

set_background("fundo.png")

# 3. Cabeçalho Principal
st.markdown("<h1>Agrupador Inteligente de PDFs 📄</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitulo'>Envie os ficheiros completos. O sistema vai montar o PDF final na ordem: Pedido > Nota Fiscal > Boleto.</p>", unsafe_allow_html=True)

# 4. Bloco de Identificação (Títulos Grandes)
with st.container(border=True):
    col_mot, col_carga = st.columns(2)
    
    with col_mot:
        st.markdown("<h3>🚚 Nome do Motorista:</h3>", unsafe_allow_html=True)
        motorista = st.text_input("", key="mot", label_visibility="collapsed")
        
    with col_carga:
        st.markdown("<h3>📦 Nº da Carga:</h3>", unsafe_allow_html=True)
        carga = st.text_input("", key="car", label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)

# 5. As 3 Colunas principais
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("<h3>1. Pedidos</h3>", unsafe_allow_html=True)
        st.markdown("<div class='texto-escuro' style='font-size:12px;'>Upload Arquivo de Pedidos</div>", unsafe_allow_html=True)
        pedidos = st.file_uploader("", type="pdf", accept_multiple_files=True, key="ped", label_visibility="collapsed")

with col2:
    with st.container(border=True):
        st.markdown("<h3>2. Notas Fiscais</h3>", unsafe_allow_html=True)
        st.markdown("<div class='texto-escuro' style='font-size:12px;'>Upload Arquivo de Notas</div>", unsafe_allow_html=True)
        notas = st.file_uploader("", type="pdf", accept_multiple_files=True, key="nf", label_visibility="collapsed")

with col3:
    with st.container(border=True):
        st.markdown("<h3>3. Boletos</h3>", unsafe_allow_html=True)
        st.markdown("<div class='texto-escuro' style='font-size:12px;'>Upload Arquivo de Boletos</div>", unsafe_allow_html=True)
        boletos = st.file_uploader("", type="pdf", accept_multiple_files=True, key="bol", label_visibility="collapsed")

# 6. Lógica visual e Contagem
qtd_pedidos = len(pedidos) if pedidos else 0
qtd_notas = len(notas) if notas else 0
qtd_boletos = len(boletos) if boletos else 0

total_arquivos = qtd_pedidos + qtd_notas + qtd_boletos
total_categorias = (1 if qtd_pedidos > 0 else 0) + (1 if qtd_notas > 0 else 0) + (1 if qtd_boletos > 0 else 0)
progresso = int((total_categorias / 3) * 100)

ped_status = f"Recebido ({qtd_pedidos} ficheiro(s))" if qtd_pedidos > 0 else "Aguardando..."
nf_status = f"Recebido ({qtd_notas} ficheiro(s))" if qtd_notas > 0 else "Aguardando..."
bol_status = f"Recebido ({qtd_boletos} ficheiro(s))" if qtd_boletos > 0 else "Aguardando..."

st.markdown("<br>", unsafe_allow_html=True)

# 7. Caixa de Status
with st.container(border=True):
    st.markdown('<div class="status-header">Processing Status</div>', unsafe_allow_html=True)
    
    stat_col1, stat_col2 = st.columns([2, 1])
    
    with stat_col1:
        st.progress(progresso)
        st.markdown(f"<div class='texto-escuro' style='font-size: 24px;'>{progresso}%</div>", unsafe_allow_html=True)
        
        if progresso == 100:
            st.markdown("<div class='texto-escuro'>✅ Todos os uploads recebidos! Pronto para processar.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='texto-escuro'>⏳ Aguardando uploads adicionais...</div>", unsafe_allow_html=True)
            
    with stat_col2:
        st.markdown(f"""
        <div class='texto-escuro'>
            <ul style='font-size: 14px; line-height: 1.6; list-style-type: none; padding-left: 0;'>
                <li>▪️ <b>Pedidos:</b> {ped_status}</li>
                <li>▪️ <b>Notas Fiscais:</b> {nf_status}</li>
                <li>▪️ <b>Boletos:</b> {bol_status}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# 8. TRAVA DE SEGURANÇA E CAIXA DE ALERTA VERMELHA CUSTOMIZADA
faltam_dados = motorista.strip() == "" or carga.strip() == ""
faltam_arquivos = total_arquivos < 2
botao_bloqueado = faltam_dados or faltam_arquivos

# Caixa de erro construída do zero (Fundo vermelho claro, letra vermelho escuro)
alerta_html = """
<div style="background-color: #FEE2E2; color: #991B1B; padding: 15px; border-radius: 8px; border: 2px solid #FCA5A5; font-weight: bold; margin-bottom: 15px; font-size: 15px;">
    {mensagem}
</div>
"""

if faltam_dados:
    st.markdown(alerta_html.format(mensagem="⚠️ Atenção: Preencha o Nome do Motorista e o Nº da Carga."), unsafe_allow_html=True)
elif faltam_arquivos:
    st.markdown(alerta_html.format(mensagem="⚠️ Atenção: Anexe pelo menos 2 arquivos no total para poder realizar o agrupamento."), unsafe_allow_html=True)

# Botão Final
if st.button("PROCESSAR E JUNTAR PDFs", use_container_width=True, disabled=botao_bloqueado):
    if pedidos or notas or boletos:
        merger = PdfWriter()
        try:
            pedidos_ord = sorted(pedidos, key=lambda x: x.name) if pedidos else []
            notas_ord = sorted(notas, key=lambda x: x.name) if notas else []
            boletos_ord = sorted(boletos, key=lambda x: x.name) if boletos else []
            
            for p in pedidos_ord: merger.append(p)
            for n in notas_ord: merger.append(n)
            for b in boletos_ord: merger.append(b)
                
            output = io.BytesIO()
            merger.write(output)
            merger.close()
            output.seek(0)
            
            st.balloons()
            st.success("PDFs agrupados com sucesso! Clique no botão abaixo para descarregar o ficheiro.")
            
            hora_correta = datetime.utcnow() - timedelta(hours=3)
            agora = hora_correta.strftime("%d-%m-%Y-%H:%M") 
            
            nome_mot = motorista.strip().upper()
            num_carga = carga.strip()
            nome_final_pdf = f"{nome_mot} ({num_carga}) - {agora}.pdf"
            
            st.download_button(
                label=f"📥 DESCARREGAR {nome_final_pdf}",
                data=output,
                file_name=nome_final_pdf,
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Erro ao processar: {e}")
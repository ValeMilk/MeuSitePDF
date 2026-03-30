import streamlit as st
from pypdf import PdfWriter
import io
import base64
from datetime import datetime # Importação nova para puxar a hora exata

# 1. Configuração da página
st.set_page_config(
    page_title="Agrupador Inteligente de PDFs",
    page_icon="logo.png",
    layout="wide"
)

# 2. Injeção pesada de Design (CSS)
def set_background(image_file):
    try:
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        
        css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        
        .stApp > header {{ background-color: transparent; }}
        h1, p {{ color: white; }}

        /* Estilo dos Cards Bege */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: #F4F2E9 !important;
            border-radius: 12px !important;
            border: 2px solid #D5DBE1 !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            padding: 10px;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"] p, 
        div[data-testid="stVerticalBlockBorderWrapper"] h3, 
        div[data-testid="stVerticalBlockBorderWrapper"] h1,
        div[data-testid="stVerticalBlockBorderWrapper"] span,
        div[data-testid="stVerticalBlockBorderWrapper"] li,
        div[data-testid="stVerticalBlockBorderWrapper"] label {{
            color: #1B222C !important;
        }}

        /* O botão "Browse files" em azul escuro */
        div[data-testid="stFileUploader"] button {{
            background-color: #143A66 !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
        }}
        div[data-testid="stFileUploader"] button:hover {{ background-color: #0d2745 !important; }}
        div[data-testid="stFileUploader"] {{ background-color: transparent !important; }}

        /* Botão gigante de Processar em Preto/Cinza Escuro */
        .stButton > button {{
            background-color: #2D3139 !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: bold;
            padding: 10px !important;
            margin-top: 15px;
        }}
        .stButton > button:hover {{ background-color: #1a1c21 !important; }}
        
        /* Cor da Barra de Progresso */
        .stProgress > div > div > div {{ background-color: #143A66 !important; }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ Imagem 'fundo.jpg' não encontrada. Coloque-a na mesma pasta do app.py.")

set_background("fundo.jpg")

# 3. Cabeçalho
st.markdown("<h1>Agrupador Inteligente de PDFs 📄</h1>", unsafe_allow_html=True)
st.write("Envie os arquivos completos. O sistema vai montar o PDF final na ordem: Pedido > Nota Fiscal > Boleto.")

# NOVO: Bloco de Identificação (Motorista e Carga)
with st.container(border=True):
    col_mot, col_carga = st.columns(2)
    with col_mot:
        motorista = st.text_input("🚚 Nome do Motorista:")
    with col_carga:
        carga = st.text_input("📦 Nº da Carga:")

st.markdown("<br>", unsafe_allow_html=True)

# 4. As 3 Colunas principais
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("### 1. Pedidos")
        st.markdown("<p style='font-size:12px; margin-top:-15px;'>Upload Arquivo de Pedidos</p>", unsafe_allow_html=True)
        pedidos = st.file_uploader("", type="pdf", accept_multiple_files=True, key="ped", label_visibility="collapsed")

with col2:
    with st.container(border=True):
        st.markdown("### 2. Notas Fiscais")
        st.markdown("<p style='font-size:12px; margin-top:-15px;'>Upload Arquivo de Notas</p>", unsafe_allow_html=True)
        notas = st.file_uploader("", type="pdf", accept_multiple_files=True, key="nf", label_visibility="collapsed")

with col3:
    with st.container(border=True):
        st.markdown("### 3. Boletos")
        st.markdown("<p style='font-size:12px; margin-top:-15px;'>Upload Arquivo de Boletos</p>", unsafe_allow_html=True)
        boletos = st.file_uploader("", type="pdf", accept_multiple_files=True, key="bol", label_visibility="collapsed")

# 5. Lógica visual da Barra de Status
qtd_pedidos = len(pedidos) if pedidos else 0
qtd_notas = len(notas) if notas else 0
qtd_boletos = len(boletos) if boletos else 0

total_categorias = (1 if qtd_pedidos > 0 else 0) + (1 if qtd_notas > 0 else 0) + (1 if qtd_boletos > 0 else 0)
progresso = int((total_categorias / 3) * 100)

ped_status = f"Recebido ({qtd_pedidos} arquivo(s))" if qtd_pedidos > 0 else "Aguardando..."
nf_status = f"Recebido ({qtd_notas} arquivo(s))" if qtd_notas > 0 else "Aguardando..."
bol_status = f"Recebido ({qtd_boletos} arquivo(s))" if qtd_boletos > 0 else "Aguardando..."

st.markdown("<br>", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("""
        <div style="background-color: #143A66; color: white !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 8px 8px 0 0; margin: -10px -10px 15px -10px;">
            Processing Status
        </div>
    """, unsafe_allow_html=True)
    
    stat_col1, stat_col2 = st.columns([2, 1])
    
    with stat_col1:
        st.progress(progresso)
        st.markdown(f"<span style='font-size: 20px; font-weight:bold;'>{progresso}%</span>", unsafe_allow_html=True)
        if progresso == 100:
            st.markdown("✅ **Todos os uploads recebidos! Pronto para processar.**")
        else:
            st.markdown("⏳ Aguardando uploads adicionais...")
            
    with stat_col2:
        st.markdown(f"""
        <ul style='font-size: 14px; line-height: 1.6; list-style-type: none; padding-left: 0;'>
            <li>▪️ <b>Pedidos:</b> {ped_status}</li>
            <li>▪️ <b>Notas Fiscais:</b> {nf_status}</li>
            <li>▪️ <b>Boletos:</b> {bol_status}</li>
        </ul>
        """, unsafe_allow_html=True)

# 6. Botão Final de Processamento e Download
if st.button("PROCESSAR E JUNTAR PDFs", use_container_width=True):
    if pedidos or notas or boletos:
        merger = PdfWriter()
        try:
            # LÓGICA CORRIGIDA: Intercalando um a um (Pedido -> Nota -> Boleto)
            max_arquivos = max(qtd_pedidos, qtd_notas, qtd_boletos)
            
            for i in range(max_arquivos):
                if i < qtd_pedidos: merger.append(pedidos[i])
                if i < qtd_notas: merger.append(notas[i])
                if i < qtd_boletos: merger.append(boletos[i])
                
            output = io.BytesIO()
            merger.write(output)
            merger.close()
            output.seek(0)
            
            st.balloons()
            st.success("PDFs agrupados com sucesso! Clique no botão abaixo para baixar.")
            
            # NOVO: Gerando o nome do arquivo dinâmico
            agora = datetime.now().strftime("%d-%m-%Y-%H:%M") # Formata a data e hora
            nome_mot = motorista.strip().upper() if motorista else "MOTORISTA_NAO_INFORMADO"
            num_carga = carga.strip() if carga else "SEM_CARGA"
            
            nome_final_pdf = f"{nome_mot} ({num_carga}) - {agora}.pdf"
            
            st.download_button(
                label=f"📥 BAIXAR {nome_final_pdf}",
                data=output,
                file_name=nome_final_pdf,
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Erro ao processar: {e}")
    else:
        st.error("Por favor, faça o upload de pelo menos um arquivo antes de processar.")
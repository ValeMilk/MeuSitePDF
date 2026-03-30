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

# 2. Injeção de Design (CSS) - Efeito Light Glass (Contraste Perfeito)
def set_background(image_file):
    try:
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        
        css = f"""
        <style>
        /* Fundo principal com a sua imagem */
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        
        .stApp > header {{ background-color: transparent; }}
        
        /* Títulos principais (Brancos com sombra escura para leitura no fundo) */
        h1, h2, .subtitulo {{
            color: #ffffff !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        }}

        /* Caixas principais (Cards) - Vidro Branco Fosco (Para a fonte não sumir!) */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: rgba(255, 255, 255, 0.90) !important; 
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
            padding: 15px;
        }}

        /* FORÇANDO Textos DENTRO dos cards a serem ESCUROS */
        div[data-testid="stVerticalBlockBorderWrapper"] p, 
        div[data-testid="stVerticalBlockBorderWrapper"] span,
        div[data-testid="stVerticalBlockBorderWrapper"] li,
        div[data-testid="stVerticalBlockBorderWrapper"] label,
        div[data-testid="stVerticalBlockBorderWrapper"] h3 {{
            color: #0F172A !important; 
            font-weight: 600 !important;
        }}

        /* Caixas de digitação */
        div[data-testid="stTextInput"] input {{
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 6px !important;
        }}

        /* Área de Upload (Tracejado) */
        div[data-testid="stFileUploader"] {{
            background-color: rgba(241, 245, 249, 0.6) !important;
            border: 1px dashed #64748B !important;
            border-radius: 8px;
        }}

        /* Botão "Browse files" em azul */
        div[data-testid="stFileUploader"] button {{
            background-color: #2563EB !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            font-weight: bold;
        }}
        div[data-testid="stFileUploader"] button:hover {{ background-color: #1D4ED8 !important; }}

        /* Barra Azul do Título "Processing Status" */
        .status-header {{
            background-color: #1E40AF; 
            color: white !important; 
            padding: 10px; 
            text-align: center; 
            font-weight: bold; 
            border-radius: 8px; 
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}

        /* Botão gigante de Processar */
        .stButton > button {{
            background-color: #16A34A !important; /* Verde */
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: bold;
            padding: 12px !important;
            font-size: 16px !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        .stButton > button:hover {{ background-color: #15803D !important; }}
        
        /* Botão bloqueado (Cinza) */
        .stButton > button:disabled {{
            background-color: #94A3B8 !important;
            color: #F1F5F9 !important;
        }}
        
        .stProgress > div > div > div {{ background-color: #2563EB !important; }}
        
        /* Textos dos alertas (Avisos Amarelos/Vermelhos) */
        div[data-testid="stAlert"] p, div[data-testid="stAlert"] span {{
            color: #0F172A !important;
            font-weight: bold;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ Imagem 'fundo.png' não encontrada. Coloque-a na mesma pasta do app.py.")

set_background("fundo.png")

# 3. Cabeçalho
st.markdown("<h1>Agrupador Inteligente de PDFs 📄</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitulo'>Envie os ficheiros completos. O sistema vai montar o PDF final na ordem: Pedido > Nota Fiscal > Boleto.</p>", unsafe_allow_html=True)

# Bloco de Identificação (Motorista e Carga)
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

# 5. Lógica visual e Contagem
qtd_pedidos = len(pedidos) if pedidos else 0
qtd_notas = len(notas) if notas else 0
qtd_boletos = len(boletos) if boletos else 0

total_arquivos = qtd_pedidos + qtd_notas + qtd_boletos # Conta quantos arquivos existem no total

total_categorias = (1 if qtd_pedidos > 0 else 0) + (1 if qtd_notas > 0 else 0) + (1 if qtd_boletos > 0 else 0)
progresso = int((total_categorias / 3) * 100)

ped_status = f"Recebido ({qtd_pedidos} ficheiro(s))" if qtd_pedidos > 0 else "Aguardando..."
nf_status = f"Recebido ({qtd_notas} ficheiro(s))" if qtd_notas > 0 else "Aguardando..."
bol_status = f"Recebido ({qtd_boletos} ficheiro(s))" if qtd_boletos > 0 else "Aguardando..."

st.markdown("<br>", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown('<div class="status-header">Processing Status</div>', unsafe_allow_html=True)
    
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


# 6. TRAVA DE SEGURANÇA E BOTÃO DE PROCESSAMENTO
faltam_dados = motorista.strip() == "" or carga.strip() == ""
faltam_arquivos = total_arquivos < 2 # BLOQUEIO: Exige pelo menos 2 arquivos no total para liberar a junção

# O botão fica bloqueado se faltarem textos ou se houver menos de 2 arquivos
botao_bloqueado = faltam_dados or faltam_arquivos

if faltam_dados:
    st.warning("⚠️ Atenção: Preencha o Nome do Motorista e o Nº da Carga.")
elif faltam_arquivos:
    st.warning("⚠️ Atenção: Anexe pelo menos 2 arquivos no total para poder realizar o agrupamento.")

if st.button("PROCESSAR E JUNTAR PDFs", use_container_width=True, disabled=botao_bloqueado):
    if pedidos or notas or boletos:
        merger = PdfWriter()
        try:
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
            st.success("PDFs agrupados com sucesso! Clique no botão abaixo para descarregar o ficheiro.")
            
            hora_correta = datetime.utcnow() - timedelta(hours=3)
            agora = hora_correta.strftime("%d-%m-%Y-%H:%M") 
            
            nome_mot = motorista.strip().upper()
            num_carga = carga.strip()
            
            nome_final_pdf = f"{nome_mot} ({num_carga}) - {agora}.pdf"
            
            st.download_button(
                label=f"📥 Baixar arquivo: {nome_final_pdf}",
                data=output,
                file_name=nome_final_pdf,
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Erro ao processar: {e}")
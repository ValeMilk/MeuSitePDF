import streamlit as st
from pypdf import PdfReader, PdfWriter
import io
import base64
import re
from datetime import datetime, timedelta

# 1. Configuração da página
st.set_page_config(page_title="Agrupador Inteligente de PDFs", page_icon="logo.png", layout="wide")

# 2. Design (CSS Original)
def set_background(image_file):
    try:
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        css = f"""
        <style>
        .stApp {{ background-image: url("data:image/png;base64,{encoded_string}"); background-size: cover; background-position: center; background-attachment: fixed; }}
        h1, .subtitulo {{ color: #ffffff !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.9); }}
        div[data-testid="stVerticalBlockBorderWrapper"] {{ background-color: rgba(248, 250, 252, 0.15) !important; border-radius: 12px !important; border: 1px solid rgba(203, 213, 225, 0.3) !important; backdrop-filter: blur(10px); padding: 15px; }}
        div[data-testid="stTextInput"] input {{ background-color: #FFFFFF !important; color: #0F172A !important; font-weight: bold !important; height: 45px; }}
        .status-header {{ background-color: #1E40AF !important; color: #FFFFFF !important; padding: 10px; text-align: center; font-weight: bold; border-radius: 8px; margin-bottom: 15px; }}
        .texto-branco {{ color: #ffffff !important; font-weight: 700; text-shadow: 1px 1px 2px black; }}
        
        /* Estilo do Botão Principal */
        .stButton > button {{
            background-color: #16A34A !important;
            color: white !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            height: 50px !important;
            width: 100% !important;
            border: none !important;
            font-size: 18px !important;
        }}
        .stButton > button:hover {{ background-color: #15803D !important; }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except: pass

set_background("fundo.png")

st.markdown("<h1>Agrupador Inteligente de PDFs 📄</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitulo'>Envie os ficheiros completos. O sistema vai montar o PDF final na ordem: Pedido > Nota Fiscal > Boleto.</p>", unsafe_allow_html=True)

# 3. Identificação
with st.container(border=True):
    col_mot, col_carga = st.columns(2)
    with col_mot:
        st.markdown("<h3 style='color:white; margin-bottom:5px;'>🚚 Nome do Motorista:</h3>", unsafe_allow_html=True)
        motorista = st.text_input("Motorista", key="mot", label_visibility="collapsed")
    with col_carga:
        st.markdown("<h3 style='color:white; margin-bottom:5px;'>📦 Nº da Carga:</h3>", unsafe_allow_html=True)
        carga = st.text_input("Carga", key="car", label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)

# 4. Uploads
col1, col2, col3 = st.columns(3)
with col1:
    with st.container(border=True):
        st.markdown("<h3 style='color:white;'>1. Pedidos</h3>", unsafe_allow_html=True)
        arq_ped = st.file_uploader("Upload Pedidos", type="pdf", accept_multiple_files=True, key="up_ped", label_visibility="collapsed")
with col2:
    with st.container(border=True):
        st.markdown("<h3 style='color:white;'>2. Notas Fiscais</h3>", unsafe_allow_html=True)
        arq_nf = st.file_uploader("Upload Notas", type="pdf", accept_multiple_files=True, key="up_nf", label_visibility="collapsed")
with col3:
    with st.container(border=True):
        st.markdown("<h3 style='color:white;'>3. Boletos</h3>", unsafe_allow_html=True)
        arq_bol = st.file_uploader("Upload Boletos", type="pdf", accept_multiple_files=True, key="up_bol", label_visibility="collapsed")

# 5. Barra de Status
qtd_ped = len(arq_ped) if arq_ped else 0
qtd_nf = len(arq_nf) if arq_nf else 0
qtd_bol = len(arq_bol) if arq_bol else 0
categorias_preenchidas = (1 if qtd_ped > 0 else 0) + (1 if qtd_nf > 0 else 0) + (1 if qtd_bol > 0 else 0)
progresso = int((categorias_preenchidas / 3) * 100)

st.markdown("<br>", unsafe_allow_html=True)
with st.container(border=True):
    st.markdown('<div class="status-header">Processing Status</div>', unsafe_allow_html=True)
    sc1, sc2 = st.columns([2, 1])
    with sc1:
        st.progress(progresso)
        st.markdown(f"<div class='texto-branco' style='font-size: 24px;'>{progresso}%</div>", unsafe_allow_html=True)
        if progresso == 100:
            st.markdown("<div class='texto-branco'>✅ Todos os uploads recebidos! Pronto para processar.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='texto-branco'>⏳ Aguardando uploads adicionais...</div>", unsafe_allow_html=True)
    with sc2:
        st.markdown(f"""<div class='texto-branco' style='font-size: 14px; line-height: 1.8;'>
            ▪️ <b>Pedidos:</b> {'Recebido' if qtd_ped > 0 else 'Aguardando...'}<br>
            ▪️ <b>Notas Fiscais:</b> {'Recebido' if qtd_nf > 0 else 'Aguardando...'}<br>
            ▪️ <b>Boletos:</b> {'Recebido' if qtd_bol > 0 else 'Aguardando...'}
        </div>""", unsafe_allow_html=True)

# 6. Lógica do Botão e Processamento
st.markdown("<br>", unsafe_allow_html=True)

# Trava do botão: só desativa se o motorista ou a carga estiverem vazios
botao_desativado = not motorista.strip() or not carga.strip()

if st.button("PROCESSAR E JUNTAR PDFs", use_container_width=True, disabled=botao_desativado):
    if not arq_ped and not arq_nf and not arq_bol:
        st.error("Por favor, anexe pelo menos um arquivo.")
    else:
        with st.spinner("📦 Processando e organizando arquivos... Por favor, aguarde."):
            agrupamentos = {}
            
            def extrair_dados(arquivos, tipo):
                if not arquivos: return
                for arq in arquivos:
                    reader = PdfReader(arq)
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
                                if re.search(r'\b' + re.escape(c) + r'\b', txt): num = c; break
                            if not num:
                                m = re.search(r'Nr\.?\s*do\s*Documento\D*(\d+)', txt, re.IGNORECASE)
                                if m: num = m.group(1)
                        
                        if num: num_ativo = num
                        if num_ativo:
                            if num_ativo not in agrupamentos: agrupamentos[num_ativo] = {'pedido':[], 'nota':[], 'boleto':[]}
                            agrupamentos[num_ativo][tipo].append(page)

            # Executa a extração
            extrair_dados(arq_ped, 'pedido')
            extrair_dados(arq_nf, 'nota')
            extrair_dados(arq_bol, 'boleto')

            output = io.BytesIO()
            final_merger = PdfWriter()

            if agrupamentos:
                # Ordena e junta por chave (Pedido > Nota > Boleto)
                for k in sorted(agrupamentos.keys()):
                    for p in agrupamentos[k]['pedido']: final_merger.add_page(p)
                    for p in agrupamentos[k]['nota']: final_merger.add_page(p)
                    for p in agrupamentos[k]['boleto']: final_merger.add_page(p)
            else:
                # Fallback: Junta tudo na ordem bruta se não achar chaves
                for a in (arq_ped or []): final_merger.append(a)
                for a in (arq_nf or []): final_merger.append(a)
                for a in (arq_bol or []): final_merger.append(a)

            final_merger.write(output)
            final_merger.close()
            output.seek(0)
            
            st.balloons()
            st.success("✅ Arquivos processados com sucesso!")
            
            agora = (datetime.utcnow() - timedelta(hours=3)).strftime("%d-%m-%Y-%Hh%M")
            nome_f = f"{motorista.upper()} ({carga}) - {agora}.pdf"
            
            st.download_button(
                label=f"📥 CLIQUE AQUI PARA BAIXAR: {nome_f}",
                data=output,
                file_name=nome_f,
                mime="application/pdf",
                use_container_width=True
            )

if botao_desativado:
    st.warning("⚠️ Preencha o Motorista e o Nº da Carga para liberar o botão.")
import streamlit as st
import base64

st.set_page_config(page_title="Central de Sistemas - Vale Milk", page_icon="logo.png", layout="wide")

def set_background(image_file):
    try:
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """, unsafe_allow_html=True)
    except:
        pass

set_background("fundo.png")

st.markdown("""
<style>
h1 { color: #ffffff !important; text-align: center; text-shadow: 2px 2px 6px rgba(0,0,0,0.8); }
p  { color: #e2e8f0 !important; text-align: center; text-shadow: 1px 1px 4px rgba(0,0,0,0.8); }

div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: rgba(255, 255, 255, 0.92) !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255,255,255,0.5) !important;
    backdrop-filter: blur(10px);
    padding: 10px 20px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.25) !important;
}
</style>
""", unsafe_allow_html=True)

# Título
st.markdown("<br>", unsafe_allow_html=True)
st.title("Central de Sistemas")
st.markdown("<p style='font-size:16px;'>Acesse todas as aplicações da Vale Milk em um só lugar</p>", unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)

# Cards
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    with st.container(border=True):
        st.markdown("### 📄 Consolidador de Documentos")
        st.markdown("Unifique pedidos, notas fiscais e boletos das cargas de entrega em um único arquivo PDF.")
        st.markdown("<br>", unsafe_allow_html=True)
        st.link_button("Acessar ↗", "https://valemilk-pdf.streamlit.app/app", use_container_width=True)

with col2:
    with st.container(border=True):
        st.markdown("### 🧪 Validador de Pedidos")
        st.markdown("Audite pedidos em PDF cruzando automaticamente com preços e clientes cadastrados no ERP.")
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("🔒 Em breve...", disabled=True, use_container_width=True, key="btn2")

with col3:
    with st.container(border=True):
        st.markdown("### ➕ Em desenvolvimento")
        st.markdown("Novas funcionalidades serão adicionadas em breve para facilitar sua rotina.")
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("🔒 Em breve...", disabled=True, use_container_width=True, key="btn3")
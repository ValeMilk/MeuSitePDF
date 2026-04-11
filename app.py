import streamlit as st
import base64

st.set_page_config(page_title="Central de Sistemas - Vale Milk", page_icon="logo.png", layout="wide")

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
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except:
        pass

set_background("fundo.png")

st.markdown("""
<style>
/* Título */
.titulo-central {
    text-align: center;
    color: #ffffff;
    font-size: 42px;
    font-weight: 900;
    text-shadow: 2px 2px 6px rgba(0,0,0,0.8);
    margin-top: 40px;
    margin-bottom: 5px;
}
.subtitulo-central {
    text-align: center;
    color: #e2e8f0;
    font-size: 16px;
    text-shadow: 1px 1px 4px rgba(0,0,0,0.8);
    margin-bottom: 50px;
}

/* Cards */
.card-container {
    display: flex;
    justify-content: center;
    gap: 30px;
    flex-wrap: wrap;
    padding: 0 40px;
}
.card {
    background-color: rgba(255, 255, 255, 0.92);
    border-radius: 16px;
    padding: 30px;
    width: 320px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.25);
    border: 1px solid rgba(255,255,255,0.5);
    backdrop-filter: blur(10px);
    transition: transform 0.2s;
}
.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.35);
}
.card-icon {
    font-size: 36px;
    margin-bottom: 12px;
}
.card-title {
    font-size: 20px;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 8px;
}
.card-desc {
    font-size: 14px;
    color: #475569;
    line-height: 1.6;
    margin-bottom: 20px;
}
.card-link {
    font-size: 14px;
    font-weight: 700;
    color: #1D4ED8;
    text-decoration: none;
}
.card-link:hover {
    text-decoration: underline;
}
.card-soon {
    font-size: 14px;
    font-weight: 700;
    color: #94A3B8;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='titulo-central'>Central de Sistemas</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo-central'>Acesse todas as aplicações da Vale Milk em um só lugar</div>", unsafe_allow_html=True)

st.markdown("""
<div class='card-container'>

    <div class='card'>
        <div class='card-icon'>📄</div>
        <div class='card-title'>Consolidador de Documentos</div>
        <div class='card-desc'>
            Unifique pedidos, notas fiscais e boletos das cargas de entrega em um único arquivo PDF.
        </div>
        <a class='card-link' href='https://valemilk-pdf.streamlit.app/app' target='_blank'>Acessar ↗</a>
    </div>

    <div class='card'>
        <div class='card-icon'>🧪</div>
        <div class='card-title'>Validador de Pedidos</div>
        <div class='card-desc'>
            Audite pedidos em PDF cruzando automaticamente com preços e clientes cadastrados no ERP.
        </div>
        <span class='card-soon'>🔒 Em breve...</span>
    </div>

</div>
""", unsafe_allow_html=True)
import streamlit as st
from pypdf import PdfWriter
import io

# Configuração da página (Isso muda o ícone da aba lá em cima)
st.set_page_config(
    page_title="Agrupador de PDFs",
    page_icon="logo.png"
)

# Se quiser a logo DENTRO do site também, remova o '#' da linha abaixo:
# st.image("logo.png", width=200)

st.title("Agrupador de PDFs")

uploaded_files = st.file_uploader("Escolha os arquivos PDF", type="pdf", accept_multiple_files=True)

if uploaded_files:
    if st.button("Agrupar PDFs"):
        merger = PdfWriter()
        for pdf in uploaded_files:
            merger.append(pdf)
        
        output = io.BytesIO()
        merger.write(output)
        merger.close()
        output.seek(0)
        
        st.download_button(
            label="Baixar PDF Agrupado",
            data=output,
            file_name="pdf_agrupado.pdf",
            mime="application/pdf"
        )
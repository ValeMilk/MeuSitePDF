import streamlit as st
from pypdf import PdfWriter
import io

# Configuração da página (Ajustado para ser compatível)
st.set_page_config(
    page_title="Agrupador de PDFs",
    page_icon="🥛" # Usei o emoji de leite para garantir que apareça algo da ValeMilk na aba
)

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
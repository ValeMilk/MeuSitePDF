import streamlit as st
from pypdf import PdfWriter
import io

# 1. CONFIGURAÇÃO DA PÁGINA (Isso muda a logo na aba e o nome)
st.set_page_config(
    page_title="Agrupador de PDFs - ValeMilk",
    page_icon="logo.png",  # Substitua pelo nome do seu arquivo de imagem
    layout="centered"
)

# Estilização básica para o título
st.title("📂 Agrupador de PDFs ValeMilk")
st.markdown("Selecione os arquivos abaixo para unir em um único PDF.")

# 2. COMPONENTE DE UPLOAD
uploaded_files = st.file_uploader(
    "Arraste os arquivos aqui", 
    type="pdf", 
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"{len(uploaded_files)} arquivos selecionados.")
    
    # Botão para processar
    if st.button("Gerar PDF Único"):
        merger = PdfWriter()
        
        try:
            for pdf in uploaded_files:
                merger.append(pdf)
            
            # Criar o arquivo final em memória
            output_pdf = io.BytesIO()
            merger.write(output_pdf)
            merger.close()
            output_pdf.seek(0)
            
            st.divider()
            st.balloons()
            
            # 3. BOTÃO DE DOWNLOAD
            st.download_button(
                label="📥 Baixar PDF Agrupado",
                data=output_pdf,
                file_name="PDF_Agrupado_ValeMilk.pdf",
                mime="application/pdf"
            )
            
        except Exception as e:
            st.error(f"Erro ao processar os arquivos: {e}")
else:
    st.info("Aguardando upload de arquivos...")

# Rodapé simples
st.caption("Desenvolvido para uso interno - ValeMilk 2026")
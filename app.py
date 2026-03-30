import streamlit as st
from pypdf import PdfWriter
import io

# 1. Configuração da página (Mantendo a logo que deu certo)
st.set_page_config(
    page_title="Agrupador Inteligente de PDFs",
    page_icon="logo.png",
    layout="wide"  # "wide" permite que as colunas fiquem espalhadas na tela
)

st.title("Agrupador Inteligente de PDFs 📄")
st.write("Envie os arquivos completos. O sistema vai montar o PDF final na ordem: Pedido > Nota Fiscal > Boleto.")

# 2. Criando as 3 colunas exatamente como na imagem
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1. Pedidos")
    file_pedidos = st.file_uploader("Upload Arquivo de Pedidos", type="pdf", key="pedidos")

with col2:
    st.subheader("2. Notas Fiscais")
    file_notas = st.file_uploader("Upload Arquivo de Notas", type="pdf", key="notas")

with col3:
    st.subheader("3. Boletos")
    file_boletos = st.file_uploader("Upload Arquivo de Boletos", type="pdf", key="boletos")

st.divider()

# 3. Lógica para processar e juntar
if st.button("PROCESSAR E JUNTAR PDFs", use_container_width=True):
    # Verifica se pelo menos um arquivo foi enviado
    if file_pedidos or file_notas or file_boletos:
        merger = PdfWriter()
        
        # Adiciona na ordem correta
        if file_pedidos:
            merger.append(file_pedidos)
        if file_notas:
            merger.append(file_notas)
        if file_boletos:
            merger.append(file_boletos)
            
        # Gera o resultado
        output = io.BytesIO()
        merger.write(output)
        merger.close()
        output.seek(0)
        
        st.success("PDFs processados com sucesso!")
        st.download_button(
            label="📥 BAIXAR PDF FINAL",
            data=output,
            file_name="agrupado_valemilk.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.warning("Por favor, selecione ao menos um arquivo para juntar.")
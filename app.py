import streamlit as st
from pypdf import PdfWriter
import io

# 1. Configuração da página e ícone
st.set_page_config(
    page_title="Agrupador Inteligente de PDFs",
    page_icon="logo.png",
    layout="wide"  # Isso permite que as 3 colunas caibam na tela
)

# 2. Título e Descrição
st.title("Agrupador Inteligente de PDFs 📄")
st.write("Envia os arquivos completos. O sistema vai montar o PDF final na ordem: Pedido > Nota Fiscal > Boleto.")

# 3. Layout em 3 Colunas (Exatamente como na foto)
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1. Pedidos")
    file_pedidos = st.file_uploader("Upload Arquivo de Pedidos", type="pdf", key="ped")

with col2:
    st.subheader("2. Notas Fiscais")
    file_notas = st.file_uploader("Upload Arquivo de Notas", type="pdf", key="nf")

with col3:
    st.subheader("3. Boletos")
    file_boletos = st.file_uploader("Upload Arquivo de Boletos", type="pdf", key="bol")

# Espaçamento
st.markdown("<br>", unsafe_allow_html=True)

# 4. Botão de Processar Largo
if st.button("PROCESSAR E JUNTAR PDFs", use_container_width=True):
    if file_pedidos or file_notas or file_boletos:
        merger = PdfWriter()
        
        # Adiciona na ordem da imagem
        if file_pedidos:
            merger.append(file_pedidos)
        if file_notas:
            merger.append(file_notas)
        if file_boletos:
            merger.append(file_boletos)
            
        # Criar o arquivo final
        output = io.BytesIO()
        merger.write(output)
        merger.close()
        output.seek(0)
        
        st.balloons()
        st.success("PDFs agrupados com sucesso!")
        
        # Botão de download também largo
        st.download_button(
            label="BAIXAR PDF FINAL",
            data=output,
            file_name="Agrupado_ValeMilk.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.error("Por favor, faça o upload de pelo menos um arquivo.")
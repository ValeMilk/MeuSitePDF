import streamlit as st
from pypdf import PdfWriter
import io

# 1. Configuração da página (Ícone da aba e Layout Largo)
st.set_page_config(
    page_title="Agrupador Inteligente de PDFs",
    page_icon="logo.png",
    layout="wide"
)

# 2. Título e cabeçalho conforme a imagem
st.title("Agrupador Inteligente de PDFs 📄")
st.write("Envia os arquivos completos. O sistema vai montar o PDF final na ordem: Pedido > Nota Fiscal > Boleto.")

# 3. Layout em 3 Colunas para os Uploads
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1. Pedidos")
    file_pedidos = st.file_uploader("Upload Arquivo de Pedidos", type="pdf", key="u_pedidos")

with col2:
    st.subheader("2. Notas Fiscais")
    file_notas = st.file_uploader("Upload Arquivo de Notas", type="pdf", key="u_notas")

with col3:
    st.subheader("3. Boletos")
    file_boletos = st.file_uploader("Upload Arquivo de Boletos", type="pdf", key="u_boletos")

# Espaçamento visual
st.markdown("<br>", unsafe_allow_html=True)

# 4. Botão de Processar (Ocupando a largura total como na imagem)
if st.button("PROCESSAR E JUNTAR PDFs", use_container_width=True):
    if file_pedidos or file_notas or file_boletos:
        merger = PdfWriter()
        
        # Ordem de junção: Pedido -> Nota -> Boleto
        if file_pedidos:
            merger.append(file_pedidos)
        if file_notas:
            merger.append(file_notas)
        if file_boletos:
            merger.append(file_boletos)
            
        # Gerar o PDF final em memória
        output = io.BytesIO()
        merger.write(output)
        merger.close()
        output.seek(0)
        
        st.balloons()
        st.success("PDFs processados com sucesso!")
        
        # Botão de Download também largo
        st.download_button(
            label="BAIXAR PDF FINAL",
            data=output,
            file_name="Agrupado_ValeMilk.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.error("Por favor, selecione pelo menos um arquivo antes de processar.")

# Rodapé discreto
st.caption("ValeMilk - Sistema Interno")
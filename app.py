import streamlit as st
from pypdf import PdfReader, PdfWriter
import io
import re

# 1. Configuração da página (Deve ser o primeiro comando do Streamlit)
st.set_page_config(layout="wide", page_title="Agrupador de PDFs")

# 2. Injeção de CSS para traduzir os botões do Streamlit para PT-BR
st.markdown("""
    <style>
        /* Esconde o "Drag and drop..." e coloca o texto em PT-BR */
        [data-testid="stFileUploadDropzone"] div div::before {
            content: "Arraste e solte o arquivo aqui";
            display: block;
            margin-bottom: 4px;
        }
        [data-testid="stFileUploadDropzone"] div div span {
            display: none;
        }
        
        /* Esconde o "Limit 200MB..." e coloca o texto em PT-BR */
        [data-testid="stFileUploadDropzone"] div div::after {
            content: "Limite de 200 MB por arquivo • PDF";
            display: block;
            font-size: .8em;
            color: #a3a8b8;
        }
        [data-testid="stFileUploadDropzone"] div div small {
            display: none;
        }
        
        /* Esconde o "Browse files" e coloca "Procurar arquivos" */
        [data-testid="stFileUploadDropzone"] button {
            color: transparent !important;
        }
        [data-testid="stFileUploadDropzone"] button::after {
            content: "Procurar arquivos";
            color: white;
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
        }
    </style>
""", unsafe_allow_html=True)

# 3. Cabeçalho do Site
st.title("Agrupador Inteligente de PDFs 📄")
st.write("Envie os arquivos completos. O sistema vai extrair as páginas (mesmo múltiplas), cruzar os dados de forma inteligente e montar o PDF final na ordem: Pedido > Nota Fiscal > Boleto.")

st.divider()

# 4. Áreas de Upload (Divididas em 3 colunas)
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1. Pedidos")
    arq_pedidos = st.file_uploader("Upload Arquivo de Pedidos", type="pdf", key="pedidos")

with col2:
    st.subheader("2. Notas Fiscais")
    arq_notas = st.file_uploader("Upload Arquivo de Notas", type="pdf", key="notas")

with col3:
    st.subheader("3. Boletos")
    arq_boletos = st.file_uploader("Upload Arquivo de Boletos", type="pdf", key="boletos")

st.divider()

# 5. Lógica Principal de Processamento
if st.button("PROCESSAR E JUNTAR PDFs", use_container_width=True):
    if not arq_pedidos and not arq_notas and not arq_boletos:
        st.warning("Por favor, envie pelo menos um arquivo para processar.")
    else:
        # Dicionário mestre que guarda as páginas separadas pelo número de ligação
        agrupamentos = {}
        
        def processar_arquivo(arquivo, tipo_doc):
            if arquivo:
                leitor = PdfReader(arquivo)
                numero_ativo = None 
                
                for pagina in leitor.pages:
                    texto = pagina.extract_text()
                    numero_encontrado = None
                    
                    if texto:
                        # --- REGRA DO PEDIDO ---
                        if tipo_doc == 'pedido':
                            match = re.search(r'(\d+)\s*\d*Doc\.:', texto, re.IGNORECASE)
                            if not match:
                                match = re.search(r'Doc\.?:\s*(\d+)', texto, re.IGNORECASE)
                            if match:
                                numero_encontrado = match.group(1)
                                
                        # --- REGRA DA NOTA FISCAL ---
                        elif tipo_doc == 'nota':
                            match = re.search(r'(\d+)\s*S[ÉE]RIE', texto, re.IGNORECASE)
                            if not match:
                                match = re.search(r'NF-e\s*(\d+)', texto, re.IGNORECASE)
                            if match:
                                numero_encontrado = match.group(1)
                                
                        # --- REGRA DO BOLETO (Blindada contra datas) ---
                        elif tipo_doc == 'boleto':
                            # Procura primeiramente pelos números que já achamos nos pedidos
                            chaves_conhecidas = list(agrupamentos.keys())
                            for chave in chaves_conhecidas:
                                if re.search(r'\b' + re.escape(chave) + r'\b', texto):
                                    numero_encontrado = chave
                                    break
                            
                            # Fallback caso a pessoa mande só o boleto
                            if not numero_encontrado:
                                match = re.search(r'Nr\.?\s*do\s*Documento\D*(\d+)', texto, re.IGNORECASE)
                                if match:
                                    numero_encontrado = match.group(1)
                    
                    # Atualiza a "memória" se achou um número novo na página
                    if numero_encontrado:
                        numero_ativo = numero_encontrado
                        
                    # Guarda a página na gaveta correta
                    if numero_ativo:
                        if numero_ativo not in agrupamentos:
                            agrupamentos[numero_ativo] = {'pedido': [], 'nota': [], 'boleto': []}
                        
                        agrupamentos[numero_ativo][tipo_doc].append(pagina)

        with st.spinner("Lendo e cruzando as páginas de todos os arquivos... Isso pode levar alguns segundos."):
            # A ordem de execução garante que o Pedido dite os números corretos primeiro
            processar_arquivo(arq_pedidos, 'pedido')
            processar_arquivo(arq_notas, 'nota')
            processar_arquivo(arq_boletos, 'boleto')
            
            if not agrupamentos:
                st.error("Não foi possível encontrar nenhum número de ligação válido nos PDFs enviados. Verifique os arquivos.")
            else:
                merger = PdfWriter()
                
                # Junta tudo respeitando a hierarquia: Pedido > Nota > Boleto
                for numero, docs in agrupamentos.items():
                    for pagina_pedido in docs['pedido']:
                        merger.add_page(pagina_pedido)
                        
                    for pagina_nota in docs['nota']:
                        merger.add_page(pagina_nota)
                        
                    for pagina_boleto in docs['boleto']:
                        merger.add_page(pagina_boleto)
                        
                # Prepara o arquivo final na memória para o usuário baixar
                pdf_final = io.BytesIO()
                merger.write(pdf_final)
                merger.close()
                pdf_final.seek(0)
                
                st.success(f"Sucesso! {len(agrupamentos)} operações foram encontradas e ordenadas perfeitamente.")
                
                # Botão final de download
                st.download_button(
                    label="📥 BAIXAR PDF FINAL AGRUPADO",
                    data=pdf_final,
                    file_name="Arquivos_Agrupados_Final.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
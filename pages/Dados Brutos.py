import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(layout = 'wide')                                                                # para alterar o formato da tela

@st.cache_data                                                                                     # mantem o ultimo arquivo armazenado em cache
def conversor_DF_CSV(df):
    return df.to_csv(index = False).encode('utf-8')                                                # transforma em csv | codifica os dados em 'utf-8'

def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!',                                           # retorna uma mensagem de sucesso pra o usuario
                         icon = "✅")    
    time.sleep(5)                                                                                  # tempo para a mensagem desaparecer   
    sucesso.empty()                                                                                # apaga a mensagem                                            


st.title('Dados Brutos')                                                                           # adiciona um titulo

url = 'https://labdados.com/produtos'                                                              # site para pegar os dados / endereço da api
response = requests.get(url)                                                                       # acesso aos dados da api
dados = pd.DataFrame.from_dict(response.json())                                                    # transorma a requisição em Json para que ela possa ser transformada em DataFrame
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], 
                                         format = '%d/%m/%Y')

with st.expander('Colunas'):                                                                       # seção compacta-expandivel
    colunas = st.multiselect('Selecione as Colunas',                                               # caixa de seleção multipla
                             list(dados.columns),                                                  # lista total de campos 
                             list(dados.columns),                                                  # lista de campos padrões
                             placeholder = 'Selecione as Colunas')          

st.sidebar.title('Filtros')                                                                        # barra lateral | titulo da barra                                                                   

with st.sidebar.expander('Nome do Produto'): 
    produtos = st.multiselect('Selecione os Produtos', 
                              dados['Produto'].unique(), 
                              dados['Produto'].unique(), 
                              placeholder = 'Selecione os Produtos')

with st.sidebar.expander('Categoria do Produto'):
    categoria = st.multiselect('Selecione a Categoria do Produto', 
                               dados['Categoria do Produto'].unique(), 
                               dados['Categoria do Produto'].unique(), 
                               placeholder = 'Selecione a Categoria do Produto')

with st.sidebar.expander('Preço do Produto'):
    preco = st.slider('Selecione o Preço', 0, 5000, (0, 5000))                                     #  barra de seleção '(0,5000)' transforma o intervalo em continuo

with st.sidebar.expander('Frete do Compra'):
    frete = st.slider('Selecione o Valor do Frete', 
                      dados['Frete'].min(), 
                      dados['Frete'].max(), 
                      (dados['Frete'].min(), 
                       dados['Frete'].max()))

with st.sidebar.expander('Data da Compra'):
    data_compra = st.date_input('Selecione a Data',                                                # input de data na forma de calendario
                                (dados['Data da Compra'].min(), 
                                 dados['Data da Compra'].max()))     
    
with st.sidebar.expander('Vendedor'):
    vendedor = st.multiselect('Selecione o Vendedor', 
                              dados['Vendedor'].unique(), 
                              dados['Vendedor'].unique(), 
                              placeholder = 'Selecione o Vendedor')

with st.sidebar.expander('Local da Compra'):
    local = st.multiselect('Selecione o Local da Compra', 
                           dados['Local da compra'].unique(), 
                           dados['Local da compra'].unique(), 
                           placeholder = 'Selecione o Local da Compra')

with st.sidebar.expander('Avaliação :star:'):
    avaliacao = st.slider('Selecione a Quantidade de Estrelas', 
                          dados['Avaliação da compra'].min(), 
                          dados['Avaliação da compra'].max(), 
                          (dados['Avaliação da compra'].min(), 
                           dados['Avaliação da compra'].max()))

with st.sidebar.expander('Forma de Pagamento'):
    pagamento = st.multiselect('Selecione a Forma de Pagamento', 
                               dados['Tipo de pagamento'].unique(), 
                               dados['Tipo de pagamento'].unique(), 
                               placeholder = 'Selecione a Forma de Pagamento')

with st.sidebar.expander('Nº de Parcelas'):
    parcelas = st.slider('Selecione a Quantidade de Parcelas', 
                         dados['Quantidade de parcelas'].min(), 
                         dados['Quantidade de parcelas'].max(), 
                         (dados['Quantidade de parcelas'].min(), 
                          dados['Quantidade de parcelas'].max()))

with st.sidebar.expander('Latitude'):
    latitude = st.slider('Selecione a Latitude', 
                         dados['lat'].min(), 
                         dados['lat'].max(), 
                         (dados['lat'].min(), 
                          dados['lat'].max()))

with st.sidebar.expander('Longitude'):
    longitude = st.slider('Selecione a Longitude', 
                          dados['lon'].min(), 
                          dados['lon'].max(), 
                          (dados['lon'].min(), 
                           dados['lon'].max()))
    
query = '''
Produto in @produtos and \
`Categoria do Produto` in @categoria and \
@preco[0] <= Preço <= @preco[1] and \
@frete[0] <= Frete <= @frete[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
Vendedor in @vendedor and \
`Local da compra` in @local and \
@avaliacao[0] <= `Avaliação da compra` <= @avaliacao[1] and \
`Tipo de pagamento` in @pagamento and \
@parcelas[0] <= `Quantidade de parcelas` <= @parcelas[1] and \
@latitude[0] <= lat <= @latitude[1] and \
@longitude[0] <= lon <= @longitude[1]
'''

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

st.dataframe(dados_filtrados)                                                                      # adiciona o dataframe ao dashboard

st.markdown(f'''A tabela possui :blue[{dados_filtrados.shape[0]}] linhas 
            e :blue[{dados_filtrados.shape[1]}] colunas''')                                        # exibe o texto em markdown

st.markdown('Escreva um nome para o arquivo')

col1, col2 = st.columns(2)

with col1:
    nome_arquivo = st.text_input('', label_visibility = 'collapsed', value = 'dados')              # recebe uma string do usuario | label_visibility remove o espaço da visualização
    nome_arquivo += '.csv'
with col2:
    st.download_button('Fazer o download da tabela em csv',                                        # botão de download para os dados
                       data = conversor_DF_CSV(dados_filtrados),                                   # dados a serem baixados
                       file_name = nome_arquivo,                                                   # nome do arquivo
                       mime = 'text/csv',                                                          # formato do arquivo
                       on_click = mensagem_sucesso)                                                # ação ao clicar                                                                               


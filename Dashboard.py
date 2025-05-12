import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(layout = 'wide')                                                                # para alterar o formato da tela

def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} Milhões'

st.title('DASHBOARD DE VENDAS :shopping_trolley:')                                                 # adiciona um titulo

url = 'https://labdados.com/produtos'                                                              # site para pegar os dados / endereço da api

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
## FILTROS SIDEBAR ##
regioes = ['Brasil', 'Norte', 'Nordeste', 
           'Centro-Oeste', 'Suldeste', 'Sul']

st.sidebar.title('Filtros')                                                                        # barra lateral | titulo da barra

regiao = st.sidebar.selectbox('Região', regioes)                                                   # barra lateral | caixa de seleção 

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o periodo', 
                                 value = True)                                                     # barra lateral | checkbox

if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)                                                     # barra lateral | barra de seleção

# vai substituir parte da url pela entrada do usuario (como se eu filtrase uma pagina web)
query_string = {'regiao' : regiao.lower(), 'ano' : ano}

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

response = requests.get(url,
                        params = query_string)                                                     # acesso aos dados da api
dados = pd.DataFrame.from_dict(response.json())                                                    # transorma a requisição em Json para que ela possa ser transformada em DataFrame
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], 
                                         format = '%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores',                                           # barra lateral | caixa de seleção multipla
                                           dados['Vendedor'].unique(),
                                           placeholder = 'Selecione o(s) Vendedor(es)')      

if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]       

##############################################################################################################################################################################
## TABELAS ##
dados_estados = dados.groupby(['Local da compra'])[['Preço']].sum()

# drop_duplicates : exclui linhas duplicadas a partir de um conjunto de campos escolhidos
# merge : uni ambos os dataframes escolhendo as chaves da esquerda e direita em cada tabela

dados_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(dados_estados, left_on = 'Local da compra', right_index = True)
dados_estados = dados_estados.sort_values('Preço', ascending = False)

# define o indice e agrupa pela frequencia dos meses
dados_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))[['Preço']].sum()
dados_mensal = dados_mensal.reset_index()
dados_mensal['Ano'] = dados_mensal['Data da Compra'].dt.year
dados_mensal['Mes'] = dados_mensal['Data da Compra'].dt.month_name()

dados_categorias = dados.groupby(['Categoria do Produto'])[['Preço']].sum().sort_values('Preço', ascending = True)

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
## aba 2 ##

dados_vendas = dados.copy()
dados_vendas['Vendas'] = 1

dados_estados_vendas = dados_vendas.groupby(['Local da compra'])[['Vendas']].sum()
dados_estados_vendas = dados_vendas.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(dados_estados_vendas, left_on = 'Local da compra', right_index = True)
dados_estados_vendas = dados_estados_vendas.sort_values('Vendas', ascending = False)

dados_mensal_vendas = dados_vendas.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))[['Vendas']].sum()
dados_mensal_vendas = dados_mensal_vendas.reset_index()
dados_mensal_vendas['Ano'] = dados_mensal_vendas['Data da Compra'].dt.year
dados_mensal_vendas['Mes'] = dados_mensal_vendas['Data da Compra'].dt.month_name()

dados_categorias_vendas = dados_vendas.groupby(['Categoria do Produto'])[['Vendas']].sum().sort_values('Vendas', ascending = True)

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
## aba 3 ##

# para fazer agregação de soma e contagem ao mesmo tempo
# cria um dataframe upando os dados de vendas dos vendedores e a quantidade da receita obtida 
dados_vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))
dados_vendedores.columns = ('Receita Obtida', 'Vendas Realizadas')

##############################################################################################################################################################################
## GRAFICOS ##

# Grafico de Mapa
# st.map()                                                                                         # adiciona pontos a um mapa (visualização mais simples)
# st.pyplot()                                                                                      # para plotar um grafico em matplotlib

# scatter_geo : grafico de dispersão em cima de um mapa
fig_mapa_estados = px.scatter_geo(dados_estados, 
                                  lat = 'lat', 
                                  lon = 'lon',
                                  scope = 'south america',                                         # filtra a região de exibição do mapa
                                  size = 'Preço',                                                  # tamanho da bolha
                                  template = 'seaborn',                                            # estilo da imagem
                                  hover_name = 'Local da compra',                                  # nomeia o hover
                                  hover_data = {'lat' : False, 'lon' : False},                     # remove informações do hover
                                  title = 'Receita por Estado')

fig_receita_mensal = px.line(dados_mensal, 
                             x = 'Mes',
                             y = 'Preço',
                             markers = True,
                             range_y = (0, dados_mensal.max()),                                    # limites do eixo y
                             color = 'Ano',                                                        # cor da linha pela variavel ano
                             line_dash = 'Ano',                                                    # formato da linha pela variavel ano
                             title = 'Receita Mensal')

fig_receita_mensal.update_layout(yaxis_title = 'Receita')
fig_receita_mensal.update_xaxes(tickangle=315)

fig_receita_estados = px.bar(dados_estados[:5],
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto = True,                                                     # coloca o valor correspondente em cima de cada coluna
                             title = 'Top 5 Estados (Receita)')

fig_receita_estados.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(dados_categorias,
                                x = 'Preço',
                                y = dados_categorias.index,
                                text_auto = True,
                                title = 'Receita por Categoria')

fig_receita_categorias.update_layout(xaxis_title = 'Receita')

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
## aba 2 ##

fig_mapa_estados_vendas = px.scatter_geo(dados_estados_vendas, 
                                  lat = 'lat', 
                                  lon = 'lon',
                                  scope = 'south america',                      
                                  size = 'Vendas',                               
                                  template = 'seaborn',                         
                                  hover_name = 'Local da compra',               
                                  hover_data = {'lat' : False, 'lon' : False},  
                                  title = 'Vendas por Estado')

fig_vendas_estados = px.bar(dados_estados_vendas[:5],
                             x = 'Local da compra',
                             y = 'Vendas',
                             text_auto = True,                                  
                             title = 'Top 5 Estados (Vendas)')

fig_vendas_estados.update_layout(yaxis_title = 'Quantidade de Vendas')

fig_vendas_mensal = px.line(dados_mensal_vendas, 
                             x = 'Mes',
                             y = 'Vendas',
                             markers = True,
                             range_y = (0, dados_mensal_vendas.max()),                 
                             color = 'Ano',                                     
                             line_dash = 'Ano',                                 
                             title = 'Vendas por Mês')

fig_vendas_mensal.update_layout(yaxis_title = 'Quantidade de Vendas')
fig_vendas_mensal.update_xaxes(tickangle=315)

fig_vendas_categorias = px.bar(dados_categorias_vendas,
                                x = 'Vendas',
                                y = dados_categorias_vendas.index,
                                text_auto = True,
                                title = 'Vendas por Categoria')

fig_vendas_categorias.update_layout(xaxis_title = 'Quantidade de Vendas')

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
## aba 3 ##

def graf1(qtd):
    selecao = dados_vendedores[['Receita Obtida']].sort_values('Receita Obtida', ascending = True).head(qtd)
    fig_receita_vendedores = px.bar(selecao,
                                    x = 'Receita Obtida',
                                    y = selecao.index,
                                    text_auto = True,
                                    title = f'Top {qtd} Vendedores (Receita)')
    return fig_receita_vendedores

def graf2(qtd):
    selecao = dados_vendedores[['Vendas Realizadas']].sort_values('Vendas Realizadas', ascending = True).head(qtd)
    fig_vendas_vendedores = px.bar(selecao,
                                    x = 'Vendas Realizadas',
                                    y = selecao.index,
                                    text_auto = True,
                                    title = f'Top {qtd} Vendedores (Quantidade de Vendas)')
    return fig_vendas_vendedores
    
##############################################################################################################################################################################
## VISUALIZAÇÃO no Streamlit ##

aba1, aba2, aba3 = st.tabs(['Receita Total', 
                           'Quantidade de Vendas',
                           'Vendedores'])                                                          # acrescenta multiplas telas ao dashboard

with aba1:
    col1, col2 = st.columns(2)                                                                     # divide o dashboar em multiplas colunas

    # rt = ('R$ {:,.2f}').format(dados['Preço'].sum())
    # qv = ('{:,.0f}').format(dados.shape[0])
    rt = formata_numero(dados['Preço'].sum(), 'R$')
    qv = formata_numero(dados.shape[0])

    with col1:                                                                                     # acessa o espaço da coluna 1 e atribui objetos a ele
        st.metric('Receita Total', rt)                                                             # adiciona uma metrica (kpi) ao dashboard
        st.plotly_chart(fig_mapa_estados,                                                          # para plotar um grafico em plotly
                        use_container_width = True)                                                # limita a largura do grafico pelo tamanho da coluna
        st.plotly_chart(fig_receita_estados, 
                        use_container_width = True)
    with col2:
        st.metric('Quantidade de Vendas', qv)
        st.plotly_chart(fig_receita_mensal, 
                        use_container_width = True)
        st.plotly_chart(fig_receita_categorias, 
                        use_container_width = True)

    # st.dataframe(dados)                                                                          # adiciona o dataframe ao dashboard

with aba2:
    col1, col2 = st.columns(2)                               

    # rt = ('R$ {:,.2f}').format(dados['Preço'].sum())
    # qv = ('{:,.0f}').format(dados.shape[0])
    rt = formata_numero(dados['Preço'].sum(), 'R$')
    qv = formata_numero(dados.shape[0])

    with col1:                                               
        st.metric('Receita Total', rt)   
        st.plotly_chart(fig_mapa_estados_vendas, 
                        use_container_width = True)
        st.plotly_chart(fig_vendas_estados, 
                        use_container_width = True)                    
       
    with col2:
        st.metric('Quantidade de Vendas', qv)  
        st.plotly_chart(fig_vendas_mensal, 
                        use_container_width = True)
        st.plotly_chart(fig_vendas_categorias, 
                        use_container_width = True)                                  

with aba3:

    qtd_vendedores = st.number_input('Quantidade de Vendedores',  2, 10, 5)                        # recebe um numero do usuario(elemento interativo) [min, max, padrão]  
                  
    col1, col2 = st.columns(2)                               

    # rt = ('R$ {:,.2f}').format(dados['Preço'].sum())
    # qv = ('{:,.0f}').format(dados.shape[0])
    rt = formata_numero(dados['Preço'].sum(), 'R$')
    qv = formata_numero(dados.shape[0])

    with col1:                                               
        st.metric('Receita Total', rt)                       
        st.plotly_chart(graf1(qtd_vendedores), 
                        use_container_width = True) 
    with col2:
        st.metric('Quantidade de Vendas', qv)
        st.plotly_chart(graf2(qtd_vendedores), 
                        use_container_width = True) 
                             
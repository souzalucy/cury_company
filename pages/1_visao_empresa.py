# Import libraries
import pandas as pd
import plotly.express as px
from haversine import haversine
import streamlit as st
import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Empresa', layout='wide')

#-----------------------
# Funções
#-----------------------
def clean_code(df1):
    '''Esta função tem a responsabilidade de limpar o data frame
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica)

        Input: Dataframe
        Output: Dataframe
    '''
    # 1. convertendo a coluna Age de texto para número
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    # 2 convertendo a coluna Ratings de texto para numero decimal (float)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    # 3 convertendo a coluna order_date de texto para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # 4 convertendo multiple_deliveries de texto para numero inteiro (int)
    linhas_selecionadas2 = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas2, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # 5Removendo os espaços dentro de strings/texto/object
    df1.loc[:, "ID"] = df1.loc[:, "ID"].str.strip()
    df1.loc[:, "Road_traffic_density"] = df1.loc[:, "Road_traffic_density"].str.strip()
    df1.loc[:, "Type_of_order"] = df1.loc[:, "Type_of_order"].str.strip()
    df1.loc[:, "Type_of_vehicle"] = df1.loc[:, "Type_of_vehicle"].str.strip()
    df1.loc[:, "City"] = df1.loc[:, "City"].str.strip()
    df1.loc[:, "Festival"] = df1.loc[:, "Festival"].str.strip()

    # 6 Removendo os NaN
    df1 = df1.loc[df1['Road_traffic_density'] != 'NaN', :]
    df1 = df1.loc[df1['City'] != 'NaN', :]
    df1 = df1.loc[df1['Time_taken(min)'] != 'NaN', :]
    df1 = df1.loc[df1['Festival'] != 'NaN ', :]

    # 7 Removendo o (min) do Time_Taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split( '(min)')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1


def order_metric(df1):
    '''
    Função para contagem da coluna "Order_Date" e plotagem em gráfico de barras
    Input: Dataframe
    Output: Fig
    '''
    cols = ['ID', 'Order_Date']
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
    fig = px.bar(df_aux, x='Order_Date', y='ID')
    return fig 

def Traffic_Order_Share(df1):
    '''
    Função calcula a porcentagem de pedidos por densidade de tráfego e retorna um gráfico de pizza representando essa distribuição.
    Input: Dataframe
    Output: Fig
    '''
    df_aux3 = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df_aux3['entrega_perc'] = df_aux3['ID'] / df_aux3['ID'].sum()
    fig = px.pie(df_aux3, values='entrega_perc', names='Road_traffic_density')
    return fig

def Traffic_Order_City(df1):
    '''
    A função cria um gráfico de dispersão que mostra a quantidade de pedidos por cidade e densidade de tráfego, representando o volume de pedidos pelo tamanho dos pontos.
    Input: Dataframe
    Output: Fig
    '''
    df_aux4 = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    fig = px.scatter(df_aux4, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig

def Order_by_Week(df1):
    '''
    A fução cria um gráfico de linha que mostra a quantidade de pedidos por semana ao longo do ano.
    Input: Dataframe
    Output: Fig
    '''
    #criar a coluna de semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux2 = df1.loc[:, ["ID", 'week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux2, x='week_of_year', y='ID')
    return fig

def Order_Share_by_Week(df1):
    '''
    A função cria um gráfico de linha que mostra a média semanal de pedidos por entregador ao longo do ano.
    Input: Dataframe
    Output: Fig
    '''
    df_aux5 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux6 = df1.loc[:,['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
    df_aux_u = pd.merge(df_aux5, df_aux6, how='inner')
    df_aux_u['order_by_deliver'] = df_aux_u['ID'] / df_aux_u['Delivery_person_ID']
    fig = px.line(df_aux_u, x='week_of_year', y='order_by_deliver')
    return fig

def Country_Maps(df1):
    '''
    A função cria um mapa interativo com marcadores representando a mediana das localizações de entrega por cidade e densidade de tráfego.
    Input: Dataframe
    Output: Map
    '''
    # Calculando a mediana dos pontos geográficos por cidade e densidade de tráfego
    df_aux7 = df1.loc[:, ["City", 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()

    # Criando o mapa
    map = folium.Map()

    # Adicionando marcadores ao mapa
    for _, location_info in df_aux7.iterrows():
        folium.Marker(
            [location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']],
            popup=f"City: {location_info['City']}, Traffic: {location_info['Road_traffic_density']}"
        ).add_to(map)

    # Renderizando o mapa
    folium_static(map, width=1024, height=600)


#--------------------- Inicio da Estrutura Lógica do Código-----------------------------

# Import datasets
df1 = pd.read_csv("train.csv")

#limpando dados
df1 = clean_code(df1)

# backup
df2 = df1.copy()



# =========================================
# Barra Lateral
# =========================================
st.header("Marketplace - Visão Cliente")

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''---''')

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime.datetime( 2022, 4, 13),
    min_value=datetime.datetime(2022, 2, 11),
    max_value=datetime.datetime(2022, 4, 6),
    format='DD-MM-YYYY'
)

st.sidebar.markdown('''---''')

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown('''---''')
st.sidebar.markdown( '### Powered by Lucy Souza')

# filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas,:]

# filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]

# =========================================
# Layout no Stremlite
# =========================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        # Order Metric
        fig = order_metric(df1)
        st.markdown('# Orders by Day')
        st.plotly_chart( fig, use_container_width=True)

        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                fig = Traffic_Order_Share(df1)
                st.header('Traffic Order Share')
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig = Traffic_Order_City(df1)
                st.header('Traffic Order City')
                st.plotly_chart(fig, use_container_width=True)


with tab2:
    with st.container():
        fig = Order_by_Week(df1)
        st.markdown("# Order by Week")
        st.plotly_chart(fig, use_container_width=True)
                
        with st.container():
            fig = Order_Share_by_Week(df1)
            st.markdown("# Order Share by Week")
            st.plotly_chart(fig, use_container_width=True)


with tab3:
    st.markdown("# Country Maps")
    Country_Maps(df1)

   
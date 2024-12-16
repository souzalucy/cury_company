# Import libraries
import pandas as pd
import plotly.express as px
from haversine import haversine
import streamlit as st
import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title='Visão Restaurante', layout='wide')

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

def distance(df1, fig):
    if fig == False:
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
        df1['distance'] = df1.loc[:, cols].apply(
                lambda x: haversine(
                (x['Delivery_location_latitude'], x['Delivery_location_longitude']),
                (x['Restaurant_latitude'], x['Restaurant_longitude'])
                ),
                axis=1
                )
        avg_distance = np.round(df1['distance'].mean(), 2)
        return avg_distance
    
    else:
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
        df1['distance'] = df1.loc[:, cols].apply(
            lambda x: haversine(
                (x['Delivery_location_latitude'], x['Delivery_location_longitude']),
                (x['Restaurant_latitude'], x['Restaurant_longitude'])
                ),
                axis=1
                )
        avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
        return fig
    
def avg_std_time_delivery(df1, festival, op):

    """
    Esta função calcula o tempo médio e desvio padrão de tempo de entrega.
    Input:
        - df: Dataframe com os dados necessários para o cálculo
        - op: Tipo de operação que precisa ser calculado
            'avg_time': calcula o tempo médio
            'std_time': calcula o desvio padrão do tempo
    Output:
        - df: Dataframe com 2 colunas e 1 linha
    """
    cols = ['Time_taken(min)', 'Festival']
    df_aux10 = df1.loc[:, cols].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
    df_aux10.columns = [ 'avg_time', 'std_time']
    df_aux10 = df_aux10.reset_index() 
    df_aux10 = np.round(df_aux10.loc[df_aux10['Festival'] == festival, op], 2)
    return df_aux10    

def avg_std_time_graph(df1):       
    cols = ['City', 'Time_taken(min)']
    df_aux7 = df1.loc[:,cols].groupby('City').agg({'Time_taken(min)':['mean', 'std']})
    df_aux7.columns = ['avg_time', 'std_time']
    df_aux7 = df_aux7.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',
                        x=df_aux7['City'],
                        y=df_aux7['avg_time'],
                        error_y=dict(type='data', array=df_aux7['std_time'])))
    fig.update_layout(barmode='group')
    return fig

def avg_std_time_on_traffic(df1):
    cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
    df_aux9 = df1.loc[:,cols].groupby(['City', 'Road_traffic_density']).agg({"Time_taken(min)": ['mean', 'std']})
    df_aux9.columns = ['avg_time', 'std_time']
    df_aux9 = df_aux9.reset_index()
    fig = px.sunburst(df_aux9, path=['City', 'Road_traffic_density'], values='avg_time',
                  color='std_time', color_continuous_scale='RdBu',
                  color_continuous_midpoint=np.average(df_aux9['std_time']))
    return fig 
#--------------------- Inicio da Estrutura Lógica do Código-----------------------------
# Import datasets
df1 = pd.read_csv("train.csv")

# limpeza
df1 = clean_code(df1)

# backup
df1 = df1.copy()

# =========================================
# Barra Lateral
# =========================================
st.header("Marketplace - Visão Restaurantes")

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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overal Metrics')

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            delivery_unique = df1.loc[:, 'Delivery_person_ID'].nunique()
            col1.metric('Entregadores', delivery_unique)

        with col2:
            avg_distance = distance(df1, fig=False)
            col2.metric('A distância média', avg_distance)

        with col3:
            df_aux10 = avg_std_time_delivery(df1, 'Yes', 'avg_time')
            col3.metric('Tempo médio', df_aux10)

        with col4:
            df_aux10 = avg_std_time_delivery(df1, 'Yes', 'std_time')
            col4.metric('STD entrega', df_aux10)

        with col5:
            df_aux10 = avg_std_time_delivery(df1, 'No', 'avg_time')
            col5.metric('Tempo médio', df_aux10)

        with col6:
            df_aux10 = avg_std_time_delivery(df1, 'No', 'std_time')
            col6.metric('STD entrega', df_aux10)

    with st.container():
        st.markdown('''---''')
        col1, col2 = st.columns(2)

        with col1:
            st.title('Tempo Médio de entrega por cidade')
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.title('Distribuição da Distancia')
            cols = ['City', "Time_taken(min)", 'Type_of_order']
            df_aux8 = df1.loc[:,cols].groupby(['City', 'Type_of_order']).agg({"Time_taken(min)": ['mean', 'std']})
            df_aux8.columns = ['avg_time', 'std_time']
            df_aux8 = df_aux8.reset_index()
            st.dataframe(df_aux8, use_container_width=True)
        
    with st.container():
        st.markdown('''---''')
        st.title('Distribuição do tempo')

        col1, col2 = st.columns(2)
        with col1:
            fig = distance(df1, fig=True)
            st.plotly_chart(fig, use_container_width=True)


        with col2:
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig, use_container_width=True)


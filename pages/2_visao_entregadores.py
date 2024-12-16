# Import libraries
import pandas as pd
import plotly.express as px
from haversine import haversine
import streamlit as st
import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregadores', layout='wide')

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

def top_delivers(df1, top_asc):
     #USANDO A MÉDIA
    df2 = df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City','Delivery_person_ID']).mean().sort_values(['City', 'Time_taken(min)'], ascending=top_asc).reset_index()

    df_b01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_b02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_b03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df_todos2 = pd.concat([df_b01, df_b02, df_b03])
    return df_todos2
#--------------------- Inicio da Estrutura Lógica do Código-----------------------------
# Import datasets
df = pd.read_csv("train.csv")

# backup
df1 = df.copy()

df1 = clean_code(df1)

# =========================================
# Barra Lateral
# =========================================
st.header("Marketplace - Visão Entregadores")

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
    default='Low'
)

clima = st.sidebar.multiselect(
    'Quais as condições do clima?',
    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'],
    default='conditions Cloudy'
)

st.sidebar.markdown('''---''')
st.sidebar.markdown( '### Powered by Lucy Souza')

# filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas,:]

# filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]

# filtro de clima
linhas_selecionadas = df1['Weatherconditions'].isin(clima)
df1 = df1.loc[linhas_selecionadas,:]

# =========================================
# Layout no Stremlite
# =========================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title("Overall Metrics")
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            max_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('A maior idade é de ', max_idade)

        with col2:
            min_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('A menor idade é de ', min_idade)

        with col3:
            melhor = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('A melhor condição ', melhor)
            
        with col4:
            pior = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('A melhor condição ', pior)

    with st.container():
        st.markdown("""---""")
        st.title("Avaliações")
       
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação média por entregador')
            media = df1.loc[:, ["Delivery_person_ID", "Delivery_person_Ratings"]].groupby("Delivery_person_ID").mean().reset_index()
            st.dataframe(media)

        with col2:
            st.markdown('##### Avaliação média por trânsito')
            media_e_desvio_trafego = df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby('Road_traffic_density').agg(['mean', 'std']).reset_index()
            media_e_desvio_trafego.columns = ['Traffic', 'Delivery_mean', 'Delivery_std']
            st.dataframe(media_e_desvio_trafego)

            st.markdown('##### Avaliação média por clima')
            media_e_desvio_clima = df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions').agg(['mean', 'std']).reset_index()
            media_e_desvio_clima.columns = ['Weatherconditions', 'Delivery_mean', 'Delivery_std']
            st.dataframe(media_e_desvio_clima)

    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de entrega')
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Top entregadores mais rápidos')
            #USANDO A MÉDIA
            df_todos2 = top_delivers(df1, top_asc=True)
            st.dataframe(df_todos2)

        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df_todos2 = top_delivers(df1, top_asc=False)
            st.dataframe(df_todos2)
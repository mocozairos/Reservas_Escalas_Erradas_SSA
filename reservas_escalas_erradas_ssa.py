import streamlit as st
import mysql.connector
import decimal
import pandas as pd
from datetime import datetime, date

def gerar_df_phoenix(vw_name, base_luck):
    
    data_hoje = datetime.now()

    data_hoje_str = data_hoje.strftime("%Y-%m-%d")

    # Parametros de Login AWS
    config = {
    'user': 'user_automation_jpa',
    'password': 'luck_jpa_2024',
    'host': 'comeia.cixat7j68g0n.us-east-1.rds.amazonaws.com',
    'database': base_luck
    }
    # Conexão as Views
    conexao = mysql.connector.connect(**config)
    cursor = conexao.cursor()

    request_name = f'SELECT * FROM {vw_name} WHERE {vw_name}.`Data Execucao`>={data_hoje_str}'

    # Script MySql para requests
    cursor.execute(
        request_name
    )
    # Coloca o request em uma variavel
    resultado = cursor.fetchall()
    # Busca apenas o cabecalhos do Banco
    cabecalho = [desc[0] for desc in cursor.description]

    # Fecha a conexão
    cursor.close()
    conexao.close()

    # Coloca em um dataframe e muda o tipo de decimal para float
    df = pd.DataFrame(resultado, columns=cabecalho)
    df = df.applymap(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)
    return df

def plotar_tabela(df_filtrado):

    df_ref = df_filtrado

    df_ref = df_ref.sort_values(by='Data Execucao', ascending=False)
        
    df_ref['Data da Escala'] = pd.to_datetime(df_ref['Data da Escala']).dt.strftime("%d/%m/%Y")

    df_ref['Data Execucao'] = pd.to_datetime(df_ref['Data Execucao']).dt.strftime("%d/%m/%Y")

    st.dataframe(df_ref[lista_colunas_df], hide_index=True, use_container_width=True)

hoje = date.today()

base_luck = 'test_phoenix_salvador'

lista_colunas_df = ['Data Execucao', 'Data da Escala', 'Escala', 'Reserva', 'Veiculo', 'Motorista', 'Guia', 'Servico']

st.set_page_config(layout='wide')

st.title('Reservas em Escalas Erradas - Salvador')

st.divider()

if not 'df_escalas' in st.session_state:

    st.session_state.df_escalas = gerar_df_phoenix('vw_payment_guide', base_luck)

    st.session_state.df_escalas = st.session_state.df_escalas[~pd.isna(st.session_state.df_escalas['Escala'])].reset_index(drop=True)

    st.session_state.df_escalas = st.session_state.df_escalas[(st.session_state.df_escalas['Data da Escala']!=st.session_state.df_escalas['Data Execucao']) & 
                                                              ((st.session_state.df_escalas['Data da Escala']>=hoje) | (st.session_state.df_escalas['Data Execucao']>=hoje))].reset_index(drop=True)

atualizar_phoenix = st.button('Atualizar Dados Phoenix')

if atualizar_phoenix:

    st.session_state.df_escalas = gerar_df_phoenix('vw_payment_guide', base_luck)

    st.session_state.df_escalas = st.session_state.df_escalas[~pd.isna(st.session_state.df_escalas['Escala'])].reset_index(drop=True)

    st.session_state.df_escalas = st.session_state.df_escalas[(st.session_state.df_escalas['Data da Escala']!=st.session_state.df_escalas['Data Execucao']) & 
                                                              ((st.session_state.df_escalas['Data da Escala']>=hoje) | (st.session_state.df_escalas['Data Execucao']>=hoje))].reset_index(drop=True)

if len(st.session_state.df_escalas)>0:

    plotar_tabela(st.session_state.df_escalas)

else:

    st.markdown('*Não existem reservas para serem desescaladas no futuro*')

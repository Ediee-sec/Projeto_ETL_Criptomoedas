import log
import pyodbc
import pandas as pd
import api

#Recebe os dados da API
data = api.ticker()
data_size = len(data['Id_Trade'])

# Função que cria a conexão com o banco de dados
def connect():
    driver = 'SQL Server'
    server = 'EMERSON-PEREIRA\SQLEXPRESS'
    db = 'CriptoCoins'

    string =    (
                    'Driver={'+driver+'};'
                    'Server='+server+';'
                    'DATABASE='+db+';'
                )

    conn = pyodbc.connect(string)
    return conn

#Função que insere os dados na tabela
def insert():
    conn = connect()
    cursor = conn.cursor()
    for x in range(data_size):
        try:
             cursor.execute     (
                                f"""
                                    INSERT INTO Coins (COD_TRADE, COIN, PRICE_DOLL, PRICE_REAL, VOLUME, SIZE, DTREF)
                                    VALUES  (   '{data['Id_Trade'][x]}', 
                                                '{data['Moeda'][x]}', 
                                                {data['Preco Dolar'][x]}, 
                                                {data['Preco Reais'][x]}, 
                                                '{data['Volume'][x]}', 
                                                '{data['Tamanho'][x]}',
                                                GETDATE()                                            
                                            )
                                """
                                )
        except(pyodbc.ProgrammingError) as erro:
            log.CRIT_logBD(erro)
            cursor.rollback()

    cursor.commit()
    log.INFO_logBD(data_size)

#Função que cria um arquivo em excel e adciona os dados de forma tabulada
def data_analysis():
    try:
        df = pd.DataFrame(data)
        log.INFO_logPD(data_size)
    except ValueError as error:
        log.CRIT_logBD(error)
    df.to_excel(r'C:\Users\T-Gamer\Downloads\cripto_moedas.xlsx',
                sheet_name="Principal", encoding='utf-8-sig', index=False, header=True)

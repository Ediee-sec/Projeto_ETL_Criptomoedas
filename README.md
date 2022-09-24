## Projeto com foco em Dados

* *Este prjeto foi desenvolvido de forma totalmente idenpendente ou seja, não tirei a lógica ou ideia do mesmo de nenhum video ou curso*
-----
### Resumo
> *O projeto tem por finalizade colocar todos os atributos do ETL em prática, onde inicio extraindo os dados de algumas API, faço o tratamento dos dados extraidos e depois carrego os mesmos em uma tabela no banco de dados e em uma planinha de Excel.*

### Detalhes do projeto
> *Extrair os dados da API da Coinbase referente ao mercado de criptoativos, extrair todas as moedas listadas e seus respectivos valores e carregar esses valores em um banco de dados e um arquivo de Excel, desta forma transformamos o dado em informação para que a analise possa ser realizada por especialistas no mercado.*

### Melhoria futura
> *Como os dados são carregados em uma tabela no banco dados em uma tabela incremental, podemos então guardar o historico da mesma moeda ao longo do tempo de cada carregamento, isso possibilita a criação de BI mais elaborados.*

-----------------

## Mapa do código

 * Bibliotecas
 
 1. [Resquests](https://requests.readthedocs.io/en/latest/)
 2. [Pandas](https://pandas.pydata.org/docs/index.html)
 3. [Pyodbc](https://github.com/mkleehammer/pyodbc/wiki)
 4. [Logging](https://docs.python.org/3/library/logging.html)
 
----

> Desenvolvi o programa utilizando a modularização para facilitar o desenvolvimento e a manutenção, ou seja cada parte do ETL tem o seu proprio módulo e irei separar cada modulo por um topico destacado

----

* **Modulo API, representa a extração e transformação dos dados as letras "E" e "T" do ETL** (**E**xtract e **T**ransform)

~~~python
import requests
import  pandas as pd

#Faz a consulta na API de cotação para fazer a conversão do dolar para o real de forma atualizada
api_cot = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
req = requests.get(api_cot)
conv_cot = float(req.json()['USDBRL']['bid'])

# Cria o dicionario de dados vazio, para posteriormente preenche-lo quando tiver os dados tratados
dic_df = \
        {
            'Id_Trade'        :   [],
            'Moeda'           :   [],
            'Preco Dolar'     :   [],
            'Preco Reais'     :   [],
            'Volume'          :   [],
            'Tamanho'         :   []
        }

# Está função retorna todas as criptomoedas da Coinbase, retorna apenas o nome da criptomeda
def listCoins():
    url = f"https://api.exchange.coinbase.com/products"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    ls = response.json()

    coin = []


    for i in range(len(ls)):
        if "USD" in ls[i]['id']:
            id = ls[i]['id']
            uri = f"https://api.exchange.coinbase.com/products/{id}"
            req = requests.get(uri, headers=headers)
            prod = req.json()

            #Validação,
            # 1 - Verifica se o status da moeda é online,
            # 2 - Verifica se a moeda já tem preço listado,
            # 3 - Verifica se o retorno do request deu sucesso
            # Se as 3 validações for verdadeiro inicia o processo de Transform e appenda apenas a moeda no dicionário dic_df
            if prod['status'] == 'online' and prod['cancel_only'] == False and req.status_code == 200:
                coin.append(id)
                etl_id = id.replace('-', '').replace('USD', '')
                dic_df['Moeda'].append(etl_id)

    return coin

#Função que retorna o dicionário de dados já totalmente preechido
def ticker():
    #Itera sobre a função que contem todos os nomes das moedas
    for i in listCoins():
        url = f"https://api.exchange.coinbase.com/products/{i}/ticker"
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers)
        ls = response.json()

        #Realizar o append no dicionario de dados preenchendo rodos os atributos
        #Está função é a que chamaremos nos demais modulos, sempre que quisermos acesso aos dados que foram extraidos
        if ls['ask'] != "0":
            dic_df['Id_Trade'].append(int(ls['trade_id']))
            dic_df['Preco Dolar'].append(round(float(ls['price']), 4))
            dic_df['Preco Reais'].append(round(float(ls['price']), 4) * conv_cot) #Utiliza a conversão do dolar para o real de forma atualizada
            dic_df['Volume'].append(round(float(ls['volume']), 10))
            dic_df['Tamanho'].append(round(float(ls['size']), 10))

    return dic_df
~~~

-----------

* **Módulo Database, representa o carregamento dos dados, em um SGBD(SQL Server) e no Excel, sendo assim a letra "L" do ETL**(**L**oad)

~~~python
import log # Modulo criado dentro desta aplicação
import pyodbc
import pandas as pd
import api # Modulo criado dentro desta aplicação

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

#Função que insere os dados na tabela do banco de dados
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

~~~
<img src = img/img_2.png>
<img src = img/img_3.png>

------------------

* **Módulo log que registra em um arquivo de log as operações realizadas na aplicação**

~~~python
import logging

#Modulo que cria menssagens de log para controle da aplicação

def cfg():
    config = logging.basicConfig(level=logging.DEBUG, filename='console.log',
                            filemode='a', format='%(levelname)s - %(message)s - %(asctime)s')
    return config

def INFO_logPD(a):
    cfg()
    logging.info(f'Foram adcionados {a} registros ao arquivos xlsx (Excel) com sucesso!')

def INFO_logBD(a):
    cfg()
    logging.info(f'Foram Adcionados {a} registro ao banco de dados com sucesso!')


def CRIT_logBD(a):
    cfg()
    logging.critical(f'Erro {a} ao tentar inserir informação no banco de dados!')


def CRIT_logPD(a):
    cfg()
    logging.critical(f'Erro {a} ao tentar inserir informação no Excel!')

~~~
<img src = img/img.png>
----------

* **Módulo main responsável por orquestrar a aplicação**

~~~python
import DataBase

#Modulo main, responsável por orquestrar a aplicação e chamar apenas oque deve ser executado

#Chama a função que insere os dados no banco de dados
DataBase.insert()

#Chama a função que insere os dados no Excel
DataBase.data_analysis()
~~~

---------------

* **Criando o banco de dados bo SQL Server**

~~~sql
CREATE TABLE Coins
(
	ID 			SMALLINT PRIMARY KEY IDENTITY,
	COD_TRADE	VARCHAR	(MAX)	NOT NULL,
	COIN		VARCHAR	(10)	NOT NULL,
	PRICE_DOLL	DECIMAL	(10,2)	NOT NULL,
	PRICE_REAL	DECIMAL	(10,2)	NOT NULL,
	VOLUME		VARCHAR	(MAX)	NULL,
	SIZE		VARCHAR	(MAX)	NULL,
	DTREF		DATETIME		NOT NULL,	
)	
~~~

----------
*O projeto tem potencial para ir além, se alguém quiser contribuir pode me chamar no linkedin*
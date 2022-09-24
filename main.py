import DataBase

#Modulo main, responsável por orquestrar a aplicação e chamar apenas oque deve ser executado

#Chama a função que insere os dados no banco de dados
DataBase.insert()

#Chama a função que insere os dados no Excel
DataBase.data_analysis()
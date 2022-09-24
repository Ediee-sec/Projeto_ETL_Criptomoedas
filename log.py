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


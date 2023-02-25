import os
from flask import Flask, request, Response
from repository import db_repository
import json
from utils import utils
import ConnDB as c

app = Flask(__name__)
db = db_repository()

@app.route('/')
def index():
    
    return Response('{"detalhes" : "running"}', status=204, mimetype='application/json')

@app.route('/db-credentials', methods = ['GET'])
def db_credentials():
    return c.get_credentials()

@app.route('/consultar-pergunta/<int:id>', methods = ['GET'])
def consultar_pergunta(id):
    pergunta, respostas = db.get_pergunta(id)
    pergunta, respostas = utils.sql_to_json(pergunta), utils.sql_to_json(respostas)
    pergunta[0]['respostas'] = respostas

    response = app.response_class(response=json.dumps(pergunta), status=200, mimetype='application/json')
    return response

@app.route('/consultar-ranking/<int:qtd_registros>', methods = ['GET'])
def consultar_ranking(qtd_registros):
    ranking = db.get_ranking(qtd_registros)
    ranking = utils.sql_to_json(ranking)

    response = app.response_class(response=json.dumps(ranking), status=200, mimetype='application/json')
    return response

@app.route('/inserir-ranking', methods = ['POST'])
def inserir_ranking():
    if not request.json:
        return Response('{"detalhes" : "insira um json no body"}',
                        status=400, mimetype='application/json')

    jogador =  request.json['jogador']
    tempo_decorrido =  request.json['tempo_decorrido']
    retorno = db.insert_ranking(jogador, tempo_decorrido)

    return retorno

@app.route('/inserir-pergunta', methods = ['POST'])
def inserir_pergunta():
    if not request.json:
        return Response('{"detalhes" : "insira um json no body"}',
                        status=400, mimetype='application/json')
    
    dataJson =  request.json
    retorno = db.insert_pergunta(dataJson)
    return retorno

@app.route('/excluir-pergunta/<int:id>', methods = ['DELETE'])
def excluir_pergunta(id):
    retorno = db.delete_pergunta(id)
    return retorno

@app.route('/excluir-jogador/<username>', methods = ['DELETE'])
def excluir_jogador(username):
    retorno = db.delete_ranking(username)
    return retorno

@app.route('/consultar-id-perguntas', methods = ['GET'])
def consultar_id_perguntas():
    retorno = db.get_all_id_perguntas()
    return retorno

if __name__ == '__main__':
    app.run()
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import final
from sqlalchemy import insert, delete, update
from datetime import datetime
import time
from ConnDB import ConnDB
from flask import Response, jsonify
from utils import utils 
from ConnDB import ConnDB

class db_repository:
    def __init__(self):
        
        self.db = ConnDB()

    def get_pergunta(self, id_pergunta):
        try:
            pergunta = self.db.session.execute(f'''SELECT 
                                            id as id_pergunta,
                                            descricao as pergunta,
                                            explicacao, 
                                            '' as respostas
                                            FROM perguntas
                                            WHERE id = {id_pergunta}''')
            
            respostas = self.db.session.execute(f'''select 
                                            descricao as resposta,
                                            correta
                                            from respostas r
                                            WHERE r.id_pergunta  = {id_pergunta}''')                       
            return pergunta, respostas
        except Exception as e:
            return Response('{"detalhes" : "erro ao consultar a pergunta, verifique o id."}', 
                            status=404, mimetype='application/json')
        finally:
            self.db.close_connection()

    def get_ranking(self, qtd_registros):
        try: 
            ranking = self.db.session.execute(f'''select jogador, tempo_decorrido
                                            from ranking
                                            order by tempo_decorrido asc
                                            limit {qtd_registros}''')
            return ranking
        except Exception as e:
                return Response('{"detalhes" :  "erro ao consultar ranking, verifique a quantidade de registros solicitada no endpoint."}',
                                status=400, mimetype='application/json')
        finally:
            self.db.close_connection()

    def insert_ranking(self, username, elapsed_time):
        ranking = utils.sql_to_json(self.db.session.execute(f"select jogador, tempo_decorrido from ranking where jogador = '{username}'"))
        try: 
            if ranking:
                tempo_tabela = time.strptime(ranking[0]['tempo_decorrido'],'%H:%M:%S')
                tempo_novo = time.strptime(elapsed_time,'%H:%M:%S')

                if (tempo_tabela > tempo_novo):
                    self.db.session.execute(update(self.db.r).where(self.db.r.jogador == username).values(tempo_decorrido = elapsed_time))
                    self.db.session.commit()
                    return Response('{"detalhes" : "tempo do usuário atualizado com sucesso."}', status=204, mimetype='application/json')
                return Response('{"detalhes" : "usuário não bateu o tempo já existente."}', status=204, mimetype='application/json')

            else:
                self.db.session.execute(insert(self.db.meta.tables['ranking']).values(jogador = username, tempo_decorrido = elapsed_time, data_hora = datetime.now()))
                self.db.session.commit()
                return Response('{"detalhes" : "usuário inserido com sucesso."}', status=201, mimetype='application/json')
        except Exception as e:
                return Response('{"detalhes" :  "erro ao inserir no ranking, verifique o json no body."}',
                                status=400, mimetype='application/json')
        finally:
            self.db.close_connection()

    def insert_pergunta(self, dataJson):
        dataJson = utils.to_json(dataJson)
        pergunta = dataJson['pergunta']
        pergunta_existe = utils.sql_to_json(self.db.session.execute(f"select * from perguntas where descricao like '%{pergunta}%'"))
        
        if pergunta_existe:
            return Response('{"detalhes" : "a pergunta já existe no banco"}',
                    status=204, mimetype='application/json')
        else: 
            try: 
                result_pergunta = self.db.session.execute(insert(self.db.meta.tables['perguntas']).
                    values(descricao = pergunta, explicacao = dataJson['explicacao']))

                id_pergunta = (result_pergunta.inserted_primary_key)
                id_pergunta = int(str(id_pergunta).replace(",", "").replace("(","").replace(")",""))

                for resposta in dataJson['respostas']:
                    result_respostas = self.db.session.execute(insert(self.db.meta.tables['respostas']).
                        values(id_pergunta = id_pergunta, descricao = resposta['resposta'], correta = resposta['correta']))

                self.db.session.commit()

                return Response('{"detalhes" :  "pergunta/respostas inseridas com sucesso."}', status=200, mimetype='application/json')
            
            except Exception as e:
                return Response('{"detalhes" :  "erro ao inserir a pergunta, verifique o json no body."}',
                                status=400, mimetype='application/json')
            finally:
                self.db.close_connection()

    def delete_pergunta(self, id_pergunta):
        try:    
            resposta_existe = utils.sql_to_json(self.db.session.execute(f"select * from respostas where id_pergunta = {id_pergunta}"))
            if resposta_existe:
                self.db.session.execute(delete(self.db.resp).where(self.db.resp.id_pergunta == id_pergunta))
                self.db.session.commit()

            pergunta_existe = utils.sql_to_json(self.db.session.execute(f"select * from perguntas where id = {id_pergunta}"))
            if pergunta_existe:
                self.db.session.execute(delete(self.db.p).where(self.db.p.id == id_pergunta))
                self.db.session.commit()
            
            return Response('{"detalhes" : "pergunta/respostas deletadas."}',
                    status=200, mimetype='application/json')
            
        except Exception as e:
                return Response('{"detalhes" :  "erro ao deletar a pergunta/respostas, tente novamente mais tarde."}',
                                status=400, mimetype='application/json')
        finally:
            self.db.close_connection()

    def delete_ranking(self, username):
        try:    
            resposta_existe = utils.sql_to_json(self.db.session.execute(f"select * from ranking where jogador = '{username}'"))
            if resposta_existe:
                self.db.session.execute(delete(self.db.r).where(self.db.r.jogador == username))
                self.db.session.commit()

                return Response('{"detalhes" : "usuário deletado com sucesso."}',
                    status=200, mimetype='application/json')
            else:
                return Response('{"detalhes" : "o usuário não existe no banco de dados."}',
                    status=204, mimetype='application/json')
            
        except Exception as e:
                return Response('{"detalhes" :  "erro ao deletar usuário, tente novamente mais tarde."}',
                                status=400, mimetype='application/json')
        finally:
            self.db.close_connection()

    def get_all_id_perguntas(self):
        try: 
            ids = self.db.session.execute('select id from perguntas p')
            rows = ids.fetchall()
            lista_ids = utils.sql_to_list(rows)
            return jsonify(lista_ids)
        except Exception as e:
                return Response('{"detalhes" :  "erro ao consultar os ids existentes, contate o administrador do sistema."}',
                                status=400, mimetype='application/json')
        finally:
            self.db.close_connection()
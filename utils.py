import json

class utils: 
    def sql_to_json(sql):
        dataJson = json.dumps( [dict(ix) for ix in sql], ensure_ascii=False, default=str).encode('utf-8')
        return json.loads(dataJson.decode())

    def to_json(data):
        dataJson = json.dumps(data).encode('utf-8')
        dataJson = json.loads(dataJson.decode())
        return dataJson

    def sql_to_list(cursor):
        Arraylist = []
        lista_final = []
        for row in cursor:
            Arraylist.append([x for x in row]) # or simply data.append(list(row))

        for i in Arraylist:
            for x in i:
                lista_final.append(x)
        return lista_final
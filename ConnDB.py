import os
from sqlalchemy import create_engine, MetaData, insert, delete, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base

class ConnDB:
    def __init__(self):
        uri = get_credentials()
        
        self.engine= create_engine(uri, pool_pre_ping=True,
                                            connect_args={
                                            "keepalives": 1,
                                            "keepalives_idle": 30,
                                            "keepalives_interval": 10,
                                            "keepalives_count": 5
                                            },
                                            encoding="utf8")

        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.meta = MetaData()
        self.meta.reflect(bind=self.engine)
        self.Base = automap_base()
        self.Base.prepare(self.engine, reflect=True)
        self.r = self.Base.classes.ranking
        self.p = self.Base.classes.perguntas
        self.resp = self.Base.classes.respostas

    def close_connection(self):
        self.engine.dispose()
    
def get_credentials():
    credentials = str(os.environ['DATABASE_URL']).replace('postgres', 'postgresql')
    uri = str(credentials) + '?client_encoding=utf8'
    return uri
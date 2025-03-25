import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
import oracledb
# from dotenv import load_dotenv

# load_dotenv()

# Configuração do banco de dados
ORACLE_USER="CAIXA"
ORACLE_PASSWORD="CAIXA"
ORACLE_HOST="localhost"
ORACLE_PORT="1521"
ORACLE_SID="XEPDB1"

# URL de conexão no formato correto para oracledb
DATABASE_URL = f"oracle+oracledb://{ORACLE_USER}:{ORACLE_PASSWORD}@{ORACLE_HOST}:{ORACLE_PORT}/?service_name={ORACLE_SID}"

# Configuração do engine do SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)  # echo=True para logs de SQL no console
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# Função para obter uma sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Context manager para usar em blocos 'with'
db_context = contextmanager(get_db)
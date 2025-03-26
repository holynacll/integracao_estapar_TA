import os
import platform
from contextlib import contextmanager
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
import oracledb

from totalatacadot1.config import get_project_root, get_orcl_instant_client_path, get_orcl_instant_client_path_zipped


def setup_oracle_client():
    if platform.system() == "Windows":
        oracle_client_path = get_orcl_instant_client_path()

        if not oracle_client_path.exists():
            orcl_instant_client_zip = get_orcl_instant_client_path_zipped()
            if orcl_instant_client_zip.exists():
                shutil.unpack_archive(str(orcl_instant_client_zip), str(get_project_root()))

        if oracle_client_path.exists():  # Verifica novamente após extração
            oracledb.init_oracle_client(lib_dir=str(oracle_client_path))

setup_oracle_client()

# from dotenv import load_dotenv

# load_dotenv()

# Configuração do banco de dados
ORACLE_USER="CAIXA"
ORACLE_PASSWORD="CAIXA"
ORACLE_HOST="localhost"
ORACLE_PORT="1521"

# URL de conexão no formato correto para oracledb
if platform.system() == "Windows":
    ORACLE_SID="XE"
    DATABASE_URL = f"oracle+oracledb://{ORACLE_USER}:{ORACLE_PASSWORD}@{ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_SID}"
else:
    ORACLE_SID="XEPDB1"
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



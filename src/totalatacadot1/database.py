from pathlib import Path
import platform
from contextlib import contextmanager
import shutil

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import oracledb

from totalatacadot1.config import (
    get_project_root,
    get_orcl_instant_client_path,
    get_orcl_instant_client_path_zipped,
)


def setup_oracle_client():
    if platform.system() == "Windows":
        oracle_client_path = get_orcl_instant_client_path()

        if not oracle_client_path.exists():
            orcl_instant_client_zip = get_orcl_instant_client_path_zipped()
            if orcl_instant_client_zip.exists():
                shutil.unpack_archive(
                    str(orcl_instant_client_zip), str(get_project_root())
                )

        if oracle_client_path.exists():  # Verifica novamente após extração
            oracledb.init_oracle_client(lib_dir=str(oracle_client_path))


setup_oracle_client()

# from dotenv import load_dotenv

# load_dotenv()

# Configuração do banco de dados
ORACLE_USER = "CAIXA"
ORACLE_PASSWORD = "CAIXA"
ORACLE_HOST = "localhost"
ORACLE_PORT = "1521"

DATABASE_URLS = [
    f"oracle+oracledb://{ORACLE_USER}:{ORACLE_PASSWORD}@{ORACLE_HOST}:{ORACLE_PORT}/?service_name=XEPDB1",
    f"oracle+oracledb://{ORACLE_USER}:{ORACLE_PASSWORD}@{ORACLE_HOST}:{ORACLE_PORT}/XE",
]

# Configurações do banco de dados SQLite
SQLITE_DB_PATH = Path(get_project_root()) / "data" / "control_pdv.db"
SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)  # Cria o diretório se não existir
SQLITE_URL = f"sqlite:///{SQLITE_DB_PATH}"

class BaseOracle(DeclarativeBase):
    pass

class BaseSQLite(DeclarativeBase):
    pass


oracle_engine = None
sqlite_engine = None
for database_url in DATABASE_URLS:
    try:
        oracle_engine = create_engine(database_url, echo=True)  # echo=True para logs de SQL no console
        connection = oracle_engine.connect()
        connection.close()
        logger.info(f"Conexão Oracle bem-sucedida: {database_url}")
        break
    except Exception as e:
        logger.error(f"Erro ao conectar ao Oracle: {database_url}. Erro: {e}")

if oracle_engine is None:
    raise RuntimeError("Nenhuma conexão com o Oracle foi estabelecida.")

# Configuração do engine do SQLite
sqlite_engine = create_engine(
    SQLITE_URL,
    echo=True,
    connect_args={"check_same_thread": False}  # Necessário para SQLite em aplicações multi-thread
)

# Criar as sessões para cada banco de dados
OracleSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=oracle_engine)
SQLiteSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sqlite_engine)


# Função para obter uma sessão do Oracle
def get_oracle_db():
    db = OracleSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função para obter uma sessão do SQLite
def get_sqlite_db():
    db = SQLiteSessionLocal()
    try:
        yield db
    finally:
        db

# Context manager para usar em blocos 'with'
db_oracle_context = contextmanager(get_oracle_db)
db_sqlite_context = contextmanager(get_sqlite_db)

# Funções para criar as tabelas no SQLite (se não existirem)
def create_sqlite_tables():
    BaseSQLite.metadata.create_all(bind=sqlite_engine, checkfirst=True)

# Funções para criar as tabelas no Oracle
def create_oracle_tables():
    BaseOracle.metadata.create_all(bind=oracle_engine, checkfirst=True)

# Função para inicializar o banco de dados
def init_db():
    logger.info("Iniciando a inicialização do banco de dados...")
    create_sqlite_tables()
    logger.info("Tabelas SQLite criadas com sucesso.")
    create_oracle_tables()
    logger.info("Tabelas Oracle criadas com sucesso.")
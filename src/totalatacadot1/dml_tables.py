from totalatacadot1.database import Base, engine
from totalatacadot1.models import PCPEDCECF, PCPEDCECFItem

def create_tables():
    # Criar tabelas se não existirem
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("Tabelas criadas com sucesso!")

def remove_tables():
    # Remover tabelas se existirem
    Base.metadata.drop_all(bind=engine, checkfirst=True)
    print("Tabelas removidas com sucesso!")


if __name__ == "__main__":
    remove_tables()
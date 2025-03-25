from sqlalchemy.orm import Session
from totalatacadot1.database import engine, Base, SessionLocal
from totalatacadot1.models import PDV, PDVItem
from datetime import datetime

# Criar as tabelas no banco de dados
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")

# Inserir dados iniciais na tabela PDV
def populate_pdv():
    session = SessionLocal()
    try:
        # Verificar se já existem registros para evitar duplicação
        existing_records = session.query(PDV).first()
        if existing_records:
            print("A tabela PDV já contém dados. Nenhuma inserção necessária.")
            return

        # Inserindo registros iniciais
        pdv_data = [
            PDV(
                num_ped_ecf=11397,
                num_caixa=303,
                data=datetime.strptime("1/7/25 0:00", "%m/%d/%y %H:%M").strftime("%m/%d/%y %H:%M"),
                hora_cupom=datetime.strptime("19:58:47", "%H:%M:%S").strftime("%H:%M:%S"),
                num_cupom=10429,
                vl_total=12.69,
            ),
            PDV(
                num_ped_ecf=11398,
                num_caixa=303,
                data=datetime.strptime("1/7/25 0:00", "%m/%d/%y %H:%M").strftime("%m/%d/%y %H:%M"),
                hora_cupom=datetime.strptime("19:58:47", "%H:%M:%S").strftime("%H:%M:%S"),
                num_cupom=10430,
                vl_total=12.69,
            ),
            PDV(
                num_ped_ecf=11399,
                num_caixa=303,
                data=datetime.strptime("1/7/25 0:00", "%m/%d/%y %H:%M").strftime("%m/%d/%y %H:%M"),
                hora_cupom=datetime.strptime("19:58:47", "%H:%M:%S").strftime("%H:%M:%S"),
                num_cupom=10431,
                vl_total=12.69,
            )
        ]

        session.add_all(pdv_data)
        session.commit()
        print("Registros inseridos com sucesso!")

    except Exception as e:
        session.rollback()
        print(f"Erro ao inserir registros: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    create_tables()
    populate_pdv()

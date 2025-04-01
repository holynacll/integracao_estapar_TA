from loguru import logger
from totalatacadot1.database import OracleSessionLocal
from totalatacadot1.models import PCPEDCECF
from datetime import datetime


# Inserir dados iniciais na tabela PCPEDCECF
def populate_pdv():
    session_oracle = OracleSessionLocal()
    try:
        # Verificar se já existem registros para evitar duplicação
        existing_records = session_oracle.query(PCPEDCECF).first()
        if existing_records:
            logger.info(
                "A tabela PCPEDCECF já contém dados. Nenhuma inserção necessária."
            )
            return

        # Inserindo registros iniciais
        pdv_data = [
            PCPEDCECF(
                num_ped_ecf=11397,
                num_caixa=303,
                data=datetime.strptime("1/7/25 0:00", "%m/%d/%y %H:%M").strftime(
                    "%m/%d/%y %H:%M"
                ),
                hora_cupom=datetime.strptime("19:58:47", "%H:%M:%S").strftime(
                    "%H:%M:%S"
                ),
                num_cupom=10429,
                vl_total=12.69,
            ),
            PCPEDCECF(
                num_ped_ecf=11398,
                num_caixa=303,
                data=datetime.strptime("1/7/25 0:00", "%m/%d/%y %H:%M").strftime(
                    "%m/%d/%y %H:%M"
                ),
                hora_cupom=datetime.strptime("19:58:47", "%H:%M:%S").strftime(
                    "%H:%M:%S"
                ),
                num_cupom=10430,
                vl_total=12.69,
            ),
            PCPEDCECF(
                num_ped_ecf=11399,
                num_caixa=303,
                data=datetime.strptime("1/7/25 0:00", "%m/%d/%y %H:%M").strftime(
                    "%m/%d/%y %H:%M"
                ),
                hora_cupom=datetime.strptime("19:58:47", "%H:%M:%S").strftime(
                    "%H:%M:%S"
                ),
                num_cupom=10431,
                vl_total=12.69,
            ),
        ]

        session_oracle.add_all(pdv_data)
        session_oracle.commit()
        logger.info("Registros inseridos com sucesso!")

    except Exception as e:
        session_oracle.rollback()
        logger.info(f"Erro ao inserir registros: {e}")
    finally:
        session_oracle.close()


if __name__ == "__main__":
    populate_pdv()

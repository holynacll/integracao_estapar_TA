import sys
from datetime import datetime, timedelta
from pathlib import Path

from loguru import logger

from totalatacadot1.database import OracleSessionLocal
from totalatacadot1.models import PCPEDCECF

# Pega o caminho absoluto da pasta 'src' e adiciona no PATH do Python
src_path = Path(__file__).resolve().parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


# Inserir dados iniciais na tabela PCPEDCECF
def populate_pdv():
    session_oracle = OracleSessionLocal()
    try:
        # Verificar se já existem registros para evitar duplicação
        # existing_records = session_oracle.query(PCPEDCECF).first()
        # if existing_records:
        #     logger.info(
        #         "A tabela PCPEDCECF já contém dados. Nenhuma inserção necessária."
        #     )
        #     return

        # Inserindo registros iniciais
        pdv_data = [
            PCPEDCECF(
                num_ped_ecf=7765,
                num_caixa=303,
                data=datetime.today() - timedelta(days=1),
                hora_cupom="19:58:47",
                num_cupom=10555,
                vl_total=120.69,
            ),
            PCPEDCECF(
                num_ped_ecf=656,
                num_caixa=303,
                data=datetime.today(),
                hora_cupom="19:58:47",
                num_cupom=6767,
                vl_total=88.69,
            ),
            PCPEDCECF(
                num_ped_ecf=65756,
                num_caixa=303,
                data=datetime.today(),
                hora_cupom="19:58:47",
                num_cupom=3244,
                vl_total=55.69,
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

from datetime import datetime
from totalatacadot1.database import db_oracle_context, db_sqlite_context
from totalatacadot1.models import PCPEDCECF, ControlPDV


def get_last_pdv_pedido() -> PCPEDCECF:
    vl_limit = 99999999
    with db_oracle_context() as db:
        today = datetime.today().strftime("%d/%m/%y")
        return (
            db.query(PCPEDCECF)
            .filter(PCPEDCECF.data.like(f'{today}%'))  # Para datas com hora
            .filter(PCPEDCECF.vl_total < vl_limit)
            .order_by(PCPEDCECF.num_ped_ecf.desc())
            .first()
        )

def get_pdv_control_item_by_num_ped_ecf(num_ped_ecf: int) -> ControlPDV:
    with db_sqlite_context() as db:
        return (
            db.query(ControlPDV).filter(ControlPDV.num_ped_ecf == num_ped_ecf).first()
        )


def create_pdv_control_item(num_ped_ecf: int) -> ControlPDV:
    pdv_item = ControlPDV(num_ped_ecf=num_ped_ecf, validated=False)
    with db_sqlite_context() as db:
        db.add(pdv_item)
        db.commit()
        db.refresh(pdv_item)
        return pdv_item


from totalatacadot1.database import db_context
from totalatacadot1.models import PDV, PDVItem


def get_last_pdv_pedido() -> PDV:
    with db_context() as db:
        return db.query(PDV).order_by(PDV.num_ped_ecf.desc()).first()

def get_pdv_control_item_by_num_ped_ecf(num_ped_ecf: int) -> PDVItem:
    with db_context() as db:
        return db.query(PDVItem).filter(PDVItem.num_ped_ecf == num_ped_ecf).first()

def create_pdv_control_item(num_ped_ecf: int) -> PDVItem:
    pdv_item = PDVItem(num_ped_ecf=num_ped_ecf, validated=False)
    with db_context() as db:
        db.add(pdv_item)
        db.commit()
        db.refresh(pdv_item)
        return pdv_item

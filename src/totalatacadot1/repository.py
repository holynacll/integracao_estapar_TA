
from totalatacadot1.database import db_context
from totalatacadot1.models import PCPEDCECF, PCPEDCECFItem


def get_last_pdv_pedido() -> PCPEDCECF:
    with db_context() as db:
        return db.query(PCPEDCECF).order_by(PCPEDCECF.num_ped_ecf.desc()).first()

def get_pdv_control_item_by_num_ped_ecf(num_ped_ecf: int) -> PCPEDCECFItem:
    with db_context() as db:
        return db.query(PCPEDCECFItem).filter(PCPEDCECFItem.num_ped_ecf == num_ped_ecf).first()

def create_pdv_control_item(num_ped_ecf: int) -> PCPEDCECFItem:
    pdv_item = PCPEDCECFItem(num_ped_ecf=num_ped_ecf, validated=False)
    with db_context() as db:
        db.add(pdv_item)
        db.commit()
        db.refresh(pdv_item)
        return pdv_item

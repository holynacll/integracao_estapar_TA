import datetime

from sqlalchemy import func

from .database import db_oracle_context, db_sqlite_context
from .models import PCPEDCECF, ControlPDV, NotificationModel


def get_last_pdv_pedido() -> PCPEDCECF | None:
    vl_limit = 99999999
    today = datetime.date.today()
    with db_oracle_context() as db:
        result = (
            db.query(PCPEDCECF)
            .filter(PCPEDCECF.vl_total < vl_limit)
            .filter(func.trunc(PCPEDCECF.data) == today)
            .order_by(PCPEDCECF.num_ped_ecf.desc())
            .first()
        )
        if result is not None:
            db.expunge(result)
        return result


def get_pdv_control_item_by_num_ped_ecf(num_ped_ecf: int) -> ControlPDV | None:
    with db_sqlite_context() as db:
        return (
            db.query(ControlPDV).filter(ControlPDV.num_ped_ecf == num_ped_ecf).first()
        )


def get_pdv_control_item_by_num_ped_ecf_and_today(
    num_ped_ecf: int,
) -> ControlPDV | None:
    today = datetime.date.today()
    with db_sqlite_context() as db:
        return (
            db.query(ControlPDV)
            .filter(
                ControlPDV.num_ped_ecf == num_ped_ecf,
                ControlPDV.data == today,
            )
            .first()
        )


def get_last_control_item_of_the_dat_by_numcupom(num_cupom: int) -> ControlPDV | None:
    today = datetime.date.today()
    with db_sqlite_context() as db:
        return (
            db.query(ControlPDV)
            .filter(
                ControlPDV.num_cupom == num_cupom,
                ControlPDV.data == today,
            )
            .first()
        )


def create_pdv_control_item(
    num_ped_ecf: int,
    num_cupom: int,
    data: datetime.date,
) -> ControlPDV:
    pdv_item = ControlPDV(num_ped_ecf=num_ped_ecf, num_cupom=num_cupom, data=data)
    with db_sqlite_context() as db:
        db.add(pdv_item)
        db.commit()
        db.refresh(pdv_item)
        return pdv_item


def create_notification_item(notification_data: dict) -> NotificationModel:
    notification_item = NotificationModel(
        ticket_code=notification_data.get("ticket_code"), data=notification_data
    )
    with db_sqlite_context() as db:
        db.add(notification_item)
        db.commit()
        db.refresh(notification_item)
        return notification_item


def get_last_notification_not_sent() -> NotificationModel | None:
    with db_sqlite_context() as db:
        notification_item = (
            db.query(NotificationModel)
            .filter(NotificationModel.sent == False)  # noqa: E712
            .order_by(NotificationModel.id.desc())
            .first()
        )
    return notification_item


def update_notification_item_sent(ticket_code: str) -> NotificationModel | None:
    with db_sqlite_context() as db:
        notification_item = (
            db.query(NotificationModel)
            .filter(NotificationModel.ticket_code == ticket_code)
            .filter(NotificationModel.sent == False)  # noqa: E712
            .first()
        )
        if notification_item:
            notification_item.sent = True
            db.commit()
            db.refresh(notification_item)
    return notification_item

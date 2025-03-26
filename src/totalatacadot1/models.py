from datetime import datetime, time

from sqlalchemy import Boolean, DateTime, Integer, Numeric, Sequence, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column
from totalatacadot1.database import Base

# Definição da tabela PDV
class PCPEDCECF(Base):
    __tablename__ = "PCPEDCECF"
    
    num_ped_ecf: Mapped[int] = mapped_column(Integer, name="NUMPEDECF", primary_key=True)
    num_caixa: Mapped[int] = mapped_column(Integer, name="NUMCAIXA", nullable=True)
    data: Mapped[str] = mapped_column(String(20), name="DATA", nullable=True)
    hora_cupom: Mapped[str] = mapped_column(String(20), name="HORACUPOM", nullable=True)
    num_cupom: Mapped[int] = mapped_column(Integer, name="NUMCUPOM", nullable=True)
    vl_total: Mapped[float] = mapped_column(Numeric(10, 2), name="VLTOTAL", nullable=True)

    def __repr__(self) -> str:
        return (
            f"PCPEDCECF(num_ped={self.num_ped_ecf}, "
            f"num_caixa={self.num_caixa}, "
            f"data={self.data}, "
            f"hora_cupom={self.hora_cupom}, "
            f"num_cupom={self.num_cupom})"
            f"vl_total={self.vl_total}, "
        )


class PCPEDCECFItem(Base):
    __tablename__ = "PCPEDCECFItem"
    
    id: Mapped[int] = mapped_column(Integer, Sequence('PCPEDCECFItem_seq'), primary_key=True, name="ID")
    num_ped_ecf: Mapped[int] = mapped_column(Integer, name="NUMPEDECF", nullable=True)
    validated: Mapped[bool] = mapped_column(Boolean, name="VALIDATED", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, name="CREATEDAT", server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, name="UPDATEDAT", server_default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        return (
            f"PCPEDCECFItem(num_ped_ecf={self.num_ped_ecf}, "
            f"validated={self.validated}, "
            f"created_at={self.created_at}, "
            f"updated_at={self.updated_at})"
        )

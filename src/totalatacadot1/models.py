from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, Numeric, Sequence, String, func
from sqlalchemy.orm import Mapped, mapped_column
from totalatacadot1.database import Base

# Definição da tabela PDV
class PDV(Base):
    __tablename__ = "PDV"
    
    exportado: Mapped[str] = mapped_column(String(1), name="EXPORTADO", nullable=True)
    num_ped_ecf: Mapped[int] = mapped_column(Integer, name="NUMPEDECF", primary_key=True)
    cod_func_cx: Mapped[int] = mapped_column(Integer, name="CODFUNCCX", nullable=True)
    num_caixa: Mapped[int] = mapped_column(Integer, name="NUMCAIXA", nullable=True)
    num_serie_equip: Mapped[str] = mapped_column(String(50), name="NUMSERIEEQUIP", nullable=True)
    data: Mapped[datetime] = mapped_column(DateTime, name="DATA", nullable=True)
    cod_filial: Mapped[int] = mapped_column(Integer, name="CODFILIAL", nullable=True)
    cod_cli: Mapped[int] = mapped_column(Integer, name="CODCLI", nullable=True)
    cod_usur: Mapped[int] = mapped_column(Integer, name="CODUSUR", nullable=True)
    cod_praca: Mapped[int] = mapped_column(Integer, name="CODPRACA", nullable=True)
    cod_supervisor: Mapped[int] = mapped_column(Integer, name="CODSUPERVISOR", nullable=True)
    cod_plpag: Mapped[int] = mapped_column(Integer, name="CODPLPAG", nullable=True)
    posicao: Mapped[str] = mapped_column(String(5), name="POSICAO", nullable=True)
    cond_venda: Mapped[int] = mapped_column(Integer, name="CONDVENDA", nullable=True)
    per_venda: Mapped[float] = mapped_column(Numeric(10, 2), name="PERCVENDA", nullable=True)
    num_cupom: Mapped[int] = mapped_column(Integer, name="NUMCUPOM", nullable=True)
    serie_ecf: Mapped[str] = mapped_column(String(10), name="SERIEECF", nullable=True)
    cod_cob: Mapped[str] = mapped_column(String(5), name="CODCOB", nullable=True)
    cod_emitente: Mapped[int] = mapped_column(Integer, name="CODEMITENTE", nullable=True)
    dt_entrega: Mapped[DateTime] = mapped_column(DateTime, name="DTENTREGA", nullable=True)
    vl_atend: Mapped[float] = mapped_column(Numeric(10, 2), name="VLATEND", nullable=True)
    vl_total: Mapped[float] = mapped_column(Numeric(10, 2), name="VLTOTAL", nullable=True)
    vl_tabela: Mapped[float] = mapped_column(Numeric(10, 2), name="VLTABELA", nullable=True)
    vl_desconto: Mapped[float] = mapped_column(Numeric(10, 2), name="VLDESCONTO", nullable=True)
    tipo_venda: Mapped[str] = mapped_column(String(5), name="TIPOVENDA", nullable=True)
    vl_outras_despesas: Mapped[float] = mapped_column(Numeric(10, 2), name="VLOUTRASDESP", nullable=True)
    num_itens: Mapped[int] = mapped_column(Integer, name="NUMITENS", nullable=True)
    hora: Mapped[int] = mapped_column(Integer, name="HORA", nullable=True)
    minuto: Mapped[int] = mapped_column(Integer, name="MINUTO", nullable=True)
    prazo1: Mapped[float] = mapped_column(Numeric(10, 2), name="PRAZO1", nullable=True)
    prazo2: Mapped[float] = mapped_column(Numeric(10, 2), name="PRAZO2", nullable=True)
    prazo3: Mapped[float] = mapped_column(Numeric(10, 2), name="PRAZO3", nullable=True)
    prazo4: Mapped[float] = mapped_column(Numeric(10, 2), name="PRAZO4", nullable=True)
    prazo5: Mapped[float] = mapped_column(Numeric(10, 2), name="PRAZO5", nullable=True)
    prazo6: Mapped[float] = mapped_column(Numeric(10, 2), name="PRAZO6", nullable=True)
    prazo7: Mapped[float] = mapped_column(Numeric(10, 2), name="PRAZO7", nullable=True)
    prazo8: Mapped[float] = mapped_column(Numeric(10, 2), name="PRAZO8", nullable=True)
    prazo9: Mapped[float] = mapped_column(Numeric(10, 2), name="PRAZO9", nullable=True)
    prazo10: Mapped[float] = mapped_column(Numeric(10, 2), name="PRAZO10", nullable=True)
    prazo11: Mapped[float] = mapped_column(Numeric(10, 2), name="PRAZO11", nullable=True)
    prazo12: Mapped[float] = mapped_column(Numeric(10, 2), name="PRAZO12", nullable=True)
    prazo_medio: Mapped[float] = mapped_column(Numeric(10, 2), name="PRAZOMEDIO", nullable=True)
    num_vias_mapa_sep: Mapped[int] = mapped_column(Integer, name="NUMVIASMAPASEP", nullable=True)
    operacao: Mapped[str] = mapped_column(String(10), name="OPERACAO", nullable=True)
    vl_custo_real: Mapped[float] = mapped_column(Numeric(10, 2), name="VLCUSTOREAL", nullable=True)
    vl_custo_fin: Mapped[float] = mapped_column(Numeric(10, 2), name="VLCUSTOFIN", nullable=True)
    tot_peso: Mapped[float] = mapped_column(Numeric(10, 2), name="TOTPESO", nullable=True)
    tot_volume: Mapped[float] = mapped_column(Numeric(10, 2), name="TOTVOLUME", nullable=True)
    vl_custo_rep: Mapped[float] = mapped_column(Numeric(10, 2), name="VLCUSTOREP", nullable=True)
    vl_custo_cont: Mapped[float] = mapped_column(Numeric(10, 2), name="VLCUSTOCONT", nullable=True)
    num_ped: Mapped[int] = mapped_column(Integer, name="NUMPED", nullable=True)
    num_car: Mapped[int] = mapped_column(Integer, name="NUMCAR", nullable=True)
    num_transvenda: Mapped[int] = mapped_column(Integer, name="NUMTRANSVENDA", nullable=True)
    dt_fat: Mapped[datetime] = mapped_column(DateTime, name="DTFAT", nullable=True)
    hora_fat: Mapped[int] = mapped_column(Integer, name="HORAFAT", nullable=True)
    minuto_fat: Mapped[int] = mapped_column(Integer, name="MINUTOFAT", nullable=True)
    importado: Mapped[str] = mapped_column(String(1), name="IMPORTADO", nullable=True)
    posicao_retorno: Mapped[str] = mapped_column(String(50), name="POSICAORETORNO", nullable=True)
    dt_exportacao: Mapped[datetime] = mapped_column(DateTime, name="DTEXPORTACAO", nullable=True)
    dt_cancel: Mapped[datetime] = mapped_column(DateTime, name="DTCANCEL", nullable=True)
    num_orca: Mapped[int] = mapped_column(Integer, name="NUMORCA", nullable=True)
    num_caixa_fiscal: Mapped[int] = mapped_column(Integer, name="NUMCAIXAFISCAL", nullable=True)
    num_ec: Mapped[int] = mapped_column(Integer, name="NUMECF", nullable=True)
    gerar_dados_nf_paulista: Mapped[str] = mapped_column(String(1), name="GERARDADOSNFPAULISTA", nullable=True)
    versao_rotina: Mapped[str] = mapped_column(String(50), name="VERSAOROTINA", nullable=True)
    num_ccf: Mapped[int] = mapped_column(Integer, name="NUMCCF", nullable=True)
    num_regiao: Mapped[int] = mapped_column(Integer, name="NUMREGIAO", nullable=True)
    vl_mexiva: Mapped[float] = mapped_column(Numeric(10, 2), name="VLMEXIVA", nullable=True)
    frete_despacho: Mapped[float] = mapped_column(Numeric(10, 2), name="FRETEDESPACHO", nullable=True)
    cod_fornec_frete: Mapped[int] = mapped_column(Integer, name="CODFORNECFRETE", nullable=True)
    motorista_veiculo: Mapped[str] = mapped_column(String(50), name="MOTORISTAVEICULO", nullable=True)
    uf_veiculo: Mapped[str] = mapped_column(String(2), name="UFVEICULO", nullable=True)
    placa_veiculo: Mapped[str] = mapped_column(String(10), name="PLACAVEICULO", nullable=True)
    transportadora: Mapped[str] = mapped_column(String(50), name="TRANSPORTADORA", nullable=True)
    cgc_frete: Mapped[str] = mapped_column(String(20), name="CGFRETE", nullable=True)
    ie_frete: Mapped[str] = mapped_column(String(20), name="IEFRETE", nullable=True)
    uf_frete: Mapped[str] = mapped_column(String(2), name="UFFRETE", nullable=True)
    vl_frete: Mapped[float] = mapped_column(Numeric(10, 2), name="VLFRETE", nullable=True)
    num_ped_rca: Mapped[int] = mapped_column(Integer, name="NUMPEDRCA", nullable=True)
    chave_nfce: Mapped[str] = mapped_column(String(200), name="CHAVENFCE", nullable=True)
    qr_code_nfce: Mapped[str] = mapped_column(String(500), name="QRCODENFCE", nullable=True)
    protocolo_nfce: Mapped[str] = mapped_column(String(50), name="PROTOCOLONFCE", nullable=True)
    xml_nfce: Mapped[str] = mapped_column(String(4000), name="XMLNFCE", nullable=True)
    situacao_nfce: Mapped[str] = mapped_column(String(20), name="SITUACAONFCE", nullable=True)
    uid_registro: Mapped[str] = mapped_column(String(100), name="UIDREGISTRO", nullable=True)
    id_parceiro: Mapped[int] = mapped_column(Integer, name="IDPARCEIRO", nullable=True)

    def __repr__(self) -> str:
        return (
            f"PDV(num_ped={self.num_ped}, "
            f"data={self.data}, "
            f"cod_filial={self.cod_filial}, "
            f"vl_total={self.vl_total}, "
            f"num_cupom={self.num_cupom})"
        )


class PDVItem(Base):
    __tablename__ = "PDVITEM"
    
    id: Mapped[int] = mapped_column(Integer, Sequence('pdvitem_seq'), primary_key=True, name="ID")
    num_ped_ecf: Mapped[int] = mapped_column(Integer, name="NUMPEDECF", nullable=True)
    validated: Mapped[bool] = mapped_column(Boolean, name="VALIDATED", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, name="CREATEDAT", server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, name="UPDATEDAT", server_default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        return (
            f"PDVItem(num_ped_ecf={self.num_ped_ecf}, "
            f"validated={self.validated}, "
            f"created_at={self.created_at}, "
            f"updated_at={self.updated_at})"
        )

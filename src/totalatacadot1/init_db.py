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
                exportado="S",
                num_ped_ecf=11397,
                cod_func_cx=2,
                num_caixa=303,
                num_serie_equip="NotaFiscal",
                data=datetime(2025, 1, 7, 0, 0),
                cod_filial=3,
                cod_cli=1,
                cod_usur=300,
                cod_praca=11,
                cod_supervisor=3,
                cod_plpag=1,
                posicao="L",
                cond_venda=1,
                per_venda=100.0,
                num_cupom=10429,
                serie_ecf="X",
                cod_cob="D",
                cod_emitente=2,
                dt_entrega=datetime(2025, 1, 7, 0, 0),
                vl_atend=12.69,
                vl_total=12.69,
                vl_tabela=12.69,
                vl_desconto=0.0,
                tipo_venda="VV",
                vl_outras_despesas=0.0,
                num_itens=1,
                hora=19,
                minuto=58,
                prazo1=0.0,
                prazo2=0.0,
                prazo3=0.0,
                prazo_medio=0.0,
                num_vias_mapa_sep=1,
                operacao="N",
                vl_custo_real=9.5,
                vl_custo_fin=9.5,
                tot_peso=0.6,
                tot_volume=1.0,
                vl_custo_rep=6.76,
                vl_custo_cont=6.08,
                num_ped=None,
                num_car=None,
                num_transvenda=None,
                dt_fat=datetime(2025, 1, 7, 19, 59),
                hora_fat=None,
                minuto_fat=None,
                importado="N",
                posicao_retorno="PCAUX2075. 34.0.12.2",
                dt_exportacao=None,
                dt_cancel=None,
                num_orca=3,
                num_caixa_fiscal=None,
                num_ec=None,
                gerar_dados_nf_paulista=None,
                versao_rotina=None,
                num_ccf=None,
                num_regiao=None,
                vl_mexiva=0.77,
                frete_despacho=0.17,
                cod_fornec_frete=None,
                motorista_veiculo=None,
                uf_veiculo=None,
                placa_veiculo=None,
                transportadora=None,
                cgc_frete=None,
                ie_frete=None,
                uf_frete=None,
                vl_frete=12.69,
                num_ped_rca=None,
                chave_nfce="2.92501E+43",
                qr_code_nfce="http://nfe.sefaz.ba.gov.br/servicos/nfce/qrcode.aspx?p=29250105466724000300653030000104291328588764|2|1|1|6945FA2E6B1F1C1F236547A91911A817BB2A4CB6",
                protocolo_nfce="229250027519477",
                xml_nfce="VENDA DE MERC. ADQUIRIDA OU RECEBIDA DE TERCEIROS",
                situacao_nfce="1",
                uid_registro="000A0653-7FFAFBBF-BFEBFBFF",
                id_parceiro=300,
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

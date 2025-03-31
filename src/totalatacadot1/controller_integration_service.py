from dataclasses import dataclass
from datetime import datetime
import logging

from totalatacadot1.integration_service import (
    DiscountRequest,
    IntegrationService,
    ResponseReturn,
)

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Classes de modelo (DTOs)
@dataclass
class DiscountCreationDto:
    """DTO para criação de desconto."""

    purchase_value: float  # vltotal
    terminal_id: int  # numcaixa
    num_cupom: int  # numcupom
    discount_datetime: datetime
    fiscal_document: str  # CNPJ
    card_barcode: str = ""  # código que será digitado/scaneado no terminal

    # Validação do valor da compra
    def validate_purchase_value(self):
        if self.purchase_value <= 0:
            raise ValueError("Valor da compra deve ser maior que zero")

    # Validação do TerminalId
    def validate_terminal_id(self):
        if self.terminal_id <= 0:
            raise ValueError("TerminalId inválido")

    # Validação do código de barras do cartão
    def validate_card_barcode(self):
        if not self.card_barcode or self.card_barcode.strip() == "":
            raise ValueError("Cartão inválido")

    # Validação do documento fiscal
    def validate_fiscal_document(self):
        if not self.fiscal_document or self.fiscal_document.strip() == "":
            raise ValueError("Documento fiscal inválido")
        # if not validar_cnpj(self.fiscal_document):
        #     raise ValueError("Documento fiscal inválido (CNPJ inválido)")


# Função para validar CNPJ (equivalente ao método ValidarCNPJ do C#)
def validar_cnpj(cnpj: str) -> bool:
    cnpj = cnpj.strip().replace(".", "").replace("-", "").replace("/", "")
    if len(cnpj) != 14:
        return False

    # Cálculo dos dígitos verificadores
    multiplicador1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    multiplicador2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    temp_cnpj = cnpj[:12]
    soma = sum(int(temp_cnpj[i]) * multiplicador1[i] for i in range(12))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    temp_cnpj += str(digito1)
    soma = sum(int(temp_cnpj[i]) * multiplicador2[i] for i in range(13))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    return cnpj[-2:] == f"{digito1}{digito2}"


# Função principal para criar desconto
def create_discount(
    request: DiscountCreationDto, service: IntegrationService
) -> ResponseReturn:
    try:
        # Validar o DTO
        request.validate_purchase_value()
        request.validate_terminal_id()
        request.validate_card_barcode()
        request.validate_fiscal_document()

        # Criar a requisição para o serviço de integração
        discount_request = DiscountRequest(
            cmd_term_id=request.terminal_id,
            cmd_card_id=request.card_barcode,
            cmd_op_value=int(request.purchase_value * 100),  # Converter para centavos,
            cmd_op_seq_no=request.num_cupom,
            cmd_tmt=int(request.discount_datetime.timestamp()),
            cmd_seq_no=service.get_next_number(),
        )

        # Chamar o serviço de integração
        response = service.create_discount(discount_request)

        if response.Success:
            return response
        else:
            raise ValueError(response.Message)
    except ValueError as ex:
        logger.error(f"Erro de validação: {ex}")
        return ResponseReturn(Success=False, Message=str(ex))
    except Exception as ex:
        logger.error(f"Erro em CreateDiscount: {ex}")
        return ResponseReturn(Success=False, Message=f"Erro: {ex}")


def main():
    pass
    # Instância do serviço
    # service = IntegrationService("10.7.39.10", 3000)

    # date = "1/7/25 0:00"
    # hora_cupom = "19:58:47"
    # date_time_cupom = datetime.strptime()
    # # Criar uma requisição de exemplo
    # request = DiscountCreationDto(
    #     CardBarcode="1234567890123456", # input caixa
    #     TerminalId=303, # db
    #     PurchaseValue=100.50, # db
    #     num_cupom=10431, # db
    #     hora_cupom=1694593434, # db
    #     FiscalDocument="04558054000173",  # CNPJ válido
    # )

    # # Chamar a função para criar desconto
    # result = create_discount(request, service)

    # # Exibir o resultado
    # logger.info(f"Success: {result.Success}, Message: {result.Message}")


# Exemplo de uso
if __name__ == "__main__":
    main()

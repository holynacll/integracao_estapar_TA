from dataclasses import dataclass
from typing import Optional
import logging

from totalatacadot1.integration_service import DiscountRequest, IntegrationService, ResponseReturn

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Classes de modelo (DTOs)
@dataclass
class DiscountCreationDto:
    TerminalId: int
    CardBarcode: str
    PurchaseValue: float
    FiscalDocument: str

    # Validação do valor da compra
    def validate_purchase_value(self):
        if self.PurchaseValue <= 0:
            raise ValueError("Valor da compra deve ser maior que zero")

    # Validação do TerminalId
    def validate_terminal_id(self):
        if self.TerminalId <= 0:
            raise ValueError("TerminalId inválido")

    # Validação do código de barras do cartão
    def validate_card_barcode(self):
        if not self.CardBarcode or self.CardBarcode.strip() == "":
            raise ValueError("Cartão inválido")

    # Validação do documento fiscal
    def validate_fiscal_document(self):
        if not self.FiscalDocument or self.FiscalDocument.strip() == "":
            raise ValueError("Documento fiscal inválido")
        if not validar_cnpj(self.FiscalDocument):
            raise ValueError("Documento fiscal inválido (CNPJ inválido)")


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
def create_discount(request: DiscountCreationDto, service: IntegrationService) -> ResponseReturn:
    try:
        # Validar o DTO
        # request.validate_purchase_value()
        # request.validate_terminal_id()
        # request.validate_card_barcode()
        # request.validate_fiscal_document()

        # Converter o DTO para o modelo de requisição
        request_cnv = DiscountRequest(
            CmdTermId=request.TerminalId,
            CmdCardId=request.CardBarcode,
            CmdOpValue=int(request.PurchaseValue * 100),  # Converter para centavos
            CmdOpSeqNo=service.get_next_number(),
            CmdRUF_0=0xFFFFFFFF,
            CmdRUF_1=0xFFFFFFFF,
            CmdSaleType=0xFFFFFFFF,
            CmdOpDisplayLen=0,
            CmdCustDisplayLen=0,
            CmdPrinterLineLen=40,
            CmdSignature=request.FiscalDocument,
        )

        # Chamar o serviço de integração
        result = service.create_discount(request_cnv)

        if result.Success:
            return result
        else:
            raise ValueError(result.Message)
    except ValueError as ex:
        logger.error(f"Erro de validação: {ex}")
        return ResponseReturn(Success=False, Message=str(ex))
    except Exception as ex:
        logger.error(f"Erro em CreateDiscount: {ex}")
        return ResponseReturn(Success=False, Message=f"Erro: {ex}")


# Instância do serviço
service = IntegrationService("10.7.39.10", 3000)

# Exemplo de uso
if __name__ == "__main__":
    # Criar uma requisição de exemplo
    request = DiscountCreationDto(
        TerminalId=1,
        CardBarcode="1234567890123456",
        PurchaseValue=100.50,
        FiscalDocument="04558054000173",  # CNPJ válido
    )

    # Chamar a função para criar desconto
    result = create_discount(request, service)

    # Exibir o resultado
    print(f"Success: {result.Success}, Message: {result.Message}")

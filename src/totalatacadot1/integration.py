import socket
import struct
import time
import logging

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constantes
CMD_CONSULT = 0x0000000F  # Tipo de comando para consulta
CMD_VALIDATION = 0x00000010  # Tipo de comando para validação
RSP_CONSULT = 0x0001000F  # Tipo de resposta para consulta
RSP_VALIDATION = 0x00010010  # Tipo de resposta para validação

# Endereço IP e porta do Integration Service
INTEGRATION_SERVICE_IP = "10.7.39.10"
INTEGRATION_SERVICE_PORT = 3000

# Estrutura das mensagens
class DiscountRequest:
    def __init__(self, card_id, term_id, value):
        self.CmdType = CMD_VALIDATION  # Tipo de comando (validação)
        self.CmdTermId = term_id # ID do terminal PDV
        self.CmdOpValue = int(value * 100) # Valor da compra em centavos (R$ 100,00)
        self.CmdCardId = card_id # Código de barras do cartão
        self.CmdSignature = "04558054000173"  # CNPJ do estabelecimento
        self.CmdOpSeqNo = 45  # Número sequencial da operação
        self.CmdRUF_0 = 0xFFFFFFFF  # Reservado para uso futuro
        self.CmdRUF_1 = 0xFFFFFFFF  # Reservado para uso futuro
        self.CmdSaleType = 0xFFFFFFFF  # Tipo de venda (reservado)
        self.CmdOpDisplayLen = 0  # Número de caracteres do visor do operador
        self.CmdCustDisplayLen = 0  # Número de caracteres do visor do cliente
        self.CmdPrinterLineLen = 40  # Número de caracteres da linha de impressão

    def serialize(self):
        """Serializa a requisição em bytes, conforme o manual."""
        message = struct.pack(
            "<HHI15s16sII64sIIIIII",  # Novo formato corrigido
            0,  # cmdFiller (2 bytes)
            0x0000000F,  # cmdType (4 bytes, little-endian)
            int(time.time()),  # cmdTmt (4 bytes, little-endian)
            self.CmdSignature.encode().ljust(15, b'\x00'),  # cmdSignature (15 bytes, null-terminated)
            b"ESTAPAR".ljust(16, b'\x00'),  # cmdCompanySign (16 bytes, null-terminated)
            self.CmdTermId,  # cmdTermId (4 bytes, little-endian)
            self.CmdOpSeqNo,  # cmdSeqNo (4 bytes, little-endian)
            self.CmdCardId.encode().ljust(64, b'\x00'),  # cmdCardId (64 bytes, null-terminated)
            0,  # cmdOpValue (4 bytes, little-endian)
            0,  # cmdOpSeqNo (4 bytes, little-endian)
            0xFFFFFFFF,  # cmdRUF_0 (4 bytes, reservado)
            0xFFFFFFFF,  # cmdRUF_1 (4 bytes, reservado)
            0xFFFFFFFF,  # cmdSaleType (4 bytes, reservado)
            0   # cmdOpDisplayLen (4 bytes)
        )

        return message


# class DiscountResponse:
#     def __init__(self, data):
#         """Deserializa a resposta recebida do Integration Service."""
#         self.RspStatus = struct.unpack('<I', data[16:20])[0]  # Status da resposta
#         self.RspStatusTxt = self.get_status_text(self.RspStatus)  # Texto do status


class DiscountResponse:
    def __init__(self, data):
        """Deserializa a resposta recebida do Integration Service."""
        logger.info(f"Resposta completa: {data.hex()}")
        logger.info(f"Tamanho da resposta: {len(data)} bytes")

        # Extrai o campo rspStatus (bytes 16 a 20)
        self.RspStatus = struct.unpack('<I', data[16:20])[0]  # Status da resposta
        logger.info(f"Status da resposta: 0x{self.RspStatus:08X}")

        # Extrai o texto do status
        self.RspStatusTxt = self.get_status_text(self.RspStatus)

    @staticmethod
    def get_status_text(status):
        """Retorna o texto correspondente ao status."""
        status_messages = {
            0x00000000: "Cartão validado até DD/MM/AAAA - HH:MM",
            0x00000001: "Cartão não validado",
            0x00000002: "Cartão já validado",
            0x00000003: "Valor da compra insuficiente para validação",
            0x00000004: "Cartão inválido",
            0x00000005: "Comando inválido",
            0x00000006: "Operação inválida",
            0x00000007: "Terminal não cadastrado",
            0x00000008: "Tempo de desconto excedido",
        }
        return status_messages.get(status, f"Status desconhecido (0x{status:08X})")


def send_discount_request(request: DiscountRequest) -> DiscountResponse:
    """Envia a requisição para o Integration Service e recebe a resposta."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_client:
            tcp_client.connect((INTEGRATION_SERVICE_IP, INTEGRATION_SERVICE_PORT))
            logger.info("Conexão estabelecida com sucesso.")

            # Serializa a requisição
            message = request.serialize()
            logger.info(f"Enviando requisição: {message.hex()}")

            # Envia a requisição
            tcp_client.sendall(message)

            # Recebe a resposta
            response = tcp_client.recv(2048)
            logger.info(f"Resposta recebida: {response.hex()}")

            # Deserializa a resposta
            return DiscountResponse(response)
    except Exception as ex:
        logger.error(f"Erro na comunicação com o Integration Service: {ex}")
        return None


# Exemplo de uso
if __name__ == "__main__":
    # Cria uma requisição de desconto
    ticket_code = "9220428135318"
    NUMCAIXA = 303
    VLTOTAL = 12.69
    request = DiscountRequest(card_id=ticket_code, term_id=NUMCAIXA, value=VLTOTAL)

    # Envia a requisição e recebe a resposta
    response = send_discount_request(request)

    if response:
        print(f"Status: {response.RspStatusTxt}")
    else:
        print("Falha na comunicação com o Integration Service.")

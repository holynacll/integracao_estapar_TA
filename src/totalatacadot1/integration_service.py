from enum import Enum
from dataclasses import dataclass
import socket
import struct
import logging
import time
import traceback

# Configuração do logger
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class CommandType(Enum):
    CONSULT = 0x0000000F # 15
    VALIDATION = 0x00000010 # 16


@dataclass
class DiscountRequest:
    cmd_term_id: int # Numero do terminal do requisitante (NUM_CAIXA)
    cmd_card_id: str # Código de barras do cartão
    cmd_op_value: int # Valor da compra em centavos
    cmd_op_seq_no: int # Número sequencial do cupom fiscal
    cmd_tmt: int # timestamp da requisição
    msg_block_size: int = 0 # tamanho do bloco da mensagem
    cmd_filler: int = 0 # Reservado
    cmd_type: CommandType = CommandType.CONSULT
    cmd_signature: str = "04558054000173" # CNPJ da empresa (null-terminated)
    cmd_company_sign: bytes = b"ESTAPAR" # assinatura da aplicação (null-terminated)
    cmd_seq_no: int = 1  # número sequencial da operação
    cmd_ruf_0: int = 0xFFFFFFFF # Reservado
    cmd_ruf_1: int = 0xFFFFFFFF # Reservado
    cmd_sale_type: int = 0xFFFFFFFF # Tipo de venda (reservado)
    cmd_op_display_len: int = 0 # Número de caracteres do visor do operador
    
    
    def serialize(self):
        """Serializa a requisição em bytes, conforme o manual."""
        print(f"cmd_filler: {self.cmd_filler} ({type(self.cmd_filler)})")
        print(f"cmd_type: {self.cmd_type.value} ({type(self.cmd_type.value)})")
        print(f"cmd_tmt: {self.cmd_tmt} ({type(self.cmd_tmt)})")
        print(f"cmd_signature: {self.cmd_signature} ({type(self.cmd_signature)})")
        print(f"cmd_company_sign: {self.cmd_company_sign} ({type(self.cmd_company_sign)})")
        print(f"cmd_seq_no: {self.cmd_seq_no} ({type(self.cmd_seq_no)})")
        print(f"cmd_term_id: {self.cmd_term_id} ({type(self.cmd_term_id)})")
        print(f"cmd_card_id: {self.cmd_card_id} ({type(self.cmd_card_id)})")
        print(f"cmd_op_value: {self.cmd_op_value} ({type(self.cmd_op_value)})")
        print(f"cmd_op_seq_no: {self.cmd_op_seq_no} ({type(self.cmd_op_seq_no)})")
        print(f"cmd_ruf_0: {self.cmd_ruf_0} ({type(self.cmd_ruf_0)})")
        print(f"cmd_ruf_1: {self.cmd_ruf_1} ({type(self.cmd_ruf_1)})")
        print(f"cmd_sale_type: {self.cmd_sale_type} ({type(self.cmd_sale_type)})")
        print(f"cmd_op_display_len: {self.cmd_op_display_len} ({type(self.cmd_op_display_len)})")
        message = struct.pack(
            "<HHI15s16sII64sIIIIII",  # Novo formato corrigido
            self.cmd_filler,  # cmdFiller (2 bytes)
            self.cmd_type.value,  # cmdType (4 bytes, little-endian)
            self.cmd_tmt,  # cmdTmt (4 bytes, little-endian)
            self.cmd_signature.encode().ljust(15, b'\x00'),  # cmdSignature (15 bytes, null-terminated)
            self.cmd_company_sign.ljust(16, b'\x00'),  # cmdCompanySign (16 bytes, null-terminated)
            self.cmd_seq_no,  # cmdSeqNo (4 bytes, little-endian)
            self.cmd_term_id,  # cmdTermId (4 bytes, little-endian)
            self.cmd_card_id.encode().ljust(64, b'\x00'),  # cmdCardId (64 bytes, null-terminated)
            self.cmd_op_value,  # cmdOpValue (4 bytes, little-endian)
            self.cmd_op_seq_no,  # cmdOpSeqNo (4 bytes, little-endian)
            self.cmd_ruf_0,  # cmdRUF_0 (4 bytes, reservado)
            self.cmd_ruf_1,  # cmdRUF_1 (4 bytes, reservado)
            self.cmd_sale_type,  # cmdSaleType (4 bytes, reservado)
            self.cmd_op_display_len   # cmdOpDisplayLen (4 bytes)
        )
        print(f"message: {message} ({type(message)})")
        # Adicionando tamanho da mensagem no início
        message = struct.pack("<H", len(message)) + message
        return message

@dataclass
class ResponseReturn:
    Success: bool = False
    Message: str = ""

class IntegrationService:
    def __init__(self, ip, port):
        self.integration_service_ip = ip
        self.integration_service_port = port
        self.current_number = 0
    
    def get_next_number(self) -> int:
        self.current_number += 1
        return self.current_number

    def create_discount(self, request: DiscountRequest) -> ResponseReturn:
        response_return = ResponseReturn()

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_client:
                tcp_client.connect((self.integration_service_ip, self.integration_service_port))
                logger.warning(f"Conexão estabelecida com sucesso: {self.integration_service_ip}:{self.integration_service_port}")

                # request.CmdSeqNo = 45
                message = request.serialize()
                formatted_output = self.format_bytes_to_hex_string(message)
                logger.warning(f"Enviando: \n{formatted_output}")
                tcp_client.sendall(message)

                response = self.read_response(tcp_client)
                if response:
                    if "Cartao invalido" in response:
                        response_return.Success = False
                        response_return.Message = "invalid card number"
                        logger.warning("Mensagem recebida -->>> Cartão inválido")
                    elif "Cartao validado ate" in response:
                        response_return.Success = True
                        response_return.Message = "card validated until"
                        logger.warning("Mensagem recebida -->>> Cartao validado ate")
                    elif "Cartao ja validado" in response:
                        response_return.Success = False
                        response_return.Message = "card already validated"
                        logger.warning("Mensagem recebida -->>> Cartao ja validado")
                    elif "Valor de compra insuficiente para validacao" in response:
                        response_return.Success = False
                        response_return.Message = "insufficient purchase value for validation"
                        logger.warning("Mensagem recebida -->>> Valor de compra insuficiente para validacao")
                    elif "Comando invalido" in response:
                        response_return.Success = False
                        response_return.Message = "invalid command"
                        logger.warning("Mensagem recebida -->>> Comando invalido")
                    elif "Operacao invalida" in response:
                        response_return.Success = False
                        response_return.Message = "invalid operation"
                        logger.warning("Mensagem recebida -->>> Operacao invalida")
                    elif "Terminal nao cadastrado" in response:
                        response_return.Success = False
                        response_return.Message = "terminal not registered"
                        logger.warning("Mensagem recebida -->>> Terminal nao cadastrado")
                    elif "Tempo de desconto excedido" in response:
                        response_return.Success = False
                        response_return.Message = "discount time exceeded"
                        logger.warning("Mensagem recebida -->>> Tempo de desconto excedido")
                    elif "Tipo de cartao invalido" in response:
                        response_return.Success = False
                        response_return.Message = "invalid card type"
                        logger.warning("Mensagem recebida -->>> Tipo de cartao invalido")
                    else:
                        response_return.Success = True
                        response_return.Message = response
                        logger.warning(f"Mensagem recebida -->>> {response}")
                else:
                    response_return.Success = False
                    response_return.Message = "Recebida uma resposta vazia do servidor"
                    logger.warning("Recebida uma resposta vazia do servidor")
        except Exception as ex:
            logger.error(f"Erro em CreateDiscount: {ex} - {traceback.format_exc()}")
            response_return.Success = False
            response_return.Message = f"Erro: {ex}"

        return response_return


    def read_response(self, tcp_client):
        response = b''
        while True:
            data = tcp_client.recv(2048)
            if not data:
                break
            response += data
        return response.decode('ascii').rstrip('\x00')

    def format_bytes_to_hex_string(self, bytes_data):
        hex_string = ""
        for i in range(0, len(bytes_data), 16):
            hex_string += f"{i:04x}   "
            for j in range(i, min(i + 16, len(bytes_data))):
                hex_string += f"{bytes_data[j]:02x} "
            hex_string += "  "
            for j in range(i, min(i + 16, len(bytes_data))):
                char = chr(bytes_data[j])
                hex_string += char if char.isprintable() else '.'
            hex_string += "\n"
        return hex_string

# Exemplo de uso
if __name__ == "__main__":
    service = IntegrationService("10.7.39.10", 3000)
    NUMCAIXA = 303
    VLTOTAL = 1269
    ticket_code = "9220428135318"
    request = DiscountRequest(
        cmd_term_id=NUMCAIXA,
        cmd_card_id=ticket_code,
        cmd_op_value=VLTOTAL,
    )
    response = service.create_discount(request)
    print(f"Success: {response.Success}, Message: {response.Message}")

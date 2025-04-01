import socket
import struct
from typing import Optional
from loguru import logger
import traceback

from totalatacadot1.enums import ResponseStatus
from totalatacadot1.schemas import DiscountRequest, DiscountResponse, ResponseReturn


class EstaparIntegrationService:
    """Serviço de integração com a API da Estapar"""
    
    DEFAULT_TIMEOUT = 10  # segundos
    BUFFER_SIZE = 4096
    
    def __init__(self, ip: str, port: int):
        self.server_ip = ip
        self.server_port = port
        self.sequence_number = 0
        self._validate_connection_params()

    def _validate_connection_params(self):
        """Valida os parâmetros de conexão"""
        if not self.server_ip or not isinstance(self.server_port, int):
            raise ValueError("IP e porta do servidor devem ser configurados")

    def get_next_number(self) -> int:
        """Gera o próximo número de sequência"""
        self.sequence_number += 1
        return self.sequence_number
    def create_discount(self, request: DiscountRequest) -> ResponseReturn:
        """
        Envia uma requisição de desconto para a API da Estapar
        e processa a resposta
        """
        logger.info(f"Enviando requisição de desconto para {self.server_ip}:{self.server_port}")
        logger.debug(f"Requisição: {request}")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.DEFAULT_TIMEOUT)
                
                # Conecta ao servidor
                self._connect(sock)
                
                # Serializa e envia a mensagem
                message = request.serialize()
                self._log_message(message, "Enviando requisição")
                sock.sendall(message)
                
                # Processa a resposta
                response = self._read_response(sock)
                if not response:
                    return ResponseReturn(False, "Sem resposta do servidor")
                
                return self._parse_response(response)
                
        except socket.timeout:
            error_msg = "Timeout na comunicação com o servidor"
            logger.error(error_msg)
            return ResponseReturn(False, error_msg)
            
        except ConnectionRefusedError:
            error_msg = "Conexão recusada pelo servidor"
            logger.error(error_msg)
            return ResponseReturn(False, error_msg)
            
        except Exception as ex:
            error_msg = f"Erro inesperado: {str(ex)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return ResponseReturn(False, error_msg)

    def _connect(self, sock: socket.socket):
        """Estabelece conexão com o servidor"""
        logger.info(f"Conectando a {self.server_ip}:{self.server_port}")
        sock.connect((self.server_ip, self.server_port))
        logger.success("Conexão estabelecida com sucesso")

    def _read_response(self, sock: socket.socket) -> Optional[bytes]:
        """Lê a resposta do servidor"""
        try:
            # Primeiro lê o tamanho da mensagem (2 bytes)
            size_data = sock.recv(2)
            if len(size_data) < 2:
                return None
                
            msg_size = struct.unpack("<H", size_data)[0]
            
            # Lê o restante da mensagem
            received = bytearray()
            while len(received) < msg_size:
                chunk = sock.recv(min(self.BUFFER_SIZE, msg_size - len(received)))
                if not chunk:
                    break
                received.extend(chunk)
                
            return bytes(received)
            
        except socket.timeout:
            logger.error("Timeout ao ler resposta do servidor")
            return None

    def _parse_response(self, response_data: bytes) -> ResponseReturn:
        """Interpreta a resposta do servidor"""
        try:
            # Decodifica a resposta
            response_text = response_data.decode('ascii').rstrip('\x00')
            logger.info(f"Resposta recebida: {response_text}")
            
            if not response_text:
                return ResponseReturn(False, "Resposta vazia do servidor")
            
            # Parse do status (simplificado - ajustar conforme protocolo real)
            if "Cartao validado ate" in response_text:
                return ResponseReturn(
                    True,
                    "Cartão validado com sucesso",
                    DiscountResponse(ResponseStatus.VALIDATED, response_text)
                )
            elif "Cartao invalido" in response_text:
                return ResponseReturn(
                    False,
                    "Cartão inválido",
                    DiscountResponse(ResponseStatus.INVALID_CARD, response_text)
                )
            elif "Cartao ja validado" in response_text:
                return ResponseReturn(
                    False,
                    "Cartão já validado",
                    DiscountResponse(ResponseStatus.ALREADY_VALIDATED, response_text)
                )
            elif "Valor de compra insuficiente para validacao" in response_text:
                return ResponseReturn(
                    False,
                    "Valor de compra insuficiente para validação",
                    DiscountResponse(ResponseStatus.INSUFFICIENT_VALUE, response_text)
                )
            elif "Comando invalido" in response_text:
                return ResponseReturn(
                    False,
                    "Comando inválido",
                    DiscountResponse(ResponseStatus.INVALID_COMMAND, response_text)
                )
            elif "Operacao invalida" in response_text:
                return ResponseReturn(
                    False,
                    "Operação inválida",
                    DiscountResponse(ResponseStatus.INVALID_OPERATION, response_text)
                )
            elif "Terminal nao cadastrado" in response_text:
                return ResponseReturn(
                    False,
                    "Terminal não cadastrado",
                    DiscountResponse(ResponseStatus.UNREGISTERED_TERMINAL, response_text)
                )
            elif "Tempo de desconto excedido" in response_text:
                return ResponseReturn(
                    False,
                    "Tempo de desconto excedido",
                    DiscountResponse(ResponseStatus.DISCOUNT_TIME_EXCEEDED, response_text)
                )
            elif "Tipo de cartao invalido" in response_text:
                return ResponseReturn(
                    False,
                    "Tipo de cartão inválido",
                    DiscountResponse(ResponseStatus.INVALID_CARD, response_text)
                )
            return ResponseReturn(True, response_text)
            
        except Exception as ex:
            error_msg = f"Erro ao processar resposta: {str(ex)}"
            logger.error(error_msg)
            return ResponseReturn(False, error_msg)

    def _log_message(self, message: bytes, title: str):
        """Loga mensagens em formato hexadecimal para debug"""
        hex_dump = self._format_hex_dump(message)
        logger.debug(f"{title}:\n{hex_dump}")

    def _format_hex_dump(self, data: bytes) -> str:
        """Formata dados binários para exibição hexadecimal"""
        lines = []
        for i in range(0, len(data), 16):
            chunk = data[i:i+16]
            hex_part = ' '.join(f"{b:02x}" for b in chunk)
            ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            lines.append(f"{i:04x}   {hex_part.ljust(47)}  {ascii_part}")
        return '\n'.join(lines)

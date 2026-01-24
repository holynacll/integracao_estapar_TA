# integration.py

import socket
import struct
from typing import Optional, Tuple
from loguru import logger
import traceback

# from totalatacadot1.enums import ResponseStatus # Assuming VehicleType enum exists
from totalatacadot1.enums import ResponseStatus, VehicleType
from totalatacadot1.schemas import DiscountRequest, DiscountResponse, ResponseReturn


# Helper function to decode bytes safely
def safe_decode(byte_string: bytes, encoding="latin-1") -> str:
    """Decodes bytes, removes null termination, and handles errors."""
    try:
        # Remove data after the first null byte and decode
        return byte_string.split(b"\x00", 1)[0].decode(encoding)
    except Exception as e:
        logger.warning(
            f"Failed to decode bytes with {encoding}: {e}. Bytes: {byte_string.hex()}"
        )
        # Fallback or return placeholder
        return f"[Decode Error: {encoding}]"


class EstaparIntegrationService:
    """Serviço de integração com a API da Estapar"""

    CONNECTION_TIMEOUT = 3 # seconds
    DEFAULT_TIMEOUT = 10  # segundos
    BUFFER_SIZE = 4096

    # Header: 2(Filler)+4(Type)+15(Sig)+16(CompSign)+4(Tmt)+4(SeqNo) = 45 bytes
    # Data:   4(TermId)+64(CardId)+4(Status)+128(OpDisp)+128(CustDisp)+128(PrintLine)+4(EntryTS)+2(VehType)+2(RUF1)+4(RUF2) = 566 bytes
    # Total Expected Payload = 45 + 566 = 611 bytes
    EXPECTED_RESPONSE_PAYLOAD_SIZE = 611
    RESPONSE_FORMAT = (
        "<"  # Little-endian
        # rspHeader (45 bytes)
        "H"  # rspFiller (2 bytes, unsigned short) - Ignored
        "I"  # rspType (4 bytes, unsigned int)
        "15s"  # rspSignature (15 bytes, string)
        "16s"  # rspCompanySign (16 bytes, string)
        "I"  # rspTmt (4 bytes, unsigned int) - Timestamp
        "I"  # rspSeqNo (4 bytes, unsigned int) - Sequence number matched
        # rspData (566 bytes)
        "I"  # rspTermld (4 bytes, unsigned int)
        "64s"  # rspCardld (64 bytes, string)
        "I"  # rspStatus (4 bytes, unsigned int) <-- *** IMPORTANT ***
        "128s"  # rspOpDisplayTxt (128 bytes, string)
        "128s"  # rspCustDisplayTxt (128 bytes, string)
        "128s"  # rspPrinterLineTxt (128 bytes, string)
        "I"  # rspEntryTimeStamp (4 bytes, unsigned int)
        "H"  # rspVehicleType (2 bytes, unsigned short)
        "H"  # rspRUF_1 (2 bytes, unsigned short) - Reserved
        "I"  # rspRUF_2 (4 bytes, unsigned int) - Reserved
    )

    # Mapeamento baseado na documentação (pág 8)
    _STATUS_MAPPING = {
        0x00000000: (ResponseStatus.VALIDATED, "Cartão validado com sucesso", True),
        0x00000001: (ResponseStatus.INVALID_CARD, "Cartão não validado", False),
        0x00000002: (ResponseStatus.ALREADY_VALIDATED, "Cartão já validado", False),
        0x00000003: (ResponseStatus.INSUFFICIENT_VALUE, "Valor da compra insuficiente para validação", False),
        0x00000004: (ResponseStatus.INVALID_CARD, "Cartão inválido", False),
        0x00000005: (ResponseStatus.INVALID_COMMAND, "Comando inválido", False),
        0x00000006: (ResponseStatus.INVALID_OPERATION, "Operação inválida", False),
        0x00000007: (ResponseStatus.UNREGISTERED_TERMINAL, "Terminal não cadastrado", False),
        0x00000008: (ResponseStatus.DISCOUNT_TIME_EXCEEDED, "Tempo de desconto excedido", False),
    }

    def __init__(self, ip: str, port: int):
        self.server_ip = ip
        self.server_port = port
        # Sequence number management should ideally persist across connections
        # if the protocol requires it per terminal session, not per socket connection.
        # For simplicity here, we reset on init. A more robust implementation
        # might need external state management.
        self.sequence_number = 0
        self._validate_connection_params()

    def _validate_connection_params(self):
        """Valida os parâmetros de conexão"""
        if not self.server_ip or not isinstance(self.server_port, int):
            raise ValueError("IP e porta do servidor devem ser configurados")

    def _get_next_sequence_number(self) -> int:
        """Gera o próximo número de sequência para uma nova requisição."""
        # Note: Behavior might depend on whether sequence resets per connection or per session.
        # Assuming it increments per request within this service instance.
        self.sequence_number += 1
        return self.sequence_number

    def create_discount(self, request_data: DiscountRequest) -> ResponseReturn:
        """
        Envia uma requisição de desconto para a API da Estapar
        e processa a resposta
        """
        # Assign the next sequence number to the request before serializing
        request_data.cmd_seq_no = self._get_next_sequence_number()

        logger.info(
            f"Enviando requisição de desconto para {self.server_ip}:{self.server_port} (Seq: {request_data.cmd_seq_no})"
        )
        logger.debug(f"Requisição: {request_data}")  # repr should be fine

        sock = None  # Define sock outside try for finally block
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            timeout = self.CONNECTION_TIMEOUT
            sock.settimeout(timeout)

            # Conecta ao servidor
            self._connect(sock)
            logger.debug(f"Conectado ao servidor {self.server_ip}:{self.server_port}")

            # Serializa e envia a mensagem
            message = request_data.serialize()
            self._log_message(message, "Enviando requisição")
            timeout = self.DEFAULT_TIMEOUT
            sock.settimeout(timeout) # Set timeout for sending
            sock.sendall(message)

            # Lê e processa a resposta completa (header + data)
            response_payload = self._read_response_payload(sock)
            if response_payload is None:
                # Error already logged in _read_response_payload
                return ResponseReturn(
                    False,
                    "Não foi possível ler a resposta completa do servidor (timeout ou erro)",
                )

            # Log the raw response payload before parsing
            self._log_message(response_payload, "Payload da resposta recebida")

            return self._parse_response(response_payload, request_data.cmd_seq_no)

        except socket.timeout:
            error_msg = f"Timeout na comunicação com o servidor."
            logger.error(error_msg)
            return ResponseReturn(False, error_msg)

        except ConnectionRefusedError:
            error_msg = (
                "Conexão recusada pelo servidor."
            )
            logger.error(error_msg)
            return ResponseReturn(False, error_msg)

        except socket.gaierror:  # getaddrinfo error (DNS lookup failure)
            error_msg = (
                "Não foi possível resolver o endereço do servidor"
            )
            logger.error(error_msg)
            return ResponseReturn(False, error_msg)

        except Exception as ex:
            error_msg = f"Erro inesperado durante a integração: {str(ex)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return ResponseReturn(False, error_msg)
        finally:
            if sock:
                try:
                    sock.close()
                    logger.debug("Socket fechado.")
                except Exception as e:
                    logger.warning(f"Erro ao fechar o socket: {e}")

    def _connect(self, sock: socket.socket):
        """Estabelece conexão com o servidor"""
        logger.info(f"Conectando a {self.server_ip}:{self.server_port}")
        sock.connect((self.server_ip, self.server_port))
        logger.success("Conexão estabelecida com sucesso")

    def _read_response_payload(self, sock: socket.socket) -> Optional[bytes]:
        """Lê o payload completo (rspHeader + rspData) da resposta do servidor."""
        try:
            # 1. Ler os primeiros 2 bytes (msgBlockSize)
            size_data = sock.recv(2)
            if not size_data or len(size_data) < 2:
                logger.error(
                    "Não foi possível ler o tamanho da mensagem (conexão fechada ou vazia)."
                )
                return None
            msg_payload_size = struct.unpack("<H", size_data)[0]
            logger.debug(
                f"Tamanho do payload da resposta esperado (msgBlockSize): {msg_payload_size} bytes."
            )

            # Validação básica do tamanho esperado (sanity check)
            if msg_payload_size == 0:
                logger.warning("Servidor respondeu com tamanho de payload zero.")
                return b""  # Return empty bytes for zero size
            if (
                msg_payload_size > self.BUFFER_SIZE * 10
            ):  # Arbitrary limit to prevent huge allocations
                logger.error(
                    f"Tamanho do payload da resposta ({msg_payload_size}) excede limite razoável. Abortando leitura."
                )
                return None
            # Specific check against protocol definition
            if msg_payload_size != self.EXPECTED_RESPONSE_PAYLOAD_SIZE:
                logger.warning(
                    f"Tamanho do payload recebido ({msg_payload_size}) difere do esperado pelo protocolo ({self.EXPECTED_RESPONSE_PAYLOAD_SIZE}). Continuando, mas pode indicar problema."
                )

            # 2. Ler o restante da mensagem (o payload real: rspHeader + rspData)
            received_payload = bytearray()
            bytes_to_read = msg_payload_size
            while len(received_payload) < bytes_to_read:
                remaining = bytes_to_read - len(received_payload)
                chunk = sock.recv(min(self.BUFFER_SIZE, remaining))
                if not chunk:
                    logger.error(
                        f"Conexão fechada inesperadamente ao ler payload. Recebido {len(received_payload)} de {bytes_to_read} bytes."
                    )
                    return None  # Connection closed before full message received
                received_payload.extend(chunk)

            if len(received_payload) != bytes_to_read:
                logger.error(
                    f"Inconsistência na leitura. Esperado {bytes_to_read} bytes, recebido {len(received_payload)}."
                )
                return (
                    None  # Should not happen with the loop logic, but defensive check
                )

            logger.debug(
                f"Payload completo da resposta lido ({len(received_payload)} bytes)."
            )
            return bytes(received_payload)

        except socket.timeout:
            logger.error(
                "Timeout ao ler resposta do servidor."
            )
            return None
        except struct.error as e:
            logger.error(f"Erro de struct ao desempacotar tamanho da mensagem: {e}")
            return None
        except Exception as e:
            logger.error(
                f"Erro inesperado ao ler resposta: {e}\n{traceback.format_exc()}"
            )
            return None

    def _parse_response(
        self, response_payload: bytes, expected_seq_no: int
    ) -> ResponseReturn:
        """Interpreta o payload da resposta binária do servidor."""
        logger.debug(f"Iniciando parse do payload de {len(response_payload)} bytes.")

        # 1. Validar o tamanho do payload recebido contra o formato esperado
        try:
            expected_size = struct.calcsize(self.RESPONSE_FORMAT)
            if len(response_payload) != expected_size:
                logger.error(
                    f"Tamanho incorreto do payload da resposta! Recebido: {len(response_payload)}, Esperado: {expected_size}. Parse abortado."
                )
                self._log_message(
                    response_payload, "Payload da resposta com tamanho incorreto"
                )
                return ResponseReturn(
                    False,
                    f"Erro de protocolo: Tamanho da resposta inválido ({len(response_payload)} bytes)",
                )

            # 2. Desempacotar a resposta usando o formato definido
            unpacked_data = struct.unpack(self.RESPONSE_FORMAT, response_payload)

        except struct.error as e:
            error_msg = f"Erro ao desempacotar resposta binária: {e}. Payload recebido pode estar malformado."
            logger.error(error_msg)
            self._log_message(
                response_payload, "Payload da resposta que causou erro de struct"
            )
            return ResponseReturn(False, error_msg)

        # 3. Mapear os dados desempacotados para variáveis nomeadas
        try:
            (
                rsp_type, rsp_signature_b, rsp_company_sign_b, rsp_tmt, rsp_seq_no,
                rsp_term_id, rsp_card_id_b, rsp_status_code,
                rsp_op_display_txt_b, rsp_cust_display_txt_b, rsp_printer_line_txt_b,
                rsp_entry_timestamp, rsp_vehicle_type_code, _, _
            ) = (
                unpacked_data[1], unpacked_data[2], unpacked_data[3], unpacked_data[4], unpacked_data[5],
                unpacked_data[6], unpacked_data[7], unpacked_data[8],
                unpacked_data[9], unpacked_data[10], unpacked_data[11],
                unpacked_data[12], unpacked_data[13], unpacked_data[14], unpacked_data[15]
            )

            # 4. Decodificar campos de string (bytes -> str) com segurança
            rsp_printer_line_txt = safe_decode(rsp_printer_line_txt_b)

            # 5. Logar os valores parseados para depuração
            logger.debug(
                f"Parse da Resposta - Status Code: {rsp_status_code} (0x{rsp_status_code:08X})"
            )

            # 6. Validar número de sequência
            if rsp_seq_no != expected_seq_no:
                logger.warning(
                    f"Número de sequência da resposta ({rsp_seq_no}) não corresponde ao esperado ({expected_seq_no})!"
                )

            # 7. Mapear rsp_status_code para ResponseStatus enum e mensagem
            success = False
            message = f"Status desconhecido: {rsp_status_code}"
            response_status_enum = ResponseStatus.UNKNOWN

            if rsp_status_code in self._STATUS_MAPPING:
                response_status_enum, message, success = self._STATUS_MAPPING[rsp_status_code]
            
            # Tratar caso especial de código 0x00000007 com mensagem específica
            if rsp_status_code == 0x00000007 and "Tipo de cartao invalido" in rsp_printer_line_txt:
                response_status_enum = ResponseStatus.INVALID_CARD_TYPE
                message = "Tipo de cartão inválido"
                success = False

            # 8. Mapear vehicle type code
            vehicle_type_str = None
            if rsp_vehicle_type_code == 0x0001:
                vehicle_type_str = VehicleType.MOTO.value
            elif rsp_vehicle_type_code == 0x0002:
                vehicle_type_str = VehicleType.CARRO.value

            # 9. Construir o objeto DiscountResponse
            discount_response = DiscountResponse(
                status=response_status_enum,
                message=rsp_printer_line_txt or message,
                entry_timestamp=rsp_entry_timestamp if rsp_entry_timestamp != 0 else None,
                vehicle_type=vehicle_type_str,
            )

            # 10. Retornar
            logger.info(
                f"Resposta processada - Sucesso: {success}, Status: {response_status_enum.name}, Mensagem: '{discount_response.message}'"
            )
            return ResponseReturn(
                success=success, message=discount_response.message, data=discount_response
            )

        except Exception as ex:
            error_msg = f"Erro inesperado durante o parse da resposta: {str(ex)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            self._log_message(
                response_payload,
                "Payload da resposta que causou erro de parse inesperado",
            )
            return ResponseReturn(False, error_msg)

    def _log_message(self, message: bytes, title: str):
        """Loga mensagens em formato hexadecimal para debug"""
        # Limitar o tamanho logado para não poluir muito se a msg for enorme
        MAX_LOG_BYTES = 256
        log_limit_info = ""
        if len(message) > MAX_LOG_BYTES:
            log_limit_info = f" (primeiros {MAX_LOG_BYTES} bytes)"
            message = message[:MAX_LOG_BYTES]

        hex_dump = self._format_hex_dump(message)
        logger.debug(f"{title}{log_limit_info}:\n{hex_dump}")

    def _format_hex_dump(self, data: bytes) -> str:
        """Formata dados binários para exibição hexadecimal"""
        lines = []
        for i in range(0, len(data), 16):
            chunk = data[i : i + 16]
            hex_part = " ".join(f"{b:02x}" for b in chunk)
            # Usar '.' para bytes não imprimíveis ou fora do range ASCII básico comum
            ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            lines.append(f"{i:04x}   {hex_part.ljust(47)}  {ascii_part}")
        return "\n".join(lines)

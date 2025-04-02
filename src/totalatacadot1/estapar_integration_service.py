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
def safe_decode(byte_string: bytes, encoding='latin-1') -> str:
    """Decodes bytes, removes null termination, and handles errors."""
    try:
        # Remove data after the first null byte and decode
        return byte_string.split(b'\x00', 1)[0].decode(encoding)
    except Exception as e:
        logger.warning(f"Failed to decode bytes with {encoding}: {e}. Bytes: {byte_string.hex()}")
        # Fallback or return placeholder
        return f"[Decode Error: {encoding}]"

class EstaparIntegrationService:
    """Serviço de integração com a API da Estapar"""

    DEFAULT_TIMEOUT = 10  # segundos
    BUFFER_SIZE = 4096

    # Header: 2(Filler)+4(Type)+15(Sig)+16(CompSign)+4(Tmt)+4(SeqNo) = 45 bytes
    # Data:   4(TermId)+64(CardId)+4(Status)+128(OpDisp)+128(CustDisp)+128(PrintLine)+4(EntryTS)+2(VehType)+2(RUF1)+4(RUF2) = 566 bytes
    # Total Expected Payload = 45 + 566 = 611 bytes
    EXPECTED_RESPONSE_PAYLOAD_SIZE = 611
    RESPONSE_FORMAT = (
        "<"  # Little-endian
        # rspHeader (45 bytes)
        "H"    # rspFiller (2 bytes, unsigned short) - Ignored
        "I"    # rspType (4 bytes, unsigned int)
        "15s"  # rspSignature (15 bytes, string)
        "16s"  # rspCompanySign (16 bytes, string)
        "I"    # rspTmt (4 bytes, unsigned int) - Timestamp
        "I"    # rspSeqNo (4 bytes, unsigned int) - Sequence number matched
        # rspData (566 bytes)
        "I"    # rspTermld (4 bytes, unsigned int)
        "64s"  # rspCardld (64 bytes, string)
        "I"    # rspStatus (4 bytes, unsigned int) <-- *** IMPORTANT ***
        "128s" # rspOpDisplayTxt (128 bytes, string)
        "128s" # rspCustDisplayTxt (128 bytes, string)
        "128s" # rspPrinterLineTxt (128 bytes, string)
        "I"    # rspEntryTimeStamp (4 bytes, unsigned int)
        "H"    # rspVehicleType (2 bytes, unsigned short)
        "H"    # rspRUF_1 (2 bytes, unsigned short) - Reserved
        "I"     # rspRUF_2 (4 bytes, unsigned int) - Reserved
    )


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

        logger.info(f"Enviando requisição de desconto para {self.server_ip}:{self.server_port} (Seq: {request_data.cmd_seq_no})")
        logger.debug(f"Requisição: {request_data}") # repr should be fine

        sock = None # Define sock outside try for finally block
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.DEFAULT_TIMEOUT)

            # Conecta ao servidor
            self._connect(sock)

            # Serializa e envia a mensagem
            message = request_data.serialize()
            self._log_message(message, "Enviando requisição")
            sock.sendall(message)

            # Lê e processa a resposta completa (header + data)
            response_payload = self._read_response_payload(sock)
            if response_payload is None:
                # Error already logged in _read_response_payload
                return ResponseReturn(False, "Não foi possível ler a resposta completa do servidor (timeout ou erro)")

            # Log the raw response payload before parsing
            self._log_message(response_payload, "Payload da resposta recebida")

            return self._parse_response(response_payload, request_data.cmd_seq_no)

        except socket.timeout:
            error_msg = f"Timeout ({self.DEFAULT_TIMEOUT}s) na comunicação com o servidor {self.server_ip}:{self.server_port}"
            logger.error(error_msg)
            return ResponseReturn(False, error_msg)

        except ConnectionRefusedError:
            error_msg = f"Conexão recusada pelo servidor {self.server_ip}:{self.server_port}"
            logger.error(error_msg)
            return ResponseReturn(False, error_msg)

        except socket.gaierror: # getaddrinfo error (DNS lookup failure)
             error_msg = f"Não foi possível resolver o endereço do servidor: {self.server_ip}"
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
                logger.error("Não foi possível ler o tamanho da mensagem (conexão fechada ou vazia).")
                return None
            msg_payload_size = struct.unpack("<H", size_data)[0]
            logger.debug(f"Tamanho do payload da resposta esperado (msgBlockSize): {msg_payload_size} bytes.")

            # Validação básica do tamanho esperado (sanity check)
            if msg_payload_size == 0:
                 logger.warning("Servidor respondeu com tamanho de payload zero.")
                 return b'' # Return empty bytes for zero size
            if msg_payload_size > self.BUFFER_SIZE * 10: # Arbitrary limit to prevent huge allocations
                 logger.error(f"Tamanho do payload da resposta ({msg_payload_size}) excede limite razoável. Abortando leitura.")
                 return None
            # Specific check against protocol definition
            if msg_payload_size != self.EXPECTED_RESPONSE_PAYLOAD_SIZE:
                 logger.warning(f"Tamanho do payload recebido ({msg_payload_size}) difere do esperado pelo protocolo ({self.EXPECTED_RESPONSE_PAYLOAD_SIZE}). Continuando, mas pode indicar problema.")


            # 2. Ler o restante da mensagem (o payload real: rspHeader + rspData)
            received_payload = bytearray()
            bytes_to_read = msg_payload_size
            while len(received_payload) < bytes_to_read:
                remaining = bytes_to_read - len(received_payload)
                chunk = sock.recv(min(self.BUFFER_SIZE, remaining))
                if not chunk:
                    logger.error(f"Conexão fechada inesperadamente ao ler payload. Recebido {len(received_payload)} de {bytes_to_read} bytes.")
                    return None # Connection closed before full message received
                received_payload.extend(chunk)

            if len(received_payload) != bytes_to_read:
                 logger.error(f"Inconsistência na leitura. Esperado {bytes_to_read} bytes, recebido {len(received_payload)}.")
                 return None # Should not happen with the loop logic, but defensive check

            logger.debug(f"Payload completo da resposta lido ({len(received_payload)} bytes).")
            return bytes(received_payload)

        except socket.timeout:
            logger.error(f"Timeout ao ler resposta do servidor {self.server_ip}:{self.server_port}.")
            return None
        except struct.error as e:
             logger.error(f"Erro de struct ao desempacotar tamanho da mensagem: {e}")
             return None
        except Exception as e:
             logger.error(f"Erro inesperado ao ler resposta: {e}\n{traceback.format_exc()}")
             return None

    def _parse_response(self, response_payload: bytes, expected_seq_no: int) -> ResponseReturn:
        """Interpreta o payload da resposta binária do servidor."""
        logger.debug(f"Iniciando parse do payload de {len(response_payload)} bytes.")

        # 1. Validar o tamanho do payload recebido contra o formato esperado
        try:
             expected_size = struct.calcsize(self.RESPONSE_FORMAT)
             if len(response_payload) != expected_size:
                 logger.error(f"Tamanho incorreto do payload da resposta! Recebido: {len(response_payload)}, Esperado: {expected_size}. Parse abortado.")
                 # Log the mismatched payload for analysis
                 self._log_message(response_payload, "Payload da resposta com tamanho incorreto")
                 return ResponseReturn(False, f"Erro de protocolo: Tamanho da resposta inválido ({len(response_payload)} bytes)")

             # 2. Desempacotar a resposta usando o formato definido
             unpacked_data = struct.unpack(self.RESPONSE_FORMAT, response_payload)

        except struct.error as e:
            error_msg = f"Erro ao desempacotar resposta binária: {e}. Payload recebido pode estar malformado."
            logger.error(error_msg)
            self._log_message(response_payload, "Payload da resposta que causou erro de struct")
            return ResponseReturn(False, error_msg)

        # 3. Mapear os dados desempacotados para variáveis nomeadas
        try:
            (
                rsp_filler,          # Ignorado
                rsp_type,
                rsp_signature_b,
                rsp_company_sign_b,
                rsp_tmt,
                rsp_seq_no,
                rsp_term_id,
                rsp_card_id_b,
                rsp_status_code,     # <<< O código de status numérico
                rsp_op_display_txt_b,
                rsp_cust_display_txt_b,
                rsp_printer_line_txt_b,
                rsp_entry_timestamp,
                rsp_vehicle_type_code,
                rsp_ruf_1,           # Ignorado
                rsp_ruf_2            # Ignorado
            ) = unpacked_data

            # 4. Decodificar campos de string (bytes -> str) com segurança
            # Usando latin-1 como fallback para evitar erros de ascii
            rsp_signature = safe_decode(rsp_signature_b)
            rsp_company_sign = safe_decode(rsp_company_sign_b)
            rsp_card_id = safe_decode(rsp_card_id_b)
            rsp_op_display_txt = safe_decode(rsp_op_display_txt_b)
            rsp_cust_display_txt = safe_decode(rsp_cust_display_txt_b)
            rsp_printer_line_txt = safe_decode(rsp_printer_line_txt_b) # Este costuma ter a msg principal

            # 5. Logar os valores parseados para depuração
            logger.debug(f"Parse da Resposta - Status Code: {rsp_status_code} (0x{rsp_status_code:08X})")
            logger.debug(f"Parse da Resposta - SeqNo Recebido: {rsp_seq_no} (Esperado: {expected_seq_no})")
            logger.debug(f"Parse da Resposta - Card ID: '{rsp_card_id}'")
            logger.debug(f"Parse da Resposta - Op Display: '{rsp_op_display_txt}'")
            logger.debug(f"Parse da Resposta - Cust Display: '{rsp_cust_display_txt}'")
            logger.debug(f"Parse da Resposta - Printer Line: '{rsp_printer_line_txt}'")
            logger.debug(f"Parse da Resposta - Entry TS: {rsp_entry_timestamp}")
            logger.debug(f"Parse da Resposta - Vehicle Code: {rsp_vehicle_type_code}")

            # 6. Validar número de sequência
            if rsp_seq_no != expected_seq_no:
                 logger.warning(f"Número de sequência da resposta ({rsp_seq_no}) não corresponde ao esperado ({expected_seq_no})!")
                 # Decidir se isso é um erro fatal ou apenas um aviso

            # 7. Mapear rsp_status_code para ResponseStatus enum e mensagem
            success = False
            message = f"Status desconhecido: {rsp_status_code}"
            response_status_enum = ResponseStatus.UNKNOWN # Default

            # Mapeamento baseado na documentação (pág 8)
            status_map = {
                0x00000000: (ResponseStatus.VALIDATED, "Cartão validado com sucesso", True),
                0x00000001: (ResponseStatus.INVALID_CARD, "Cartão não validado", False), # Ou "Cartão Inválido"
                0x00000002: (ResponseStatus.ALREADY_VALIDATED, "Cartão já validado", False),
                0x00000003: (ResponseStatus.INSUFFICIENT_VALUE, "Valor da compra insuficiente para validação", False),
                0x00000004: (ResponseStatus.INVALID_CARD, "Cartão inválido", False), # Repetido? Usar INVALID_CARD
                0x00000005: (ResponseStatus.INVALID_COMMAND, "Comando inválido", False),
                0x00000006: (ResponseStatus.INVALID_OPERATION, "Operação inválida", False),
                0x00000007: (ResponseStatus.UNREGISTERED_TERMINAL, "Terminal não cadastrado", False), # Nota: Doc tem 7 duas vezes
                0x00000008: (ResponseStatus.DISCOUNT_TIME_EXCEEDED, "Tempo de desconto excedido", False),
                # Adicionar outros códigos se existirem
            }
            # Tratar o segundo 0x00000007 -> Tipo de cartão inválido
            if rsp_status_code == 0x00000007:
                 # Verificar qual mensagem faz mais sentido, ou usar um status específico
                 # Se rspPrinterLineTxt contiver "Tipo de cartao invalido", usar esse status
                 if "Tipo de cartao invalido" in rsp_printer_line_txt:
                      response_status_enum = ResponseStatus.INVALID_CARD_TYPE # Adicionar este enum se necessário
                      message = "Tipo de cartão inválido"
                      success = False
                 else: # Senão, assumir Terminal não cadastrado
                      response_status_enum, message, success = status_map[rsp_status_code]
            elif rsp_status_code in status_map:
                response_status_enum, message, success = status_map[rsp_status_code]
            else:
                 logger.warning(f"Código de status não mapeado recebido: {rsp_status_code}")
                 # Manter success=False e a mensagem padrão "Status desconhecido"

            # 8. Mapear vehicle type code (Opcional, mas bom ter)
            vehicle_type_str = None
            if rsp_vehicle_type_code == 0x0001: # 1
                vehicle_type_str = VehicleType.MOTO.value # Assumindo enum VehicleType.MOTO = "Moto"
            elif rsp_vehicle_type_code == 0x0002: # 2
                vehicle_type_str = VehicleType.CARRO.value # Assumindo enum VehicleType.CARRO = "Carro"


            # 9. Construir o objeto DiscountResponse
            discount_response = DiscountResponse(
                status=response_status_enum,
                message=rsp_printer_line_txt or message, # Usar texto da impressora se disponível, senão o mapeado
                entry_timestamp=rsp_entry_timestamp if rsp_entry_timestamp != 0 else None, # Não mostrar 0 se não houver timestamp
                vehicle_type=vehicle_type_str
            )

            # 10. Construir e retornar o ResponseReturn final
            final_message = discount_response.message # Usar a mensagem final do DiscountResponse
            logger.info(f"Resposta processada - Sucesso: {success}, Status: {response_status_enum.name}, Mensagem: '{final_message}'")
            return ResponseReturn(
                success=success,
                message=final_message,
                data=discount_response
            )

        except Exception as ex:
            error_msg = f"Erro inesperado durante o parse da resposta: {str(ex)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            # Logar os dados brutos que causaram o erro de parse
            self._log_message(response_payload, "Payload da resposta que causou erro de parse inesperado")
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
            chunk = data[i:i+16]
            hex_part = ' '.join(f"{b:02x}" for b in chunk)
            # Usar '.' para bytes não imprimíveis ou fora do range ASCII básico comum
            ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            lines.append(f"{i:04x}   {hex_part.ljust(47)}  {ascii_part}")
        return '\n'.join(lines)

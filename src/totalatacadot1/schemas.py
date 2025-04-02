from dataclasses import dataclass
from datetime import datetime, UTC
import struct
from typing import Optional
import time

from totalatacadot1.enums import CommandType, ResponseStatus


@dataclass
class DiscountRequest:
    cmd_term_id: int  # numcaixa
    cmd_card_id: str  # código de barras do cartão
    cmd_op_value: int  # em centavos
    cmd_signature: str = "04558054000173"  # Fiscal Document CNPJ
    cmd_op_seq_no: int = 0  # numcupom / get next number / zero por enquanto
    cmd_ruf_0: int = 0xFFFFFFFF
    cmd_ruf_1: int = 0xFFFFFFFF
    cmd_sale_type: int = 0xFFFFFFFF
    cmd_op_display_len: int = 0
    cmd_cust_display_len: int = 0
    cmd_printer_line_len: int = 40

    cmd_tmt: int = int(time.time())
    cmd_type: CommandType = CommandType.VALIDATION
    cmd_company_sign: bytes = b"ESTAPAR" + b" " * 8 + b"\x00"  # 16 bytes total
    cmd_seq_no: int = 0

    def __repr__(self):
        return f"""DiscountRequest(
            cmd_term_id={self.cmd_term_id},
            cmd_card_id={self.cmd_card_id},
            cmd_op_value={self.cmd_op_value},
            cmd_signature={self.cmd_signature},
            cmd_op_seq_no={self.cmd_op_seq_no},
            cmd_ruf_0={self.cmd_ruf_0},
            cmd_ruf_1={self.cmd_ruf_1},
            cmd_sale_type={self.cmd_sale_type},
            cmd_op_display_len={self.cmd_op_display_len},
            cmd_cust_display_len={self.cmd_cust_display_len},
            cmd_printer_line_len={self.cmd_printer_line_len},
            cmd_tmt={self.cmd_tmt},
            cmd_type={self.cmd_type},
            cmd_company_sign={self.cmd_company_sign},
            cmd_seq_no={self.cmd_seq_no}
        )"""

    def validate(self):
        """Validação consolidada como no C#"""
        if self.cmd_op_value <= 0:
            raise ValueError("Valor da compra deve ser maior que zero")
        if self.cmd_term_id <= 0:
            raise ValueError("TerminalId inválido")
        if not self.cmd_card_id or self.cmd_card_id.strip() == "":
            raise ValueError("Cartão inválido")
        if not self.cmd_signature or self.cmd_signature.strip() == "":
            raise ValueError("Documento fiscal inválido")
        # if not validar_cnpj(self.cmd_signature):
        #     raise ValueError("Documento fiscal inválido (CNPJ inválido)")

    def serialize(self) -> bytes:
        """Serialização final corrigida para corresponder exatamente ao protocolo Estapar"""
        # cmdData - Formato corrigido conforme documentação Estapar
        cmd_data = struct.pack(
            "<I64sIIIIIIII",
            self.cmd_term_id,  # 4 bytes
            self.cmd_card_id.encode("ascii").ljust(64, b"\x00"),  # 64 bytes
            self.cmd_op_value,  # 4 bytes
            self.cmd_op_seq_no,  # 4 bytes
            self.cmd_ruf_0,  # 4 bytes
            self.cmd_ruf_1,  # 4 bytes
            self.cmd_sale_type,  # 4 bytes
            self.cmd_op_display_len,  # 4 bytes
            self.cmd_cust_display_len,  # 4 bytes
            self.cmd_printer_line_len,  # 4 bytes
        )  # 100 bytes

        # cmdHeader - Formato exato conforme documentação
        cmd_header = struct.pack(
            "<HI15s16sII",
            0,  # cmdFiller (2 bytes)
            self.cmd_type.value,  # cmdType (4 bytes)
            self.cmd_signature.encode("ascii").ljust(15, b"\x00"),  # 15 bytes
            self.cmd_company_sign,  # 16 bytes
            self.cmd_tmt,  # cmdTmt (4 bytes)
            self.cmd_seq_no,  # cmdSeqNo (4 bytes)
        )

        # Combina header + data
        message = cmd_header + cmd_data

        # Adiciona o tamanho total no início (msgBlockSize)
        msg_block_size = len(message)
        full_message = struct.pack("<H", msg_block_size) + message

        return full_message


@dataclass
class DiscountResponse:
    status: ResponseStatus
    message: str
    entry_timestamp: Optional[int] = None
    vehicle_type: Optional[str] = None

    def __str__(self):
        """Retorna uma string formatada com os detalhes da resposta."""
        lines = ["Detalhes Adicionais:"] # Cabeçalho para os detalhes

        # Formata a data/hora de entrada (se disponível)
        if self.entry_timestamp is not None:
            try:
                dt_object = datetime.fromtimestamp(self.entry_timestamp, UTC)
                # Formato mais comum no Brasil: DD/MM/AAAA HH:MM:SS
                formatted_time = dt_object.strftime("%d/%m/%Y %H:%M:%S") 
                lines.append(f"    Data/Hora de Entrada: {formatted_time}")
            except (TypeError, ValueError):
                 # Caso o timestamp seja inválido por algum motivo
                 lines.append(f"    Data/Hora de Entrada: (timestamp inválido: {self.entry_timestamp})")
        else:
            # Se não houver timestamp na resposta
            lines.append("    Data/Hora de Entrada: Não informada")

        # Formata o tipo de veículo (se disponível)
        vehicle_display = self.vehicle_type if self.vehicle_type is not None else "Não informado"
        lines.append(f"    Tipo de Veículo: {vehicle_display}")

        # Adiciona o status parseado para clareza (opcional)
        # lines.append(f"    Status Detalhado: {self.status.name}") 

        # Retorna as linhas unidas por quebra de linha
        # Só retorna os detalhes se houver mais do que o cabeçalho
        return "\n".join(lines) if len(lines) > 1 else ""



@dataclass
class ResponseReturn:
    """Retorno padronizado para o cliente"""

    success: bool
    message: str
    data: Optional[DiscountResponse] = None

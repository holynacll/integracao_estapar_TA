from dataclasses import dataclass
import struct
from typing import Optional
import time

from totalatacadot1.enums import CommandType, ResponseStatus

@dataclass
class DiscountRequest:
    cmd_term_id: int # numcaixa
    cmd_card_id: str # código de barras do cartão
    cmd_op_value: int # em centavos
    cmd_signature: str = "04558054000173" # Fiscal Document CNPJ
    cmd_op_seq_no: int = 0 # numcupom / get next number / zero por enquanto
    cmd_ruf_0: int = 0xFFFFFFFF
    cmd_ruf_1: int = 0xFFFFFFFF
    cmd_sale_type: int = 0xFFFFFFFF
    cmd_op_display_len: int = 0
    cmd_cust_display_len: int = 0
    cmd_printer_line_len: int = 40
    
    cmd_tmt: int = int(time.time())
    cmd_type: CommandType = CommandType.VALIDATION
    cmd_company_sign: bytes = b"ESTAPAR" + b' '*8 + b'\x00'  # 16 bytes total
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
            "<I64sIIIII",  # 7 itens no total (I64s conta como 2 + 5 inteiros)
            self.cmd_term_id,               # 4 bytes
            self.cmd_card_id.encode('ascii').ljust(64, b'\x00'),  # 64 bytes
            self.cmd_op_value,              # 4 bytes
            self.cmd_op_seq_no,             # 4 bytes
            self.cmd_ruf_0,                 # 4 bytes
            self.cmd_ruf_1,                 # 4 bytes
            self.cmd_sale_type              # 4 bytes
        )  # Total: 64 + 6*4 = 64 + 24 = 88 bytes

        # cmdHeader - Formato exato conforme documentação
        cmd_header = struct.pack(
            "<HHI15s16sII",  # 8 itens no total
            0,                      # cmdFiller (2 bytes)
            self.cmd_type.value,     # cmdType (4 bytes)
            self.cmd_tmt,            # cmdTmt (4 bytes)
            self.cmd_signature.encode('ascii').ljust(15, b'\x00'),  # 15 bytes
            b"ESTAPAR".ljust(15, b' ') + b'\x00',  # 16 bytes
            self.cmd_seq_no,         # cmdSeqNo (4 bytes)
            len(cmd_data)            # Tamanho dos dados (4 bytes)
        )  # Total: 2 + 4 + 4 + 15 + 16 + 4 + 4 = 49 bytes

        # Combina header + data
        message = cmd_header + cmd_data  # 49 + 88 = 137 bytes

        # Adiciona o tamanho total no início (msgBlockSize)
        msg_block_size = len(message)  # 137 bytes
        full_message = struct.pack("<H", msg_block_size) + message  # 2 + 137 = 139 bytes

        return full_message    

@dataclass
class DiscountResponse:
    """Estrutura de resposta da API"""
    status: ResponseStatus
    message: str
    entry_timestamp: Optional[int] = None
    vehicle_type: Optional[str] = None

@dataclass
class ResponseReturn:
    """Retorno padronizado para o cliente"""
    success: bool
    message: str
    data: Optional[DiscountResponse] = None

from enum import IntEnum


class CommandType(IntEnum):
    """Tipos de comando suportados pela API da Estapar"""
    CONSULT = 0x0000000F  # 15 - Consulta
    VALIDATION = 0x00000010  # 16 - Validação

class ResponseStatus(IntEnum):
    """Status de resposta possíveis da API"""
    VALIDATED = 0x00000000
    NOT_VALIDATED = 0x00000001
    ALREADY_VALIDATED = 0x00000002
    INSUFFICIENT_VALUE = 0x00000003
    INVALID_CARD = 0x00000004
    INVALID_COMMAND = 0x00000005
    INVALID_OPERATION = 0x00000006
    UNREGISTERED_TERMINAL = 0x00000007
    DISCOUNT_TIME_EXCEEDED = 0x00000008
    UNKNOWN_ERROR = 0x00000009
    
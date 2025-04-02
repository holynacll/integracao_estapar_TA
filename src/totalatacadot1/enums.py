from enum import Enum, IntEnum


class CommandType(IntEnum):
    """Tipos de comando suportados pela API da Estapar"""

    CONSULT = 0x0000000F  # 15 - Consulta
    VALIDATION = 0x00000010  # 16 - Validação


class ResponseStatus(Enum):
    VALIDATED = 0
    INVALID_CARD = 1
    ALREADY_VALIDATED = 2
    INSUFFICIENT_VALUE = 3
    # INVALID_CARD = 4 # Código 4 também é cartão inválido, mapeado para INVALID_CARD
    INVALID_COMMAND = 5
    INVALID_OPERATION = 6
    UNREGISTERED_TERMINAL = 7
    DISCOUNT_TIME_EXCEEDED = 8
    INVALID_CARD_TYPE = 9  # Status específico para o segundo código 7
    UNKNOWN = 99


class VehicleType(Enum):
    MOTO = "Moto"
    CARRO = "Carro"

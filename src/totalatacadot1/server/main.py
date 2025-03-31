import os
import socket
import struct
import time

from loguru import logger
from dotenv import load_dotenv

load_dotenv()
IP = os.environ.get("IP")
PORT = int(os.environ.get("PORT"))


def msg_process(mensagem):
    """Processa a mensagem recebida e retorna uma resposta simulada."""

    # Lendo os primeiros 2 bytes que indicam o tamanho da mensagem
    msgBlockSize = struct.unpack("<H", mensagem[:2])[0]

    # Extraindo cmdType (4 bytes little-endian, começando no byte 4)
    cmdType = struct.unpack("<I", mensagem[4:8])[0]

    # Lendo o código do cartão (64 bytes, a partir do byte 25)
    card_id = mensagem[25:89].decode().strip("\x00")

    logger.info(f"Recebido comando: {hex(cmdType)} para cartão {card_id}")

    # Definição do tipo de resposta
    if cmdType == 0x0000000F:  # cmdConsult
        rspType = 0x0001000F
        status = 0x00000000  # Cartão validado
    elif cmdType == 0x00000010:  # cmdValidation
        rspType = 0x00010010
        status = 0x00000002  # Cartão já validado
    else:
        return None  # Comando desconhecido

    # Criando a resposta no formato esperado
    rspTmt = int(time.time())  # Timestamp
    rspSeqNo = 1  # Número sequencial da resposta

    resposta = struct.pack(
        "<HHI15s16sII64sI128s128s128sIHHI",
        msgBlockSize,  # Tamanho da mensagem
        0,  # rspFiller
        rspType,  # Tipo de resposta
        b"04558054000173".ljust(15, b"\x00"),  # Assinatura da empresa
        b"ESTAPAR".ljust(16, b"\x00"),  # Nome da empresa
        rspTmt,  # Timestamp da resposta
        rspSeqNo,  # Número sequencial
        card_id.encode().ljust(64, b"\x00"),  # Código do cartão
        status,  # Status da operação
        b"Mensagem para operador".ljust(128, b"\x00"),  # Mensagem para operador
        b"Mensagem para cliente".ljust(128, b"\x00"),  # Mensagem para cliente
        b"Mensagem para impressao".ljust(128, b"\x00"),  # Mensagem para impressão
        int(time.time()),  # Data de entrada (simulada)
        0x0002,  # Tipo de veículo (Carro)
        0x0000,  # Reservado
        0x00000000,  # Reservado
    )

    return resposta


def start_server():
    """Inicia o servidor e aguarda conexões."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((IP, PORT))
        server.listen(5)
        logger.info(f"Servidor escutando em {IP}:{PORT}")

        while True:
            conn, addr = server.accept()
            logger.info(f"Conexão estabelecida de {addr}")
            with conn:
                logger.info(f"Conexão de {addr}")

                # Lendo os primeiros 2 bytes para saber o tamanho da mensagem
                tamanho = conn.recv(2)
                if not tamanho:
                    continue

                msg_size = struct.unpack("<H", tamanho)[0]

                # Lendo o restante da mensagem
                mensagem = conn.recv(msg_size)

                # Processa a mensagem recebida e gera uma resposta
                resposta = msg_process(tamanho + mensagem)

                if resposta:
                    conn.sendall(resposta)
                    logger.info("Resposta enviada!")


if __name__ == "__main__":
    start_server()

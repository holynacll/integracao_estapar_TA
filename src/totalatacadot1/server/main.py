import socket
import struct
import time

from loguru import logger
from dotenv import load_dotenv

load_dotenv()
IP = "127.0.0.1"
PORT = 33535


def msg_process(mensagem):
    """Processa a mensagem recebida e retorna uma resposta simulada."""
    try:
        # Extraindo cmdType (4 bytes little-endian, começando no byte 4)
        cmdType = struct.unpack("<I", mensagem[4:8])[0]

        # Lendo o código do cartão (64 bytes, a partir do byte 25)
        # Remove padding e decodifica como ASCII
        card_id = mensagem[25:89].split(b"\x00")[0].decode("ascii")

        logger.info(f"Recebido comando: {hex(cmdType)} para cartão {card_id}")

        # Definição do tipo de resposta
        if cmdType == 0x0000000F:  # cmdConsult
            rspType = 0x0001000F
            status = 0x00000000  # Cartão validado
            status_msg = f"Cartao validado ate {time.strftime('%d/%m/%Y - %H:%M')}"
        elif cmdType == 0x00000010:  # cmdValidation
            rspType = 0x00010010
            status = 0x00000000  # Cartão validado
            status_msg = f"Cartao validado ate {time.strftime('%d/%m/%Y - %H:%M')}"
        else:
            return None  # Comando desconhecido

        # Criando a resposta no formato esperado
        rspTmt = int(time.time())  # Timestamp
        rspSeqNo = struct.unpack("<I", mensagem[28:32])[
            0
        ]  # Pega o cmdSeqNo da mensagem original

        resposta = struct.pack(
            "<HHI15s16sIII64sI128s128s128sIHHI",
            513,  # Tamanho do payload da resposta (513 bytes)
            0,  # rspFiller
            rspType,  # Tipo de resposta
            b"04558054000173".ljust(15, b"\x00"),  # Assinatura da empresa
            b"ESTAPAR".ljust(15, b" ") + b"\x00",  # Nome da empresa (16 bytes total)
            rspTmt,  # Timestamp da resposta
            rspSeqNo,  # Número sequencial (mesmo da requisição)
            0,  # rspTermId (Novo campo adicionado para alinhar)
            card_id.encode("ascii").ljust(64, b"\x00"),  # Código do cartão
            status,  # Status da operação
            status_msg.encode("ascii").ljust(128, b"\x00"),  # Mensagem para operador
            status_msg.encode("ascii").ljust(128, b"\x00"),  # Mensagem para cliente
            status_msg.encode("ascii").ljust(128, b"\x00"),  # Mensagem para impressão
            int(time.time()) - 3600,  # Data de entrada (1 hora atrás)
            0x0002,  # Tipo de veículo (Carro)
            0x0000,  # Reservado (rspRUF_1)
            0x00000000,  # Reservado (rspRUF_2)
        )

        return resposta

    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        return None


def start_server():
    """Inicia o servidor e aguarda conexões."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((IP, PORT))
        server.listen(5)
        logger.info(f"Servidor escutando em {IP}:{PORT}")

        while True:
            try:
                conn, addr = server.accept()
                logger.info(f"Conexão estabelecida de {addr}")
                with conn:
                    # Lendo os primeiros 2 bytes para saber o tamanho da mensagem
                    tamanho = conn.recv(2)
                    if not tamanho:
                        continue

                    msg_size = struct.unpack("<H", tamanho)[0]

                    # Lendo o restante da mensagem
                    mensagem = b""
                    while len(mensagem) < msg_size:
                        chunk = conn.recv(msg_size - len(mensagem))
                        if not chunk:
                            break
                        mensagem += chunk

                    if len(mensagem) == msg_size:
                        # Processa a mensagem recebida e gera uma resposta
                        resposta = msg_process(tamanho + mensagem)

                        if resposta:
                            conn.sendall(resposta)
                            logger.info("Resposta enviada!")
                    else:
                        logger.warning(f"Mensagem incompleta recebida de {addr}")

            except Exception as e:
                logger.error(f"Erro na conexão: {e}")
                continue


if __name__ == "__main__":
    start_server()

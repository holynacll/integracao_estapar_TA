from dataclasses import dataclass
import requests
import json
from loguru import logger

from totalatacadot1.config import get_url_notification
from totalatacadot1.enums import CommandType


@dataclass
class Notification():
    ticket_code: str
    num_ped_ecf: int
    vl_total: float
    operation_type: CommandType
    success: bool
    message: str

    def to_dict(self):
        return {
            "ticket_code": self.ticket_code,
            "num_ped_ecf": self.num_ped_ecf,
            "vl_total": self.vl_total,
            "operation_type": self.operation_type,
            "success": self.success,
            "message": self.message,
        }


    def notify_discount(self):
        """Envia uma notificação para o endpoint configurado."""
        # Converte para JSON
        try:
            notification_data = self.to_dict()
            json_data = json.dumps(notification_data)
            headers = {"Content-Type": "application/json"}

            # Envia a requisição POST
            response = requests.post(get_url_notification(), data=json_data, headers=headers, timeout=5)
            response.raise_for_status()  # Levanta um erro para status HTTP ruins (4xx ou 5xx)

            logger.info(f"Notificação enviada com sucesso para {get_url_notification()}. Resposta: {response.status_code}")

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout ao enviar notificação para {get_url_notification()}.")
        except requests.exceptions.ConnectionError:
            logger.warning(f"Não foi possível conectar ao servidor de notificação em {get_url_notification()}.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao enviar notificação: {e}")
        except Exception as e:
            logger.error(f"Erro inesperado ao enviar notificação: {e}")


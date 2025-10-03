from dataclasses import dataclass
import requests
import json
from loguru import logger

from totalatacadot1.config import get_url_notification
from totalatacadot1.repository import create_notification_item, update_notification_item_sent


@dataclass
class Notification():
    ticket_code: str
    vl_total: float
    operation_type: str
    num_caixa: int | None = None
    num_cupom: int | None = None
    num_ped_ecf: str | None = None
    success: bool | None = None
    message: str | None = None

    def to_dict(self):
        return {
            "ticket_code": self.ticket_code,
            "num_ped_ecf": self.num_ped_ecf,
            "num_caixa": self.num_caixa,
            "num_cupom": self.num_cupom,
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
            url = get_url_notification() + '/items'

            # Envia a requisição POST
            response = requests.post(url, data=json_data, headers=headers, timeout=5)
            response.raise_for_status()  # Levanta um erro para status HTTP ruins (4xx ou 5xx)

            logger.info(f"Notificação enviada com sucesso para {url}. Resposta: {response.status_code}")
            update_notification_item_sent(self.ticket_code)
        except requests.exceptions.Timeout:
            logger.warning("Timeout ao enviar notificação.")
            create_notification_item(self.to_dict())
        except requests.exceptions.ConnectionError:
            logger.warning("Não foi possível conectar ao servidor de notificação.")
            create_notification_item(self.to_dict())
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao enviar notificação: {e}")
            create_notification_item(self.to_dict())
        except Exception as e:
            logger.error(f"Erro inesperado ao enviar notificação: {e}")
            create_notification_item(self.to_dict())


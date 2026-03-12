import sys
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

def _get_project_root() -> Path:
    return Path(__file__).parent

def _get_env_file_for_frozen_app() -> Path | str:
    """Retorna o caminho do .env baseado no contexto de execução (Dev vs Prod)."""
    if getattr(sys, "frozen", False) or "briefcase" in sys.executable.lower() or sys.platform == "win32":
        exe_dir_env = Path(sys.executable).parent / ".env"
        if exe_dir_env.exists():
            return exe_dir_env
    # Fallback para desenvolvimento
    return _get_project_root() / ".env"

class Settings(BaseSettings):
    # API Estapar
    estapar_ip: str = "10.7.39.10"
    estapar_port: int = 3000

    # Banco de Dados Oracle
    oracle_user: str = "CAIXA"
    oracle_password: str = "CAIXA"
    oracle_host: str = "localhost"
    oracle_port: str = "1521"
    oracle_sid: str = "XEPDB1"
    oracle_sid_alternative_1 = "XE"

    # URL Notificação
    url_notification: str = "http://192.168.211.249:8000"

    # Configuração Pydantic
    model_config = SettingsConfigDict(
        env_file=('.env', '.env.development', '.env.production'),
        env_file_encoding='utf-8',
        extra='ignore'
    )

    # --- Propriedades de Caminhos ---
    @property
    def project_root(self) -> Path:
        return _get_project_root()

    @property
    def assets_path(self) -> Path:
        return self.project_root / "assets"

    @property
    def images_path(self) -> Path:
        return self.assets_path / "images"

    @property
    def orcl_instant_client_path(self) -> Path:
        return self.project_root / "instantclient_19_26"

    @property
    def orcl_instant_client_path_zipped(self) -> Path:
        return self.project_root / "instantclient-basic-windows.x64.zip"

# Instância Global de Configurações
settings = Settings(_env_file=_get_env_file_for_frozen_app())

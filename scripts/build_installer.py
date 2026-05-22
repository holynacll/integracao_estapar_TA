#!/usr/bin/env python3
"""Gera o instalador Windows para um tipo de loja (VAREJO ou ATACADO).

A única diferença entre as duas versões do app é a variável `store_type`:
- VAREJO  -> último pedido buscado por num_cupom
- ATACADO -> último pedido buscado por num_ped_ecf

Este script grava o `store_type` correto no .env empacotado (preservando as
demais linhas do arquivo) e roda o briefcase para produzir o instalador.

Uso (na máquina de build Windows):
    python scripts/build_installer.py VAREJO
    python scripts/build_installer.py ATACADO
"""

import subprocess
import sys
from pathlib import Path

ENV_PATH = (
    Path(__file__).resolve().parent.parent / "src" / "totalatacadot1" / ".env"
)
VALID = {"VAREJO", "ATACADO"}


def set_store_type(store_type: str) -> None:
    """Substitui/insere a linha store_type no .env, mantendo o restante."""
    lines: list[str] = []
    if ENV_PATH.exists():
        lines = ENV_PATH.read_text(encoding="utf-8").splitlines()
    lines = [
        ln for ln in lines if not ln.strip().lower().startswith("store_type")
    ]
    lines.append(f"store_type={store_type}")
    ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[ok] store_type={store_type} gravado em {ENV_PATH}")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1].upper() not in VALID:
        print("Uso: python scripts/build_installer.py [VAREJO|ATACADO]")
        return 2

    store_type = sys.argv[1].upper()
    set_store_type(store_type)

    # `update` copia as fontes (incluindo o .env) para o bundle antes de empacotar.
    for cmd in (["briefcase", "update"], ["briefcase", "package", "windows"]):
        print(f"[run] {' '.join(cmd)}")
        rc = subprocess.call(cmd)
        if rc != 0:
            return rc
    print(f"[ok] Instalador {store_type} gerado. Verifique a pasta dist/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

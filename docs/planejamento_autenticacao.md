# Planejamento — Autenticação e Timeout de Sessão

> **Status:** Proposto
> **Data:** 2026-05-19
> **Responsável:** —

---

## 1. Objetivo

Implementar uma camada de autenticação no aplicativo de integração Estapar:

1. Ao abrir o programa, exigir autenticação (senha; usuário opcional — ver decisão em aberto).
2. Após `X` horas de inatividade, invalidar a sessão e exigir nova autenticação.
3. Armazenar a senha configurada (como hash) no banco **SQLite** existente.

---

## 2. História do Usuário

**Como** operador do sistema de integração Estapar,
**Quero** ser autenticado ao abrir o programa e ter minha sessão expirada após inatividade,
**Para que** o acesso às operações de integração seja protegido contra uso não autorizado.

### Critérios de Aceitação

- [ ] Ao iniciar, uma tela de autenticação é exibida antes de qualquer funcionalidade.
- [ ] Senha válida libera o uso; senha inválida exibe erro e bloqueia o acesso.
- [ ] Se nenhuma senha estiver cadastrada, o sistema solicita a definição de uma senha inicial.
- [ ] Após `X` horas sem interação, a sessão expira e a tela de autenticação reaparece.
- [ ] O valor de `X` é configurável (padrão sugerido: **8 horas**).
- [ ] Nenhuma operação fica acessível sem sessão ativa.

---

## 3. Problema Crítico a Resolver Primeiro

O `init_db()` atual **apaga o banco SQLite inteiro a cada startup**:

```python
# database.py (comportamento atual)
def init_db():
    if SQLITE_DB_PATH.exists():
        SQLITE_DB_PATH.unlink()   # ← deleta o arquivo
    BaseSQLite.metadata.create_all(bind=sqlite_engine)
```

Se a senha for gravada no SQLite, ela seria perdida a cada abertura do programa.

### Correção

Remover o `unlink()` e usar criação idempotente (`create_all` já é seguro com `checkfirst=True` por padrão):

```python
def init_db():
    logger.info("Iniciando a inicialização do banco de dados...")
    if sqlite_engine:
        BaseSQLite.metadata.create_all(bind=sqlite_engine)  # cria só o que falta
    logger.info("Tabelas SQLite verificadas/criadas com sucesso.")
    create_oracle_tables()
```

> **Atenção:** Verificar se algum fluxo dependia do reset do banco a cada execução
> (ex.: limpeza de `ControlPDV`/`Notification`). Caso dependesse, isolar a limpeza
> dessas tabelas específicas em vez de apagar o arquivo inteiro.

---

## 4. Componentes da Implementação

### 4.1. Model `AuthConfig` — `src/totalatacadot1/models.py`

```python
class AuthConfig(BaseSQLite):
    __tablename__ = "AuthConfig"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(120), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    session_timeout_hours: Mapped[int] = mapped_column(Integer, default=8)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
```

- Tabela mantém **uma única linha** (id=1) com a configuração de autenticação.

### 4.2. Hash de senha

- Dependência: `bcrypt` (adicionar ao `pyproject.toml`).
- Funções utilitárias (novo módulo `src/totalatacadot1/security.py`):
  - `hash_password(plain: str) -> str`
  - `check_password(plain: str, hashed: str) -> bool`

### 4.3. Funções de repositório — `src/totalatacadot1/repository.py`

```python
def get_auth_config() -> AuthConfig | None: ...
def has_password_configured() -> bool: ...
def set_auth_password(plain_password: str, timeout_hours: int = 8) -> AuthConfig: ...
def verify_login(plain_password: str) -> bool: ...
```

### 4.4. Tela de login — `src/totalatacadot1/gui/login_dialog.py` (novo)

- `QDialog` modal com:
  - Campo de senha (`QLineEdit` com `EchoMode.Password`).
  - (Opcional) campo de usuário.
  - Botão "Entrar".
  - Mensagem de erro inline.
- Modo "definição de senha inicial" quando `has_password_configured()` for `False`
  (dois campos: senha + confirmação).
- Retorna sucesso/falha para o chamador.

### 4.5. Integração no startup — `src/totalatacadot1/app.py`

- Após `db_init_setup()` e antes de iniciar a thread de background / event loop:
  - Exibir `LoginDialog`.
  - Se cancelado/falho → encerrar aplicação (`sys.exit`).

### 4.6. Timeout de inatividade — `src/totalatacadot1/controllers/app_controller.py`

- `QTimer` de inatividade reiniciado a cada interação relevante do usuário.
- Ao disparar (após `X` horas):
  - Esconder a GUI principal.
  - Reexibir `LoginDialog`.
  - Bloquear ações até nova autenticação bem-sucedida.
- Ler `session_timeout_hours` do `AuthConfig`.

---

## 5. Arquivos Afetados

| Arquivo | Ação |
|---|---|
| `src/totalatacadot1/database.py` | Modificar `init_db()` (remover `unlink`) |
| `src/totalatacadot1/models.py` | Adicionar model `AuthConfig` |
| `src/totalatacadot1/security.py` | **Novo** — hash/verificação de senha |
| `src/totalatacadot1/repository.py` | Adicionar funções de auth |
| `src/totalatacadot1/gui/login_dialog.py` | **Novo** — tela de login |
| `src/totalatacadot1/controllers/app_controller.py` | Timer de timeout + reexibição |
| `src/totalatacadot1/app.py` | Chamada de login no startup |
| `pyproject.toml` | Adicionar dependência `bcrypt` |

---

## 6. Etapas de Execução

1. [ ] Corrigir `init_db()` e validar que dados persistem entre reinícios.
2. [ ] Adicionar dependência `bcrypt`.
3. [ ] Criar `security.py` (hash/verify).
4. [ ] Criar model `AuthConfig`.
5. [ ] Criar funções de repositório de auth.
6. [ ] Criar `LoginDialog` (com modo de definição de senha inicial).
7. [ ] Integrar login no startup (`app.py`).
8. [ ] Implementar timer de timeout no `AppController`.
9. [ ] Teste manual completo do fluxo (ver seção 8).

---

## 7. Decisões em Aberto

- [ ] **Usuário + senha** ou **apenas senha**? (model já prevê `username` opcional).
- [ ] Valor padrão de timeout: **8 horas** (confirmar).
- [ ] A senha inicial é definida pela própria tela ou por script utilitário/admin?
- [ ] Deve haver opção de trocar a senha pela UI?
- [ ] Limite de tentativas de senha (bloqueio temporário)? (fora do escopo inicial)

---

## 8. Plano de Teste Manual

1. **Primeiro uso:** sem senha cadastrada → solicita definição de senha inicial.
2. **Login válido:** senha correta libera o app.
3. **Login inválido:** senha errada exibe erro e mantém bloqueio.
4. **Persistência:** fechar e reabrir o app → senha continua cadastrada (não pede definição de novo).
5. **Timeout:** simular `X` horas de inatividade (usar valor pequeno temporariamente) → app exige novo login.
6. **Reautenticação:** após timeout, login válido restaura o uso normal.

---

## 9. Estimativa

| Tarefa | Horas |
|---|---|
| Corrigir `init_db()` + model `AuthConfig` | 0.5 |
| `security.py` + repositório de auth | 0.5 |
| `LoginDialog` (PySide6) | 1.5 |
| Integração startup + timeout no controller | 1.5 |
| Testes manuais e ajustes | 0.5 |
| **Total** | **~4.5h** |

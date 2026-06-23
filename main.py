import logging
import sys

import requests
from dotenv import load_dotenv
from supabase import Client, create_client
import os

# ---------------------------------------------------------------------------
# Configuração de logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Carregamento de variáveis de ambiente
# ---------------------------------------------------------------------------
load_dotenv()

SUPABASE_URL: str = os.environ["SUPABASE_URL"]
SUPABASE_KEY: str = os.environ["SUPABASE_KEY"]
SUPABASE_TABLE: str = os.getenv("SUPABASE_TABLE", "contacts")

ZAPI_INSTANCE_ID: str = os.environ["ZAPI_INSTANCE_ID"]
ZAPI_TOKEN: str = os.environ["ZAPI_TOKEN"]

ZAPI_BASE_URL: str = (
    f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}"
)

MAX_CONTACTS: int = 3


# ---------------------------------------------------------------------------
# Supabase
# ---------------------------------------------------------------------------
def get_supabase_client() -> Client:
    """Cria e retorna um cliente autenticado do Supabase."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_contacts(client: Client) -> list[dict]:
    """
    Busca até MAX_CONTACTS contatos na tabela definida em SUPABASE_TABLE.

    Espera colunas: name (str), phone (str — formato 5511999999999).
    """
    logger.info("Buscando contatos no Supabase (tabela: %s)...", SUPABASE_TABLE)
    response = (
        client.table(SUPABASE_TABLE)
        .select("name, phone")
        .limit(MAX_CONTACTS)
        .execute()
    )
    contacts = response.data
    logger.info("%d contato(s) encontrado(s).", len(contacts))
    return contacts


# ---------------------------------------------------------------------------
# Z-API
# ---------------------------------------------------------------------------
def send_whatsapp_message(phone: str, name: str) -> None:
    """
    Envia a mensagem "Olá, <name> tudo bem com você?" via Z-API.

    Args:
        phone: Número no formato E.164 sem '+' (ex: 5511999999999).
        name:  Nome do contato para personalizar a mensagem.
    """
    url = f"{ZAPI_BASE_URL}/send-text"
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "phone": phone,
        "message": f"Olá, {name} tudo bem com você?",
    }

    logger.info("Enviando mensagem para %s (%s)...", name, phone)
    response = requests.post(url, json=payload, headers=headers, timeout=15)
    response.raise_for_status()

    data = response.json()
    logger.info("Mensagem enviada com sucesso. Resposta da Z-API: %s", data)


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------
def main() -> None:
    logger.info("=== Iniciando script ===")

    # 1. Conectar ao Supabase e buscar contatos
    try:
        supabase = get_supabase_client()
        contacts = fetch_contacts(supabase)
    except KeyError as exc:
        logger.error("Variável de ambiente obrigatória não encontrada: %s", exc)
        sys.exit(1)
    except Exception as exc:
        logger.error("Erro ao buscar contatos no Supabase: %s", exc)
        sys.exit(1)

    if not contacts:
        logger.warning("Nenhum contato encontrado. Encerrando.")
        return

    # 2. Enviar mensagem para cada contato via Z-API
    success_count = 0
    for contact in contacts:
        name: str = contact.get("name", "").strip()
        phone: str = contact.get("phone", "").strip()

        if not name:
            logger.warning("Contato ignorado por nome ausente: %s", contact)
            continue

        if not phone:
            logger.warning("Contato ignorado por telefone ausente: %s", contact)
            continue

        logger.info("Enviando para %s (%s)...", name, phone)

        try:
            send_whatsapp_message(phone=phone, name=name)
            success_count += 1
        except requests.exceptions.HTTPError as exc:
            logger.error(
                "Erro HTTP ao enviar para %s (%s): %s",
                name,
                phone,
                exc.response.text,
            )
        except requests.exceptions.RequestException as exc:
            logger.error("Erro de conexão ao enviar para %s (%s): %s", name, phone, exc)

    logger.info(
        "=== Script finalizado. %d/%d mensagem(ns) enviada(s) com sucesso. ===",
        success_count,
        len(contacts),
    )


if __name__ == "__main__":
    main()

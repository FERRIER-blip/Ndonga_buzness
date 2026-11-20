import hashlib
import hmac
import logging
from typing import Optional

import httpx
from fastapi import APIRouter, Header, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import SessionLocal
from app.api.routes.chat import process_message, SESSIONS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

# Protection simple contre les re-livraisons durant la vie du processus.
# En production multi-instance, remplacer par une table d'événements persistante.
PROCESSED_MESSAGE_IDS: set[str] = set()


def verify_signature(raw_body: bytes, signature: Optional[str]) -> bool:
    if not settings.whatsapp_app_secret:
        # Permet les tests locaux sans App Secret. À renseigner impérativement en production.
        return settings.debug
    if not signature or not signature.startswith("sha256="):
        return False
    expected = hmac.new(
        settings.whatsapp_app_secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature.removeprefix("sha256="))


@router.get("/webhook", response_class=PlainTextResponse)
def verify_webhook(
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
):
    """Handshake Meta : renvoie le challenge uniquement si le jeton correspond."""
    if (
        hub_mode == "subscribe"
        and settings.whatsapp_verify_token
        and hub_verify_token == settings.whatsapp_verify_token
        and hub_challenge
    ):
        return PlainTextResponse(hub_challenge, status_code=200)
    raise HTTPException(status_code=403, detail="Vérification du webhook refusée")


async def send_text_message(to: str, body: str) -> dict:
    """Envoie un message texte via WhatsApp Cloud API."""
    if not settings.whatsapp_token or not settings.whatsapp_phone_number_id:
        raise RuntimeError("WhatsApp Cloud API n'est pas configurée dans backend/.env")
    url = (
        f"https://graph.facebook.com/{settings.whatsapp_api_version}/"
        f"{settings.whatsapp_phone_number_id}/messages"
    )
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": body[:4096]},
    }
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.is_error:
            logger.error("Erreur d'envoi WhatsApp %s : %s", response.status_code, response.text)
            response.raise_for_status()
        return response.json()


def extract_text_messages(payload: dict):
    """Itère uniquement sur les messages texte entrants."""
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for message in value.get("messages", []):
                if message.get("type") == "text":
                    yield message


@router.post("/webhook")
async def receive_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None, alias="X-Hub-Signature-256"),
):
    raw_body = await request.body()
    if not verify_signature(raw_body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Signature Meta invalide")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON invalide")

    if payload.get("object") != "whatsapp_business_account":
        return {"received": True, "ignored": True}

    processed = 0
    for message in extract_text_messages(payload):
        message_id = message.get("id")
        sender = str(message.get("from", "")).strip()
        text_body = message.get("text", {}).get("body", "").strip()
        if not sender or not text_body or not message_id:
            continue
        if message_id in PROCESSED_MESSAGE_IDS:
            continue

        db: Session = SessionLocal()
        try:
            session_id = f"wa-{sender}"
            result = process_message(session_id, text_body, db)

            # WhatsApp fournit déjà le numéro du client. Après la collecte du nom,
            # on finalise automatiquement l'étape téléphone avec le numéro expéditeur.
            state = SESSIONS.get(session_id, {})
            if state.get("stage") == "phone":
                result = process_message(session_id, sender, db)

            await send_text_message(sender, result.get("reply", "Je n'ai pas compris votre demande."))
            PROCESSED_MESSAGE_IDS.add(message_id)
            processed += 1
        except Exception as exc:
            logger.exception("Échec du traitement du message WhatsApp de %s", sender)
            raise HTTPException(status_code=502, detail="Échec du traitement du message WhatsApp") from exc
        finally:
            db.close()

    # Les événements de statut (sent/delivered/read) sont acceptés sans réponse.
    return {"received": True, "processed_messages": processed}

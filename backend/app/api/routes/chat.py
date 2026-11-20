import re
import unicodedata
from uuid import uuid4
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.entities import Product, Customer, Order, OrderItem

router = APIRouter(prefix="/chat", tags=["Assistant conversationnel"])
# Mémoire temporaire de session : suffisante pour les essais locaux. À remplacer
# par une persistance PostgreSQL/Redis avant déploiement multi-instance.
SESSIONS: dict[str, dict] = {}

class ChatMessage(BaseModel):
    session_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=1000)


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.lower())
    value = "".join(c for c in value if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", " ", value).strip()


def menu() -> str:
    return ("Bienvenue chez Ndonga_buzness ! 👋\n\n"
            "Que souhaitez-vous faire ?\n"
            "1️⃣ Voir les produits\n2️⃣ Consulter les tarifs\n"
            "3️⃣ Passer une commande\n4️⃣ Suivre une commande\n"
            "5️⃣ Parler à un conseiller\n\nVous pouvez aussi écrire votre demande avec vos propres mots.")


def product_list(db: Session) -> str:
    products = db.query(Product).filter(Product.active.is_(True)).order_by(Product.name).all()
    if not products:
        return "Notre catalogue est momentanément vide. Vous pouvez demander à parler à un conseiller."
    lines = ["Voici les produits disponibles :"]
    for p in products:
        stock = "Disponible" if p.stock > 0 else "Rupture de stock"
        lines.append(f"• {p.name} — {p.price:,.0f} FCFA ({stock})")
    lines.append("\nÉcrivez le nom d'un produit pour en savoir plus, ou COMMANDER pour acheter.")
    return "\n".join(lines)


@router.post("/simulate")
def simulate_chat(payload: ChatMessage, db: Session = Depends(get_db)):
    return process_message(payload.session_id, payload.message, db)


def process_message(session_id: str, raw_message: str, db: Session):
    sid = session_id
    message = raw_message.strip()
    normalized = normalize(message)
    state = SESSIONS.setdefault(sid, {"stage": None, "order": {}})

    # Conversation de commande guidée
    if state.get("stage") == "product":
        products = db.query(Product).filter(Product.active.is_(True)).all()
        product = next((p for p in products if normalize(p.name) in normalized or normalized in normalize(p.name)), None)
        if not product:
            return {"reply": "Je n'ai pas identifié ce produit. Écrivez son nom comme dans le catalogue, ou MENU pour revenir à l'accueil.", "session_id": sid}
        if product.stock <= 0:
            return {"reply": f"Désolé, {product.name} est actuellement en rupture de stock. Choisissez un autre produit.", "session_id": sid}
        state["order"] = {"product_id": product.id, "product_name": product.name}
        state["stage"] = "quantity"
        return {"reply": f"Très bien : {product.name} à {product.price:,.0f} FCFA. Quelle quantité souhaitez-vous ? (stock disponible : {product.stock})", "session_id": sid}

    if state.get("stage") == "quantity":
        match = re.search(r"\d+", message)
        if not match or int(match.group()) < 1:
            return {"reply": "Indiquez une quantité entière supérieure à zéro.", "session_id": sid}
        qty = int(match.group())
        product = db.get(Product, state["order"]["product_id"])
        if not product or qty > product.stock:
            return {"reply": f"La quantité demandée dépasse le stock disponible ({product.stock if product else 0}). Indiquez une autre quantité.", "session_id": sid}
        state["order"]["quantity"] = qty
        state["stage"] = "name"
        return {"reply": "Quel est votre nom complet pour enregistrer la commande ?", "session_id": sid}

    if state.get("stage") == "name":
        if len(message) < 2 or normalize(message) in {"menu", "annuler"}:
            state["stage"] = None
            return {"reply": "Commande annulée.\n\n" + menu(), "session_id": sid}
        state["order"]["customer_name"] = message
        state["stage"] = "phone"
        return {"reply": "Merci. Quel est votre numéro de téléphone avec indicatif pays (ex. +235XXXXXXXX) ?", "session_id": sid}

    if state.get("stage") == "phone":
        phone = re.sub(r"[\s().-]", "", message)
        if not re.fullmatch(r"\+?[0-9]{8,15}", phone):
            return {"reply": "Le numéro semble invalide. Saisissez 8 à 15 chiffres, avec éventuellement + au début.", "session_id": sid}
        order_data = state["order"]
        product = db.get(Product, order_data["product_id"])
        qty = order_data["quantity"]
        if not product or product.stock < qty:
            state["stage"] = None
            return {"reply": "Désolé, le stock vient de changer. Votre commande n'a pas été enregistrée. Écrivez COMMANDER pour recommencer.", "session_id": sid}
        customer = db.query(Customer).filter(Customer.phone == phone).first()
        if not customer:
            customer = Customer(name=order_data["customer_name"], phone=phone)
            db.add(customer); db.flush()
        else:
            customer.name = order_data["customer_name"]
        order = Order(order_number=f"NDG-{uuid4().hex[:8].upper()}", customer_id=customer.id, status="En attente", total=product.price * qty)
        order.items.append(OrderItem(product_id=product.id, quantity=qty, unit_price=product.price))
        product.stock -= qty
        db.add(order); db.commit(); db.refresh(order)
        state["stage"] = None; state["order"] = {}
        return {"reply": f"✅ Votre commande est enregistrée !\nNuméro : {order.order_number}\nProduit : {product.name}\nQuantité : {qty}\nTotal : {order.total:,.0f} FCFA\nStatut : En attente\n\nMerci pour votre confiance. Écrivez MENU pour continuer.", "session_id": sid, "order_number": order.order_number}

    # Intentions et réponses du menu
    if normalized in {"menu", "bonjour", "salut", "hello", "bonsoir", "bon matin", "start"} or any(x in normalized for x in ["bonjour", "bonsoir", "salut"]):
        reply = menu()
    elif normalized in {"1", "produit", "produits", "catalogue"} or any(x in normalized for x in ["voir les produits", "catalogue", "quels produits"]):
        reply = product_list(db)
    elif normalized in {"2", "prix", "tarif", "tarifs"} or any(x in normalized for x in ["combien", "prix", "tarif"]):
        reply = product_list(db)
    elif normalized in {"3", "commander", "commande", "acheter", "je veux commander"} or any(x in normalized for x in ["passer une commande", "je voudrais acheter", "je veux acheter"]):
        state["stage"] = "product"; state["order"] = {}
        reply = "Avec plaisir ! 😊 Quel produit souhaitez-vous commander ?\n\n" + product_list(db)
    elif normalized in {"4", "suivi", "suivre", "suivi commande"} or "suivre ma commande" in normalized:
        reply = "Envoyez votre numéro de commande (ex. NDG-AB12CD34) pour consulter son statut."
    elif re.fullmatch(r"ndg [a-z0-9]{6,12}", normalized):
        code = message.upper().replace(" ", "-")
        order = db.query(Order).filter(Order.order_number == code).first()
        reply = f"Commande {order.order_number} : {order.status}. Total : {order.total:,.0f} FCFA." if order else "Je ne trouve pas cette commande. Vérifiez le numéro et réessayez."
    elif normalized in {"5", "conseiller", "humain", "agent"} or any(x in normalized for x in ["parler a un conseiller", "service client", "personne reelle"]):
        reply = "Votre demande nécessite l'intervention d'un conseiller. Un membre de notre équipe pourra reprendre la conversation. (Le transfert humain sera connecté dans une prochaine étape.)"
    else:
        # Repli déterministe : recherche de produit avant la réponse générique.
        products = db.query(Product).filter(Product.active.is_(True)).all()
        found = next((p for p in products if normalize(p.name) in normalized and normalize(p.name)), None)
        if found:
            reply = f"{found.name}\n{found.description}\nPrix : {found.price:,.0f} FCFA\nStock : {found.stock}\n\nÉcrivez COMMANDER si vous souhaitez l'acheter."
        else:
            reply = ("Je peux vous aider pour les produits, les prix, les commandes et leur suivi. "
                     "Pouvez-vous préciser votre demande ?\n\n" + menu())
    return {"reply": reply, "session_id": sid}


@router.post("/reset")
def reset_chat(payload: ChatMessage):
    SESSIONS.pop(payload.session_id, None)
    return {"reply": menu(), "session_id": payload.session_id}

from sqlalchemy import or_
from database import get_db
from models import Client

def search_clients(query: str, master_id: int = None):
    db = next(get_db())
    search_query = db.query(Client)
    if master_id:
        search_query = search_query.filter(Client.master_id == master_id)
    results = search_query.filter(
        or_(
            Client.name.ilike(f"%{query}%"),
            Client.phone.ilike(f"%{query}%"),
            Client.kod_id.ilike(f"%{query}%")
        )
    ).all()
    db.close()
    return results

def get_client_by_kod_id(kod_id: str):
    db = next(get_db())
    client = db.query(Client).filter(Client.kod_id == kod_id).first()
    db.close()
    return client

def get_client_by_phone(phone: str):
    db = next(get_db())
    client = db.query(Client).filter(Client.phone == phone).first()
    db.close()
    return client

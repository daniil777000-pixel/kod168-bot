from datetime import datetime, timedelta
from sqlalchemy import func
from database import get_db
from models import Client, Visit, Master

def get_today_stats(master_id: int = None):
    db = next(get_db())
    today = datetime.utcnow().date()
    tomorrow = today + timedelta(days=1)
    filters = []
    if master_id:
        filters.append(Visit.master_id == master_id)
    visits_query = db.query(Visit).filter(
        Visit.date >= today,
        Visit.date < tomorrow,
        *filters
    )
    total_visits = visits_query.count()
    total_revenue = visits_query.with_entities(func.sum(Visit.price)).scalar() or 0
    new_clients = db.query(Client).filter(
        Client.created_at >= today,
        Client.created_at < tomorrow
    ).count()
    vip_count = db.query(Client).filter(Client.status == "vip").count()
    db.close()
    return {
        "today_visits": total_visits,
        "today_revenue": total_revenue,
        "new_clients": new_clients,
        "vip_count": vip_count
    }

def get_top_masters():
    db = next(get_db())
    month_ago = datetime.utcnow() - timedelta(days=30)
    results = db.query(
        Master.name,
        func.count(Visit.id).label("visits"),
        func.sum(Visit.price).label("revenue")
    ).join(Visit).filter(
        Visit.date >= month_ago
    ).group_by(Master.id).order_by(
        func.sum(Visit.price).desc()
    ).all()
    db.close()
    return results

def get_client_statistics(client_id: int):
    db = next(get_db())
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        return None
    stats = {
        "name": client.name,
        "kod_id": client.kod_id,
        "total_visits": client.visits_count,
        "total_spent": client.total_spent,
        "status": client.status,
        "last_visit": client.visits[-1].date if client.visits else None,
        "favorite_service": None,
        "avg_check": client.total_spent / client.visits_count if client.visits_count > 0 else 0
    }
    if client.visits:
        service_counts = {}
        for visit in client.visits:
            service_counts[visit.service] = service_counts.get(visit.service, 0) + 1
        stats["favorite_service"] = max(service_counts, key=service_counts.get)
    db.close()
    return stats

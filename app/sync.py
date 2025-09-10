from .db import SessionLocal, engine
from .models import Base, Character
from .rick_client import fetch_filtered_characters


# Ensure tables exist — in prod, use alembic migrations instead
Base.metadata.create_all(bind=engine)




def upsert_characters():
    chars = fetch_filtered_characters()
    session = SessionLocal()
    try:
        for c in chars:
            obj = session.query(Character).get(c['id'])
            if not obj:
                obj = Character(id=c['id'], name=c['name'])
            obj.name = c['name']
            obj.status = c.get('status')
            obj.species = c.get('species')
            obj.type = c.get('type')
            obj.gender = c.get('gender')
            obj.origin = (c.get('origin') or {}).get('name')
            obj.location = (c.get('location') or {}).get('name')
            obj.image = c.get('image')
            obj.raw = c
            session.merge(obj)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()




if __name__ == '__main__':
    upsert_characters()
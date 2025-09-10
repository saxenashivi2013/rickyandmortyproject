import requests
from app.db import SessionLocal
from app.models import Character

def fetch_characters():
    url = "https://rickandmortyapi.com/api/character"
    results = []
    while url:
        resp = requests.get(url)
        data = resp.json()
        results.extend(data["results"])
        url = data["info"]["next"]
    print(f"Fetched {len(results)} characters")  # <-- add this
    return results

def seed():
    session = SessionLocal()
    characters = fetch_characters()
    for char in characters:
        c = Character(
            id=char["id"],
            name=char["name"],
            status=char["status"],
            species=char["species"],
            type=char["type"],
            gender=char["gender"],
            origin=char["origin"]["name"],
            location=char["location"]["name"],
            image=char["image"],
            raw=char,
        )
        session.merge(c)
    session.commit()
    session.close()
    print("Seeding complete.")  # <-- add this

if __name__ == "__main__":
    seed()

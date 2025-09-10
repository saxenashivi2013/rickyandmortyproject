from flask import Flask, jsonify, request, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from .db import SessionLocal
from .models import Character
from .cache import get_cache, set_cache
from .config import RATE_LIMIT, PAGE_SIZE
import json
import structlog


logger = structlog.get_logger()


app = Flask(__name__)
limiter = Limiter(key_func=get_remote_address, default_limits=[RATE_LIMIT])


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/characters')
@limiter.limit(RATE_LIMIT)
def get_characters():
    # Query params: sort=name|id, order=asc|desc, page, per_page
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')
    page = int(request.args.get('page', '1'))
    per_page = int(request.args.get('per_page', PAGE_SIZE))


    if sort not in ('id', 'name'):
        return jsonify({'error': 'invalid sort field'}), 400
    if order not in ('asc', 'desc'):
        return jsonify({'error': 'invalid order'}), 400


    # simple cache key
    cache_key = f"chars:{sort}:{order}:{page}:{per_page}"
    cached = get_cache(cache_key)
    if cached:
        return jsonify(json.loads(cached))


    session = SessionLocal()
    try:
        q = session.query(Character)
        if sort == 'name':
            q = q.order_by(Character.name.asc() if order == 'asc' else Character.name.desc())
        else:
            q = q.order_by(Character.id.asc() if order == 'asc' else Character.id.desc())
        total = q.count()
        items = q.offset((page - 1) * per_page).limit(per_page).all()
        body = {
        'meta': {'page': page, 'per_page': per_page, 'total': total},
        'items': [dict(id=i.id, name=i.name, status=i.status, species=i.species, origin=i.origin, image=i.image) for i in items]
        }
        set_cache(cache_key, json.dumps(body), ex=30)
        return jsonify(body)
    finally:
        session.close()

@app.route('/healthcheck')
def healthcheck():
    # Deep healthcheck: DB and Redis
    status = {'db': False, 'cache': False}
    try:
        s = SessionLocal()
        s.execute('SELECT 1')
        status['db'] = True
    except Exception as e:
        logger.error('db-health-fail', error=str(e))
    finally:
        try:
            s.close()
        except Exception:
            pass


    try:
        from .cache import redis_client
        redis_client.ping()
        status['cache'] = True
    except Exception as e:
        logger.error('redis-health-fail', error=str(e)) 


    ok = all(status.values())
    return jsonify({'ok': ok, 'checks': status}), (200 if ok else 503)




@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}




@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error='rate limit exceeded'), 429




@app.errorhandler(500)
def internal_error(e):
    return jsonify(error='internal error'), 503


@app.route("/ui/characters")
def characters_ui():
    """Renders the UI table that fetches /characters JSON."""
    return render_template("characters.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
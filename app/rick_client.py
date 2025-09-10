import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .config import RICK_API_BASE


client = httpx.Client(timeout=10)


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=10), retry=retry_if_exception_type(httpx.TransportError))
def fetch_characters_page(page: int = 1, params: dict = None):
	params = params or {}
	params.update({'page': page})
	url = f"{RICK_API_BASE}/character"
	r = client.get(url, params=params)
	if r.status_code == 429:
		# raise to let tenacity backoff or caller handle
		raise httpx.HTTPStatusError("rate limited", request=r.request, response=r)
	r.raise_for_status()
	return r.json()




def fetch_filtered_characters():
	# We will ask the API for species=Human&status=Alive and then filter origin locally for 'Earth' variants
	params = {'species': 'Human', 'status': 'Alive'}
	page = 1
	out = []
	while True:
		data = fetch_characters_page(page, params=params)
		results = data.get('results', [])
		for char in results:
			origin_name = (char.get('origin') or {}).get('name', '')
			if origin_name and 'Earth' in origin_name:
				out.append(char)
		info = data.get('info') or {}
		if not info.get('next'):
			break
		page += 1
	return out

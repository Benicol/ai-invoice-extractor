class Response:
    _json: str
    _total_excluding_vat: float | None
    _total_vat: float | None
    _total_including_vat: float | None
    _date: str | None
    _supplier: str | None

    def __init__(self, json: str):
        self._json = json.replace('```json', '').replace('```', '').strip()

    def __str__(self):
        return self._json

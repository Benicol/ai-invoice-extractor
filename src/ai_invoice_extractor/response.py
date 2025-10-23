import json

class Response:
    _json: str
    _total_excluding_vat: float | None
    _total_vat: float | None
    _total_including_vat: float | None
    _date: str | None
    _supplier: str | None

    def __init__(self, json_data: str):
        self._json = json_data.replace('```json', '').replace('```', '').strip()

    def __str__(self):
        return self._json

    def deserialize(self) -> Response:
        try:
            response = json.loads(self._json)
            self._total_excluding_vat = response.get('total_excluding_vat')
            self._total_vat = response.get('total_vat')
            self._total_including_vat = response.get('total_including_vat')
            self._date = response.get('date')
            self._supplier = response.get('supplier')
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to deserialize JSON response: {str(e)}") from e
        return self

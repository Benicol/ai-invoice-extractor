from . import Ticket
from .response import Response
from ollama import chat, ChatResponse
from .prompts import invoice_prompt

class AiRequester:
    _ticket: Ticket
    _model: str
    _answer: str

    def __init__(self, ticket: Ticket, model: str = "qwen2.5vl:7b"):
        self._ticket = ticket
        self._model = model

    @property
    def ticket(self) -> Ticket:
        return self._ticket

    @ticket.setter
    def ticket(self, value: Ticket):
        self._ticket = value
        del self._answer

    def request(self) -> Response:
        prompt = f"{invoice_prompt}"

        response: ChatResponse = chat(
            model=self._model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [self._ticket.get_png_data()],
                }
            ]
        )
        return Response(response['message']['content'])


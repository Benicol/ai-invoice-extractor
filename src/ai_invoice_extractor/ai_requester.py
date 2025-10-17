from . import Ticket
from .response import Response
from ollama import chat, ChatResponse
from .prompts import invoice_prompt

class AiRequester:
    _ticket: Ticket
    _answer: str

    def __init__(self, ticket: Ticket):
        self._ticket = ticket

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
            model="qwen2.5vl",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [self._ticket.get_png_data()],
                }
            ]
        )
        return Response(response['message']['content'])


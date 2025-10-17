from ai_invoice_extractor import AiRequester, Ticket
from pytest import fixture

@fixture
def ticket():
    ticket = Ticket("test_data/pdf/invoice-test-1.pdf")
    return ticket

def test_ai_requester(ticket):
    requester = AiRequester(ticket)
    print(requester.request())
import os
from pytest import fixture, raises
from ai_invoice_extractor import Ticket

@fixture
def ticket():
    ticket = Ticket("test_data/pdf/invoice-test-1.pdf")
    return ticket

def test_ticket_init():
    ticket = Ticket("test_data/pdf/invoice-test-1.pdf")
    assert ticket.pdf_path == "test_data/invoice-test-1.pdf"
    assert not hasattr(ticket, '_png_path')

def test_ticket_init_file_not_found():
    with raises(FileNotFoundError):
        Ticket("test_data/nonexistent.pdf")

def test_ticket_pdf_path_setter(ticket):
    ticket.pdf_path = "test_data/pdf/invoice-test-1.pdf"
    assert ticket.pdf_path == "test_data/invoice-test-1.pdf"

def test_ticket_pdf_path_setter_file_not_found(ticket):
    with raises(FileNotFoundError):
        ticket.pdf_path = "test_data/nonexistent.pdf"

def test_ticket_multi_page():
    with raises(Exception):
        _ = Ticket("test_data/multi-page.pdf")

def test_ticket2png(ticket):
    png_data = ticket.get_png_data()
    assert isinstance(png_data, bytes)
    assert png_data.startswith(b'\x89PNG\r\n\x1a\n')  # PNG file signature
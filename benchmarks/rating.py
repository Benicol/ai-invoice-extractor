"""Interactive rating functionality for benchmark responses."""

from typing import Any

from ai_invoice_extractor import Response

from ._utils import ask_int_in_range, values_equal
from .config import EXPECTED_RESULTS


def rate_response(response: Response, pdf_file: str) -> float:
    """Display response and request user rating.

    Behavior:
    - If deserialization fails, returns 0.0 immediately
    - For each field, compares expected vs actual value
    - If they match, automatically awards full points for that field
    - If they don't match, asks user to rate the field
    - Returns total score out of 100

    Scoring breakdown:
    - total_excluding_vat: 0-15 points
    - total_vat: 0-15 points
    - total_including_vat: 0-15 points
    - date: 0-25 points
    - supplier: 0-30 points

    Args:
        response: AI response object to rate
        pdf_file: PDF filename being evaluated

    Returns:
        Rating from 0.0 to 100.0
    """
    print(response)

    # Try to deserialize - if it fails, format is not OK -> score 0
    try:
        response.deserialize()
    except Exception as e:
        print(f"Deserialization error: {e}")
        return 0.0

    def get_attr(obj: Any, name: str) -> Any:
        """Safely get attribute from object."""
        return getattr(obj, name, None)

    total_grade = 0

    # Get expected values for this file
    expected = EXPECTED_RESULTS.get(pdf_file, {})

    # Rate total_excluding_vat (0-15)
    exp = expected.get('total_excluding_vat')
    got = get_attr(response, '_total_excluding_vat')
    if values_equal(exp, got):
        print(f"Expected == Got for total_excluding_vat ({exp}) -> awarding full 15 points")
        total_grade += 15
    else:
        print("Rate total_excluding_vat:")
        total_grade += ask_int_in_range(
            f"Expected: {exp}, Got: {got}. Rate 0-15: ", 0, 15
        )

    # Rate total_vat (0-15)
    exp = expected.get('total_vat')
    got = get_attr(response, '_total_vat')
    if values_equal(exp, got):
        print(f"Expected == Got for total_vat ({exp}) -> awarding full 15 points")
        total_grade += 15
    else:
        print("Rate total_vat:")
        total_grade += ask_int_in_range(
            f"Expected: {exp}, Got: {got}. Rate 0-15: ", 0, 15
        )

    # Rate total_including_vat (0-15)
    exp = expected.get('total_including_vat')
    got = get_attr(response, '_total_including_vat')
    if values_equal(exp, got):
        print(f"Expected == Got for total_including_vat ({exp}) -> awarding full 15 points")
        total_grade += 15
    else:
        print("Rate total_including_vat:")
        total_grade += ask_int_in_range(
            f"Expected: {exp}, Got: {got}. Rate 0-15: ", 0, 15
        )

    # Rate date (0-25)
    exp = expected.get('date')
    got = get_attr(response, '_date')
    if values_equal(exp, got):
        print(f"Expected == Got for date ({exp}) -> awarding full 25 points")
        total_grade += 25
    else:
        print("Rate date:")
        total_grade += ask_int_in_range(
            f"Expected: {exp}, Got: {got}. Rate 0-25: ", 0, 25
        )

    # Rate supplier (0-30)
    exp = expected.get('supplier')
    got = get_attr(response, '_supplier')
    if values_equal(exp, got):
        print(f"Expected == Got for supplier ({exp}) -> awarding full 30 points")
        total_grade += 30
    else:
        print("Rate supplier:")
        total_grade += ask_int_in_range(
            f"Expected: {exp}, Got: {got}. Rate 0-30: ", 0, 30
        )

    print(f"Total grade: {total_grade}/100")
    return float(total_grade)

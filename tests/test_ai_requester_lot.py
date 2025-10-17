import os
import time
import json
from ai_invoice_extractor import Ticket, AiRequester


def _next_batch_folder(base_dir: str) -> str:
    """Return path to a new numeric folder inside base_dir numbered 1..inf.

    If there are no numeric subfolders, create '1'. Otherwise create folder with max+1.
    Returns the created folder path.
    """
    os.makedirs(base_dir, exist_ok=True)
    # find numeric folders
    nums = []
    for name in os.listdir(base_dir):
        path = os.path.join(base_dir, name)
        if os.path.isdir(path) and name.isdigit():
            try:
                nums.append(int(name))
            except ValueError:
                pass
    next_num = 1 if not nums else max(nums) + 1
    new_folder = os.path.join(base_dir, str(next_num))
    os.makedirs(new_folder, exist_ok=True)
    return new_folder


def _format_elapsed(seconds_float: float, sep: str = '-') -> str:
    """Format elapsed seconds as MM<sep>SS. sep=':' for display, sep='-' for filenames."""
    total = int(seconds_float)
    mm = total // 60
    ss = total % 60
    return f"{mm:02d}{sep}{ss:02d}"


def test_batch_invoice_to_json():
    """Batch test that converts PDFs to Ticket, sends to AiRequester and writes responses.

    This test intentionally writes output files under tests/test_data/json_batches/<n>.
    Each output filename: <pdf-basename>__<model>__<mm-ss>.json and content is str(response).
    """
    root = os.path.dirname(__file__)
    pdf_dir = os.path.join(root, 'test_data', 'pdf')
    batches_base = os.path.join(root, 'test_data', 'json_batches')

    # create next numbered batch folder
    out_dir = _next_batch_folder(batches_base)

    model_name = "qwen2.5vl"

    assert os.path.isdir(pdf_dir), f"PDF dir not found: {pdf_dir}"

    files = sorted([f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')])
    total = len(files)
    assert total > 0, f"No PDF files found in {pdf_dir}"

    cumulative_elapsed = 0.0

    for idx, filename in enumerate(files, start=1):
        pdf_path = os.path.join(pdf_dir, filename)
        ticket = Ticket(pdf_path)
        requester = AiRequester(ticket)

        print(f"Processing [{idx}/{total}] {filename}...")
        start = time.perf_counter()
        try:
            response = requester.request()
        except Exception as e:
            # Record the exception text as response so the test output contains useful info.
            response = str(e)
        end = time.perf_counter()

        elapsed = end - start
        cumulative_elapsed += elapsed
        avg = cumulative_elapsed / idx
        remaining = avg * (total - idx)

        # format for filename (safe) and for display (readable)
        elapsed_str_filename = _format_elapsed(elapsed, sep='-')
        remaining_str_filename = _format_elapsed(remaining, sep='-')
        elapsed_str_display = _format_elapsed(elapsed, sep=':')
        remaining_str_display = _format_elapsed(remaining, sep=':')

        base_name = os.path.splitext(filename)[0]
        json_filename = f"{base_name}__{model_name}__{elapsed_str_filename}.json"
        json_path = os.path.join(out_dir, json_filename)

        # write the string form of the Response (do not modify Response class)
        content = str(response)
        # write raw content directly (user requested no json wrapper)
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write(content)

        percent = (idx / total) * 100
        print(f"Done [{idx}/{total}] {filename} — took {elapsed_str_display}, ETA {remaining_str_display} — {percent:.1f}%")
        print(f"Wrote {json_path}\n")

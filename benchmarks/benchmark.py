"""Main benchmark functions for AI invoice extractor.

This module provides various benchmarking capabilities:
- Simple batch processing with timing
- Model evaluation with interactive rating
- Threaded evaluation for concurrent processing
"""

import os
import queue
import threading
import time
from pathlib import Path

from ai_invoice_extractor import AiRequester, Response, Ticket

from ._utils import format_elapsed, next_batch_folder
from .config import MODELS
from .metrics import Metrics, load_processed_set
from .rating import rate_response


class RatingRequest:
    """Container for a response that needs to be rated."""

    def __init__(
        self,
        response: Response,
        pdf_file: str,
        model: dict,
        elapsed: float
    ):
        """Initialize rating request.

        Args:
            response: AI response to rate
            pdf_file: PDF filename that was processed
            model: Model configuration dict
            elapsed: Time taken in seconds
        """
        self.response = response
        self.pdf_file = pdf_file
        self.model = model
        self.elapsed = elapsed


def benchmark_batch(
    model_name: str = "qwen2.5vl",
    pdf_dir: str | None = None,
    output_dir: str | None = None
) -> None:
    """Run simple batch benchmark converting PDFs to JSON with timing.

    This writes output files under tests/test_data/json_batches/<n>/.
    Each output filename: <pdf-basename>__<model>__<mm-ss>.json

    Args:
        model_name: Name of the AI model to use
        pdf_dir: Directory containing PDF files. If None, uses tests/test_data/pdf
        output_dir: Base directory for outputs. If None, uses tests/test_data/json_batches
    """
    if pdf_dir is None:
        root = Path(__file__).parent.parent / 'tests'
        pdf_dir = str(root / 'test_data' / 'pdf')

    if output_dir is None:
        root = Path(__file__).parent.parent / 'tests'
        output_dir = str(root / 'test_data' / 'json_batches')

    # Create next numbered batch folder
    out_dir = next_batch_folder(output_dir)

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
            response = str(e)
        end = time.perf_counter()

        elapsed = end - start
        cumulative_elapsed += elapsed
        avg = cumulative_elapsed / idx
        remaining = avg * (total - idx)

        # Format for filename and display
        elapsed_str_filename = format_elapsed(elapsed, sep='-')
        elapsed_str_display = format_elapsed(elapsed, sep=':')
        remaining_str_display = format_elapsed(remaining, sep=':')

        base_name = os.path.splitext(filename)[0]
        json_filename = f"{base_name}__{model_name}__{elapsed_str_filename}.json"
        json_path = os.path.join(out_dir, json_filename)

        # Write the string form of the Response
        content = str(response)
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write(content)

        percent = (idx / total) * 100
        print(
            f"Done [{idx}/{total}] {filename} — took {elapsed_str_display}, "
            f"ETA {remaining_str_display} — {percent:.1f}%"
        )
        print(f"Wrote {json_path}\n")


def benchmark_with_rating(
    pdf_dir: str | None = None,
    output_dir: str | None = None
) -> None:
    """Run interactive benchmark that evaluates all models with user ratings.

    For each PDF file, asks user if they want to proceed, then runs all models
    and collects ratings. Writes metrics to CSV.

    Args:
        pdf_dir: Directory containing PDF files. If None, uses tests/test_data/pdf
        output_dir: Base directory for outputs. If None, uses tests/test_data/json_batches
    """
    if pdf_dir is None:
        root = Path(__file__).parent.parent / 'tests'
        pdf_dir = str(root / 'test_data' / 'pdf')

    if output_dir is None:
        root = Path(__file__).parent.parent / 'tests'
        output_dir = str(root / 'test_data' / 'json_batches')

    # Create next numbered batch folder
    out_dir = next_batch_folder(output_dir)

    files = sorted([f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')])
    metrics = Metrics()

    for i, file in enumerate(files, start=1):
        print(f"{i}/{len(files)}", file)
        if input("Do you want to proceed? (y/n): ").lower() == 'y':
            pdf_path = os.path.join(pdf_dir, file)
            ticket = Ticket(pdf_path)

            for model in MODELS:
                print(
                    f"Evaluating model: {model['name']} with {model['parameters']}B "
                    f"parameters and size {model['size']}GB"
                )
                requester = AiRequester(
                    ticket,
                    model=f"{model['name']}:{model['parameters']}b"
                )

                start = time.perf_counter()
                try:
                    response = requester.request()
                except Exception as e:
                    response = str(e)
                end = time.perf_counter()

                elapsed = end - start
                elapsed_str_display = format_elapsed(elapsed, sep=':')

                base_name = os.path.splitext(file)[0]
                elapsed_fmt = format_elapsed(elapsed, sep='-')
                json_filename = f"{base_name}__{model['name']}__{elapsed_fmt}.json"
                json_path = os.path.join(out_dir, json_filename)

                with open(json_path, 'w', encoding='utf-8') as f:
                    f.write(str(response))

                print(file)
                user_rating = rate_response(response, file)
                metrics.add(
                    model['name'],
                    model['parameters'],
                    model['size'],
                    file,
                    elapsed,
                    user_rating
                )
                print(
                    f"Model {model['name']} processed in {elapsed_str_display}. "
                    f"Output written to {json_path}\n"
                )

    csv_path = os.path.join(out_dir, 'metrics.csv')
    metrics.to_csv(csv_path)
    print(f"Metrics written to {csv_path}")


def _ai_worker(
    pdf_files: list[str],
    models: list[dict],
    rating_queue: queue.Queue,
    pdf_dir: str,
    output_dir: str,
    processed_set: set | None = None
) -> None:
    """Worker thread that generates AI responses and queues them for rating.

    Args:
        pdf_files: List of PDF filenames to process
        models: List of model configurations
        rating_queue: Queue to put rating requests into
        pdf_dir: Directory containing PDF files
        output_dir: Base directory for output files
        processed_set: Set of (pdf_file, model_name, model_params) tuples
                      already processed (to skip)
    """
    out_dir = next_batch_folder(output_dir)

    for file in pdf_files:
        pdf_path = os.path.join(pdf_dir, file)
        ticket = Ticket(pdf_path)

        for model in models:
            key = (file, model['name'], str(model['parameters']))
            if processed_set and key in processed_set:
                print(
                    f"Skipping already processed: {file} | "
                    f"{model['name']}:{model['parameters']}b"
                )
                continue

            requester = AiRequester(
                ticket,
                model=f"{model['name']}:{model['parameters']}b"
            )

            start = time.perf_counter()
            try:
                response = requester.request()
            except Exception as e:
                response = str(e)
            end = time.perf_counter()

            elapsed = end - start

            # Save response
            base_name = os.path.splitext(file)[0]
            json_filename = (
                f"{base_name}__{model['name']}__{model['parameters']}b__"
                f"{int(elapsed)}s.json"
            )
            json_path = os.path.join(out_dir, json_filename)
            with open(json_path, 'w', encoding='utf-8') as f:
                f.write(str(response))

            # Add to rating queue
            rating_queue.put(RatingRequest(response, file, model, elapsed))

    # Signal completion
    rating_queue.put(None)


def _rating_loop(rating_queue: queue.Queue, metrics: Metrics) -> None:
    """Main thread loop that rates responses as they become available.

    Args:
        rating_queue: Queue to get rating requests from
        metrics: Metrics object to record ratings
    """
    while True:
        try:
            req = rating_queue.get(timeout=1)
        except queue.Empty:
            print("No responses to rate at the moment. Waiting...")
            time.sleep(1)
            continue

        # Check for sentinel signaling worker completion
        if req is None:
            print("Worker completed and sent completion signal. Ending rating loop.")
            break

        print(
            f"\nTo rate: {req.pdf_file} | Model: {req.model['name']} "
            f"({req.model['parameters']}B)"
        )
        user_rating = rate_response(req.response, req.pdf_file)
        metrics.add(
            req.model['name'],
            req.model['parameters'],
            req.model['size'],
            req.pdf_file,
            req.elapsed,
            user_rating
        )
        print(
            f"Rated {req.pdf_file} for model {req.model['name']}: "
            f"{user_rating}/100\n"
        )


def benchmark_threaded(
    start_file: str | None = None,
    start_index: int | None = None,
    pdf_dir: str | None = None,
    output_dir: str | None = None
) -> None:
    """Run threaded benchmark with concurrent AI processing and rating.

    This version runs AI inference in a background thread while the main thread
    handles interactive rating. Supports resuming from a specific file.

    Args:
        start_file: Filename to start from (e.g., "invoice-test-5.pdf")
        start_index: 1-based index to start from
        pdf_dir: Directory containing PDF files. If None, uses tests/test_data/pdf
        output_dir: Base directory for outputs. If None, uses tests/test_data/json_batches
    """
    if pdf_dir is None:
        root = Path(__file__).parent.parent / 'tests'
        pdf_dir = str(root / 'test_data' / 'pdf')

    if output_dir is None:
        root = Path(__file__).parent.parent / 'tests'
        output_dir = str(root / 'test_data' / 'json_batches')

    files = sorted([f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')])

    # Support starting at a specific invoice
    if start_file:
        if start_file in files:
            idx0 = files.index(start_file)
            files = files[idx0:]
            print(f"Starting from requested file: {start_file} (index {idx0+1})")
        else:
            print(
                f"Start file {start_file} not found in {pdf_dir}. "
                f"Starting from beginning."
            )
    elif start_index:
        if start_index < 1:
            print("Start index must be >= 1. Starting from beginning.")
        elif start_index > len(files):
            print(
                f"Start index {start_index} exceeds file count ({len(files)}). "
                f"Starting from beginning."
            )
        else:
            files = files[start_index-1:]
            print(f"Starting from index {start_index} -> file {files[0]}")

    metrics = Metrics()

    # Load processed set to skip already done items
    processed_set = load_processed_set(metrics.csv_path)
    if processed_set:
        print(
            f"Loaded {len(processed_set)} already-processed entries from "
            f"{metrics.csv_path}"
        )

    rating_queue = queue.Queue()

    # Start worker thread
    worker = threading.Thread(
        target=_ai_worker,
        args=(files, MODELS, rating_queue, pdf_dir, output_dir, processed_set),
        daemon=True
    )
    worker.start()

    # Run rating loop in main thread
    _rating_loop(rating_queue, metrics)

    # Save final metrics
    out_dir = next_batch_folder(output_dir)
    csv_path = os.path.join(out_dir, 'metrics.csv')
    metrics.to_csv(csv_path)
    print(f"Metrics written to {csv_path}")

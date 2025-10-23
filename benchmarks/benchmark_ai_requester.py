"""Benchmark script for AI invoice extraction performance.

This benchmark processes a batch of PDF invoices and measures the performance
of the AI requester. It generates JSON output with timing information for each
processed invoice.
"""

import os
import time

from ai_invoice_extractor import AiRequester, Ticket

# Configuration
MODEL_NAME = "qwen2.5vl"
PDF_INPUT_DIR = "test_data/pdf"
OUTPUT_BASE_DIR = "test_data/json_batches"


def get_next_batch_folder(base_dir: str) -> str:
    """Return path to a new numeric folder inside base_dir numbered 1..inf.

    If there are no numeric subfolders, create '1'. Otherwise create folder with max+1.

    Args:
        base_dir: Base directory path where numbered folders will be created

    Returns:
        Path to the newly created numbered folder
    """
    os.makedirs(base_dir, exist_ok=True)

    # Find existing numeric folders
    numeric_folders = []
    for name in os.listdir(base_dir):
        path = os.path.join(base_dir, name)
        if os.path.isdir(path) and name.isdigit():
            try:
                numeric_folders.append(int(name))
            except ValueError:
                pass

    next_num = 1 if not numeric_folders else max(numeric_folders) + 1
    new_folder = os.path.join(base_dir, str(next_num))
    os.makedirs(new_folder, exist_ok=True)
    return new_folder


def format_time(seconds: float, separator: str = "-") -> str:
    """Format elapsed seconds as MM<sep>SS.

    Args:
        seconds: Time in seconds to format
        separator: Character to use between minutes and seconds
                  (':' for display, '-' for filenames)

    Returns:
        Formatted time string as MM<sep>SS
    """
    total = int(seconds)
    minutes = total // 60
    secs = total % 60
    return f"{minutes:02d}{separator}{secs:02d}"


def benchmark_batch_processing():
    """Run batch benchmark: convert PDFs to tickets and process with AI requester.

    This benchmark processes all PDF files in the configured input directory,
    sends them to the AI requester, and writes responses to JSON files.
    Each output filename includes: <pdf-basename>__<model>__<mm-ss>.json
    Output files are written to a numbered batch folder under OUTPUT_BASE_DIR.
    """
    # Setup paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    pdf_dir = os.path.join(project_root, "tests", PDF_INPUT_DIR)
    batches_base = os.path.join(project_root, "tests", OUTPUT_BASE_DIR)

    # Validate input directory
    assert os.path.isdir(pdf_dir), f"PDF directory not found: {pdf_dir}"

    # Create output directory for this batch
    output_dir = get_next_batch_folder(batches_base)

    # Get list of PDF files to process
    pdf_files = sorted([f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")])
    total_files = len(pdf_files)
    assert total_files > 0, f"No PDF files found in {pdf_dir}"

    print(f"Starting benchmark: {total_files} files to process")
    print(f"Model: {MODEL_NAME}")
    print(f"Output directory: {output_dir}\n")

    # Process each PDF file
    cumulative_time = 0.0

    for idx, filename in enumerate(pdf_files, start=1):
        pdf_path = os.path.join(pdf_dir, filename)

        # Create ticket and requester
        ticket = Ticket(pdf_path)
        requester = AiRequester(ticket)

        print(f"Processing [{idx}/{total_files}] {filename}...")

        # Measure processing time
        start_time = time.perf_counter()
        try:
            response = requester.request()
        except Exception as e:
            # Record exception as response for debugging
            response = str(e)
        end_time = time.perf_counter()

        # Calculate timing statistics
        elapsed = end_time - start_time
        cumulative_time += elapsed
        avg_time = cumulative_time / idx
        remaining_time = avg_time * (total_files - idx)

        # Format times for filename and display
        elapsed_filename = format_time(elapsed, separator="-")
        remaining_display = format_time(remaining_time, separator=":")
        elapsed_display = format_time(elapsed, separator=":")

        # Generate output filename and save response
        base_name = os.path.splitext(filename)[0]
        json_filename = f"{base_name}__{MODEL_NAME}__{elapsed_filename}.json"
        json_path = os.path.join(output_dir, json_filename)

        with open(json_path, "w", encoding="utf-8") as f:
            f.write(str(response))

        # Print progress
        progress_pct = (idx / total_files) * 100
        print(
            f"Done [{idx}/{total_files}] {filename} — took {elapsed_display}, "
            f"ETA {remaining_display} — {progress_pct:.1f}%"
        )
        print(f"Wrote {json_path}\n")

    # Print summary
    print("\n" + "=" * 60)
    print("Benchmark Complete!")
    print(f"Total files processed: {total_files}")
    print(f"Total time: {format_time(cumulative_time, separator=':')}")
    print(f"Average time per file: {format_time(cumulative_time / total_files, separator=':')}")
    print(f"Output directory: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    benchmark_batch_processing()

# Benchmarks

This directory contains benchmark scripts for measuring AI invoice extraction performance.

## Available Benchmarks

### benchmark_ai_requester.py

Batch processing benchmark that:
- Processes all PDF invoices in `tests/test_data/pdf/`
- Measures processing time for each invoice
- Generates JSON output files with timing information
- Calculates average processing time and ETA

**Usage:**
```bash
python benchmarks/benchmark_ai_requester.py
```

**Output:**
- Creates numbered batch folders in `tests/test_data/json_batches/`
- Each JSON file is named: `<pdf-name>__<model>__<MM-SS>.json`
- Contains the AI response for each invoice

## Requirements

- Ollama must be running locally
- The `qwen2.5vl` model must be available in Ollama
- PDF files must be present in `tests/test_data/pdf/`

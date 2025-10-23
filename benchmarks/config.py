"""Configuration data for AI invoice extractor benchmarks."""

# Model configurations for benchmarking
MODELS = [
    {
        "name": "qwen2.5vl",
        "parameters": 3,
        "size": 3.2
    },
    {
        "name": "qwen2.5vl",
        "parameters": 7,
        "size": 6.0
    },
    {
        "name": "granite3.2-vision",
        "parameters": 2,
        "size": 2.4
    },
    {
        "name": "qwen2.5vl",
        "parameters": 32,
        "size": 21.0
    },
    {
        "name": "mistral-small3.2",
        "parameters": 24,
        "size": 15.0
    }
]

# Expected values for test invoices
EXPECTED_RESULTS = {
    "invoice-test-1.pdf": {
        "total_excluding_vat": 62.52,
        "total_vat": 12.50,
        "total_including_vat": 75.02,
        "date": "26/08/2025",
        "supplier": "Station Mairie ARVIEU"
    },
    "invoice-test-2.pdf": {
        "total_excluding_vat": 62.52,
        "total_vat": 12.50,
        "total_including_vat": 75.02,
        "date": "26/08/2025",
        "supplier": "Station Mairie ARVIEU"
    },
    "invoice-test-3.pdf": {
        "total_excluding_vat": 62.52,
        "total_vat": 12.50,
        "total_including_vat": 75.02,
        "date": "26/08/2025",
        "supplier": "Station Mairie ARVIEU"
    },
    "invoice-test-4.pdf": {
        "total_excluding_vat": 23.38,
        "total_vat": 4.68,
        "total_including_vat": 28.06,
        "date": "27/08/2025",
        "supplier": "SARL GARAGE MONTEILLET"
    },
    "invoice-test-5.pdf": {
        "total_excluding_vat": 28.18,
        "total_vat": 2.82,
        "total_including_vat": 31.00,
        "date": "03/07/2025",
        "supplier": "Restaurant L'atelier"
    },
    "invoice-test-6.pdf": {
        "total_excluding_vat": None,
        "total_vat": None,
        "total_including_vat": None,
        "date": None,
        "supplier": None
    },
    "invoice-test-7.pdf": {
        "total_excluding_vat": 32.98,
        "total_vat": 6.60,
        "total_including_vat": 39.57,
        "date": "04/07/2025",
        "supplier": "BRICO DEPOT"
    },
    "invoice-test-8.pdf": {
        "total_excluding_vat": 32.98,
        "total_vat": 6.60,
        "total_including_vat": 39.57,
        "date": "04/07/2025",
        "supplier": "Brico Dépôt S.A.S."
    },
    "invoice-test-9.pdf": {
        "total_excluding_vat": None,
        "total_vat": None,
        "total_including_vat": 56.80,
        "date": "04/07/2025",
        "supplier": "CREDIT AGRICOLE"
    },
    "invoice-test-10.pdf": {
        "total_excluding_vat": None,
        "total_vat": None,
        "total_including_vat": 12.25,
        "date": "03/07/2025",
        "supplier": "MALRIEU SA"
    },
    "invoice-test-11.pdf": {
        "total_excluding_vat": 10.21,
        "total_vat": 2.04,
        "total_including_vat": 12.25,
        "date": "03/07/2025",
        "supplier": "MALRIEU DISTRIBUTION SAS"
    },
    "invoice-test-12.pdf": {
        "total_excluding_vat": 10.21,
        "total_vat": 2.04,
        "total_including_vat": 12.25,
        "date": "03/07/2025",
        "supplier": "MALRIEU DISTRIBUTION SAS"
    }
}

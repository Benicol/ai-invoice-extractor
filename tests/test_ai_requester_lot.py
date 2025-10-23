import os
import time
import threading
import queue
from ai_invoice_extractor import Ticket, AiRequester, Response

models = [
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
supposed = {
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

class Metrics:
    def __init__(self, csv_path: str | None = None):
        import os
        import csv
        self.data = []
        if csv_path is None:
            # default progress CSV inside tests/test_data/json_batches
            csv_dir = os.path.join(os.path.dirname(__file__), 'test_data', 'json_batches')
            os.makedirs(csv_dir, exist_ok=True)
            csv_path = os.path.join(csv_dir, 'metrics_progress.csv')
        self.csv_path = csv_path
        # initialize CSV with header only if file does not exist (do not overwrite existing progress)
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                dict_writer = csv.DictWriter(f, fieldnames=[
                    'model_name', 'model_parameters', 'model_size', 'pdf_file', 'elapsed_time_seconds', 'user_rating_percentage'
                ])
                dict_writer.writeheader()

    def add(self, model_name, model_params, model_size, pdf_file, elapsed, user_rating_percentage):
        row = {
            "model_name": model_name,
            "model_parameters": model_params,
            "model_size": model_size,
            "pdf_file": pdf_file,
            "elapsed_time_seconds": elapsed,
            "user_rating_percentage": user_rating_percentage
        }
        self.data.append(row)
        # append the new row immediately to the CSV for crash-safe persistence
        import csv
        with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=row.keys())
            dict_writer.writerow(row)

    def to_csv(self, csv_path):
        import csv
        keys = self.data[0].keys() if self.data else []
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.data)


# helper: load processed rows from existing progress CSV (returns set of tuples)
def load_processed_set(csv_path: str) -> set:
    import os
    import csv
    processed = set()
    if not os.path.exists(csv_path):
        return processed
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                # Use (pdf_file, model_name, model_parameters) as identity
                processed.add((r.get('pdf_file'), r.get('model_name'), r.get('model_parameters')))
    except Exception:
        # If CSV is corrupted or unreadable, treat as empty
        return set()
    return processed


def test_evaluate_models_capabilities():
    root = os.path.dirname(__file__)
    pdf_dir = os.path.join(root, 'test_data', 'pdf')
    batches_base = os.path.join(root, 'test_data', 'json_batches')

    # create next numbered batch folder
    out_dir = _next_batch_folder(batches_base)

    files = sorted([f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')])
    i = 1
    metrics = Metrics()
    for file in files:
        print(f"{i}/{len(files)}", file)
        i += 1
        if input("Do you want to proceed ? (y/n): ").lower() == 'y':
            pdf_path = os.path.join(pdf_dir, file)
            ticket = Ticket(pdf_path)
            for model in models:
                print(f"Evaluating model: {model['name']} with {model['parameters']}B parameters and size {model['size']}GB")
                requester = AiRequester(ticket, model=f"{model['name']}:{model['parameters']}b")
                start = time.perf_counter()
                try:
                    response = requester.request()
                except Exception as e:
                    response = str(e)
                end = time.perf_counter()
                elapsed = end - start
                elapsed_str_display = _format_elapsed(elapsed, sep=':')
                base_name = os.path.splitext(file)[0]
                json_filename = f"{base_name}__{model['name']}__{_format_elapsed(elapsed, sep='-')}.json"
                json_path = os.path.join(out_dir, json_filename)
                content = str(response)
                with open(json_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    print(file)
                user_rating = rate_response(response, file)
                metrics.add(model['name'], model['parameters'], model['size'], file, elapsed, user_rating)
                print(f"Model {model['name']} processed in {elapsed_str_display}. Output written to {json_path}\n")
    csv_path = os.path.join(out_dir, 'metrics.csv')
    metrics.to_csv(csv_path)
    print(f"Metrics written to {csv_path}")

def ask_yes_no(prompt):
    # Strictement interactif : on laisse l'appel à input() et on valide y/n
    while True:
        val = input(prompt).strip().lower()
        if val in ("y", "n"):
            return val
        print("Réponse invalide. Veuillez entrer 'y' ou 'n'.")


def ask_int_in_range(prompt, min_val, max_val):
    # Strictement interactif : on laisse input() et on valide l'entier dans l'intervalle
    while True:
        val = input(prompt).strip()
        try:
            num = int(val)
            if min_val <= num <= max_val:
                return num
            else:
                print(f"Veuillez entrer un nombre entre {min_val} et {max_val}.")
        except ValueError:
            print("Veuillez entrer un nombre entier valide.")


def rate_response(response: Response, pdf_file: str) -> float:
    """Affiche la réponse, tente la désérialisation, puis demande une note utilisateur.

    Comportement:
    - Si la désérialisation échoue -> retourne 0.0 immédiatement.
    - Si stdin n'est pas un TTY (exécution non interactive, p.ex. pytest sans -s) -> auto-notation :
      on attribue le maximum pour chaque champ où la valeur attendue == valeur obtenue, sinon 0.
    - Si stdin est un TTY -> comportement interactif : invite l'utilisateur à noter les champs non égaux
      (avec validation stricte des entrées numériques).
    """
    import sys

    print(response)

    # 1) try to deserialize: if it fails, format considered not OK -> score 0
    try:
        response.deserialize()
    except Exception as e:
        print(f"Deserialization error: {e}")
        return 0.0

    # Helper to safely get attributes
    def get_attr(obj, name):
        return getattr(obj, name, None)

    # equality check unchanged
    def values_equal(expected, got):
        # Both None / empty
        if expected is None and (got is None or str(got).strip() == '' or got == 'None'):
            return True
        # Try numeric comparison
        try:
            if expected is not None and got is not None:
                exp_num = float(expected)
                got_num = float(got)
                if abs(exp_num - got_num) <= 1e-6:
                    return True
        except Exception:
            pass
        # Fallback string compare
        if expected is not None and got is not None:
            try:
                if str(expected).strip().lower() == str(got).strip().lower():
                    return True
            except Exception:
                pass
        return False
    total_grade = 0

    # Interactive path: ask user for individual grades with validation.
    # If expected == got we automatically give the max points for that field
    # total_excluding_vat (0-15)
    exp = supposed[pdf_file]['total_excluding_vat']
    got = get_attr(response, '_total_excluding_vat')
    if values_equal(exp, got):
        print(f"Expected == Got for total_excluding_vat ({exp}) -> awarding full 15 points automatically.")
        total_grade += 15
    else:
        print("Rate total_excluding_vat:")
        total_grade += ask_int_in_range(f"Expected: {exp}, Got: {got}. Rate 0-15: ", 0, 15)

    # total_vat (0-15)
    exp = supposed[pdf_file]['total_vat']
    got = get_attr(response, '_total_vat')
    if values_equal(exp, got):
        print(f"Expected == Got for total_vat ({exp}) -> awarding full 15 points automatically.")
        total_grade += 15
    else:
        print("Rate total_vat:")
        total_grade += ask_int_in_range(f"Expected: {exp}, Got: {got}. Rate 0-15: ", 0, 15)

    # total_including_vat (0-15)
    exp = supposed[pdf_file]['total_including_vat']
    got = get_attr(response, '_total_including_vat')
    if values_equal(exp, got):
        print(f"Expected == Got for total_including_vat ({exp}) -> awarding full 15 points automatically.")
        total_grade += 15
    else:
        print("Rate total_including_vat:")
        total_grade += ask_int_in_range(f"Expected: {exp}, Got: {got}. Rate 0-15: ", 0, 15)

    # date (0-25)
    exp = supposed[pdf_file]['date']
    got = get_attr(response, '_date')
    if values_equal(exp, got):
        print(f"Expected == Got for date ({exp}) -> awarding full 25 points automatically.")
        total_grade += 25
    else:
        print("Rate date:")
        total_grade += ask_int_in_range(f"Expected: {exp}, Got: {got}. Rate 0-25: ", 0, 25)

    # supplier (0-30)
    exp = supposed[pdf_file]['supplier']
    got = get_attr(response, '_supplier')
    if values_equal(exp, got):
        print(f"Expected == Got for supplier ({exp}) -> awarding full 30 points automatically.")
        total_grade += 30
    else:
        print("Rate supplier:")
        total_grade += ask_int_in_range(f"Expected: {exp}, Got: {got}. Rate 0-30: ", 0, 30)

    print(f"Total grade: {total_grade}/100")
    return float(total_grade)

class RatingRequest:
    def __init__(self, response, pdf_file, model, elapsed):
        self.response = response
        self.pdf_file = pdf_file
        self.model = model
        self.elapsed = elapsed


def ai_worker(pdf_files, models, rating_queue, batches_base, processed_set=None):
    """Thread secondaire : génère les réponses AI et les ajoute à la file d'attente de notation.

    Si `processed_set` est fourni, on saute les combinaisons (pdf_file, model_name, model_parameters)
    déjà présentes dans le CSV de progression pour éviter le retraitement.
    """
    import os
    import time
    out_dir = _next_batch_folder(batches_base)
    for idx, file in enumerate(pdf_files, start=1):
        pdf_path = os.path.join(os.path.dirname(__file__), 'test_data', 'pdf', file)
        ticket = Ticket(pdf_path)
        for model in models:
            key = (file, model['name'], str(model['parameters']))
            if processed_set and key in processed_set:
                # Skip already-processed combination
                print(f"Skipping already processed: {file} | {model['name']}:{model['parameters']}b")
                continue
            requester = AiRequester(ticket, model=f"{model['name']}:{model['parameters']}b")
            start = time.perf_counter()
            try:
                response = requester.request()
            except Exception as e:
                response = str(e)
            end = time.perf_counter()
            elapsed = end - start
            # Sauvegarde la réponse comme avant
            base_name = os.path.splitext(file)[0]
            json_filename = f"{base_name}__{model['name']}__{model['parameters']}b__{int(elapsed)}s.json"
            json_path = os.path.join(out_dir, json_filename)
            with open(json_path, 'w', encoding='utf-8') as f:
                f.write(str(response))
            # Ajoute à la file d'attente de notation
            rating_queue.put(RatingRequest(response, file, model, elapsed))
    # Signal to indicate worker finished
    rating_queue.put(None)


def rating_loop(rating_queue, metrics):
    """Thread principal : affiche les réponses à noter dès qu'elles sont prêtes."""
    import time
    while True:
        try:
            req = rating_queue.get(timeout=1)
        except queue.Empty:
            print("Aucune réponse à noter pour l'instant. En attente...")
            time.sleep(1)
            continue
        # Check for sentinel signaling worker completion
        if req is None:
            print("Worker a terminé et a envoyé le signal de fin. Fin de la boucle de notation.")
            break
        print(f"\nÀ noter : {req.pdf_file} | Modèle : {req.model['name']} ({req.model['parameters']}B)")
        user_rating = rate_response(req.response, req.pdf_file)
        metrics.add(req.model['name'], req.model['parameters'], req.model['size'], req.pdf_file, req.elapsed, user_rating)
        print(f"Noté {req.pdf_file} pour le modèle {req.model['name']} : {user_rating}/100\n")


def test_evaluate_models_capabilities_threaded():
    """Nouvelle version interactive avec file d'attente et threads."""
    import os
    root = os.path.dirname(__file__)
    pdf_dir = os.path.join(root, 'test_data', 'pdf')
    batches_base = os.path.join(root, 'test_data', 'json_batches')
    files = sorted([f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')])

    # Support for starting at a specific invoice (useful to resume after crash)
    # Two options via environment variables:
    # - AI_RATING_START_FILE=invoice-test-5.pdf   (start at this filename)
    # - AI_RATING_START_INDEX=5                   (1-based index to start from)
    start_file = os.environ.get('AI_RATING_START_FILE')
    start_index_env = os.environ.get('AI_RATING_START_INDEX')
    if start_file:
        if start_file in files:
            idx0 = files.index(start_file)
            files = files[idx0:]
            print(f"Démarrage depuis le fichier demandé : {start_file} (index {idx0+1})")
        else:
            print(f"AI_RATING_START_FILE={start_file} introuvable dans {pdf_dir}. Démarrage au début.")
    elif start_index_env:
        try:
            si = int(start_index_env)
            if si < 1:
                raise ValueError
            if si > len(files):
                print(f"AI_RATING_START_INDEX={si} est supérieur au nombre de fichiers ({len(files)}). Démarrage au début.")
            else:
                files = files[si-1:]
                print(f"Démarrage depuis l'index {si} -> fichier {files[0]}")
        except Exception:
            print(f"AI_RATING_START_INDEX={start_index_env} invalide. Démarrage au début.")

    metrics = Metrics()
    # Load processed set from existing metrics progress CSV so we can skip already done items
    processed_csv = metrics.csv_path
    processed_set = load_processed_set(processed_csv)
    if processed_set:
        print(f"Chargé {len(processed_set)} entrées déjà traitées depuis {processed_csv}")

    rating_queue = queue.Queue()
    # Lancer le thread secondaire
    worker = threading.Thread(target=ai_worker, args=(files, models, rating_queue, batches_base, processed_set), daemon=True)
    worker.start()
    # Boucle de notation principale
    rating_loop(rating_queue, metrics)
    # Sauvegarde des métriques
    out_dir = _next_batch_folder(batches_base)
    csv_path = os.path.join(out_dir, 'metrics.csv')
    metrics.to_csv(csv_path)
    print(f"Metrics written to {csv_path}")

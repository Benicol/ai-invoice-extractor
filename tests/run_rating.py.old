#!/usr/bin/env python3
"""Petit runner pour démarrer la boucle de notation avec arguments CLI.

Usage examples:
  python tests/run_rating.py --start-file invoice-test-5.pdf
  python tests/run_rating.py --start-index 5

Ce script positionne des variables d'environnement utilisées par
`test_evaluate_models_capabilities_threaded` puis appelle la fonction.
"""
import os
import sys
import argparse
import importlib.util

from pathlib import Path

TEST_MODULE_PATH = str(Path(__file__).resolve().parent / 'test_ai_requester_lot.py')


def load_test_module(path):
    spec = importlib.util.spec_from_file_location('test_ai_requester_lot', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(description="Runner interactif pour la notation AI")
    parser.add_argument("--start-file", help="Nom de fichier PDF de départ, ex: invoice-test-5.pdf")
    parser.add_argument("--start-index", type=int, help="Index 1-based du fichier de départ")
    args = parser.parse_args(argv)

    if args.start_file:
        os.environ['AI_RATING_START_FILE'] = args.start_file
    if args.start_index:
        os.environ['AI_RATING_START_INDEX'] = str(args.start_index)

    # Load the test module by path so this script can be run directly
    mod = load_test_module(TEST_MODULE_PATH)
    # Call the interactive runner function
    if hasattr(mod, 'test_evaluate_models_capabilities_threaded'):
        mod.test_evaluate_models_capabilities_threaded()
    else:
        print('La fonction test_evaluate_models_capabilities_threaded() est introuvable dans le module de test.')


if __name__ == '__main__':
    main()

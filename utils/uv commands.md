### Dependencies update
""""""
# Installer les dépendances depuis pyproject.toml
uv pip install -r requirements.txt

# Mettre à jour toutes les dépendances
uv pip install --upgrade -r requirements.txt

# Geler les dépendances installées dans un fichier requirements.txt
uv pip freeze > requirements.txt

# Installer une dépendance spécifique
uv pip install nom_du_paquet

# Désinstaller une dépendance
uv pip uninstall nom_du_paquet

# Vérifier les dépendances obsolètes
uv pip list --outdated

# Lancer un shell Python avec uv
uv python

# Installer les dépendances en mode développement (si pyproject.toml présent)
uv pip install -e .

# Nettoyer le cache uv
uv cache clean

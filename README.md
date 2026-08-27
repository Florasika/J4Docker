# 🐳 Jour 4 / 10 — Docker : Multi-stage Build

> **Série : 10 Days of Docker** · Jour 4/10  
> Concepts : Multi-stage build · Image légère · Utilisateur non-root · Optimisation taille

---

## 📁 Fichiers du projet

```
day-04-multistage/
│
├── Dockerfile.naive        ← Image naive (~900MB)
├── Dockerfile.multistage   ← Image optimisée (~150MB)
├── requirements_j4.txt     ← Dépendances Python
├── docker-compose-j4.yml   ← Comparaison des deux images
├── app_j4/
│   └── etl_optimise.py     ← Pipeline ETL
└── README.md
```

---

## 🧠 Pourquoi le multi-stage build ?

```
Image naive :
    python:3.11 + pip + setuptools + wheels + cache + code
    → ~900MB — lourde, surface d'attaque large

Image multi-stage :
    Stage 1 (builder) : installe tout
    Stage 2 (runtime) : copie UNIQUEMENT les dépendances compilées
    → ~150MB — légère, propre, sécurisée
```

---

## 🚀 ÉTAPE 1 — Préparer les fichiers

```bash
mkdir -p jour4-docker/app_j4
mkdir -p jour4-docker/output_naive
mkdir -p jour4-docker/output_optimise
cd jour4-docker/

# Copier les fichiers depuis le dépôt :
# Dockerfile.naive        → racine
# Dockerfile.multistage   → racine
# requirements_j4.txt     → racine
# docker-compose-j4.yml   → racine
# etl_optimise.py         → app_j4/etl_optimise.py
```

---

## 🔑 ÉTAPE 2 — Comprendre le Dockerfile multi-stage

```dockerfile
# STAGE 1 : BUILDER
FROM python:3.11 AS builder

WORKDIR /build
COPY requirements_j4.txt .

# Installer dans un dossier isolé
RUN pip install --no-cache-dir --prefix=/build/install -r requirements_j4.txt

# STAGE 2 : RUNTIME (image finale légère)
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copier UNIQUEMENT les dépendances compilées du stage builder
COPY --from=builder /build/install /usr/local

# Copier le code
COPY app_j4/ ./app_j4/

# Utilisateur non-root (sécurité)
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN mkdir -p /app/output && chown -R appuser:appuser /app
USER appuser

CMD ["python", "app_j4/etl_optimise.py"]
```

---

## 🚀 ÉTAPE 3 — Construire et comparer

```bash
# Construire l'image naive
docker build -f Dockerfile.naive -t etl-naive:1.0 .

# Construire l'image multi-stage
docker build -f Dockerfile.multistage -t etl-optimise:1.0 .

# Comparer les tailles
docker images | grep etl

# Résultat attendu :
# REPOSITORY      TAG   SIZE
# etl-optimise    1.0   ~150MB
# etl-naive       1.0   ~950MB
```

---

## 🚀 ÉTAPE 4 — Lancer et tester

```bash
# Image optimisée
mkdir -p output_optimise
docker run -v $(pwd)/output_optimise:/app/output etl-optimise:1.0

# Image naive (pour comparer)
mkdir -p output_naive
docker run -v $(pwd)/output_naive:/app/output etl-naive:1.0

# Les résultats sont identiques malgré des images très différentes
ls output_optimise/
ls output_naive/
```

---

## 🚀 ÉTAPE 5 — Via docker-compose

```bash
# Image optimisée seulement
docker-compose -f docker-compose-j4.yml up --build etl_optimise

# Les deux images pour comparer
docker-compose -f docker-compose-j4.yml --profile compare up --build
```

---

## 🚀 ÉTAPE 6 — Inspecter l'image

```bash
# Voir les couches et leur taille
docker history etl-optimise:1.0

# Vérifier l'utilisateur
docker run etl-optimise:1.0 whoami
# → appuser (pas root)

# Tenter d'écrire en dehors du volume
docker run etl-optimise:1.0 touch /etc/test
# → Permission denied (utilisateur non-root)
```

---

## 🔑 Bonnes pratiques Dockerfile

### Ordre des instructions — optimiser le cache

```dockerfile
# CORRECT — cache pip réutilisé si requirements.txt ne change pas
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ ./app/

# MAUVAIS — pip réinstallé à chaque modification du code
COPY . .
RUN pip install -r requirements.txt
```

### Choisir la bonne image de base

| Image | Taille | Usage |
|-------|--------|-------|
| python:3.11 | ~900MB | Build — a tout |
| python:3.11-slim | ~45MB | Runtime recommandé |
| python:3.11-alpine | ~18MB | Ultra léger |

### Fichier .dockerignore

```
__pycache__/
*.pyc
.git/
.env
output/
*.log
```

---

## 💡 Récap — Multi-stage vs Naive

| | Image Naive | Multi-stage |
|---|---|---|
| Taille | ~900MB | ~150MB |
| Outils de build | Inclus | Exclus |
| Utilisateur | root | appuser |
| Sécurité | Faible | Meilleure |
| Production | Non | Oui |


---

⭐ **Si ce projet t'aide, mets une étoile !**

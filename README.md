# WinMarket AI — Plateforme de Scoring des Appels d'Offres

Solution propulsée par IA pour analyser, scorer et générer une réponse complète à un appel d'offres, à destination des ESN (Entreprises de Services Numériques).

Le moteur métier (extraction, RAG, capacité, scoring, génération de livrables)
est exposé par deux interfaces :

- **Interface web FastAPI** (`main.py`) — interface principale, HTML/CSS/JS +
  FastAPI + Jinja2. C'est la version à utiliser.
- **Interface Streamlit** (`src/ui/app.py`) — conservée en référence fonctionnelle
  pendant la migration ; peut être archivée une fois la version FastAPI validée.

Les deux interfaces partagent exactement le même moteur Python et la même
base de connaissances.

Depuis la V3, l'interface FastAPI est un **SaaS avec comptes** : pages
publiques (accueil, tarifs, contact), inscription/connexion, et une
application (`/app/*`) réservée aux comptes Starter actifs, dont
l'historique est **personnel** (stocké en PostgreSQL, filtré par
utilisateur). Streamlit continue de lire/écrire le fichier JSON global
`data/historique/historique_ao.json` — il n'a pas la notion de compte et
reste une interface legacy indépendante ; voir « V3 — Couche SaaS » plus bas.

## Installation locale (VS Code / terminal)

```bash
cd "WinMarket AI"
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt

copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux
```

Édite ensuite `.env`. Les secrets restent uniquement dans ce fichier local et ne
doivent jamais être versionnés :

```dotenv
# Ordre de priorité configurable ; Anthropic reste le provider principal.
LLM_PROVIDER_PRIORITY=anthropic,openai,mistral

ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
MISTRAL_API_KEY=
MISTRAL_MODEL=mistral-small-latest

PAPPERS_API_TOKEN=

# Traitements factuels et génération rédactionnelle
LLM_TEMPERATURE_FACTUAL=0.1
LLM_TEMPERATURE_GENERATION=0.3
```

Il suffit de renseigner la clé des providers réellement utilisés. Le provider
suivant dans la liste sert de fallback lorsqu'il possède une clé valide.

## Lancement — interface web FastAPI (recommandé)

```bash
# Environnement virtuel actif
uvicorn main:app --reload --port 8000
```

L'application est accessible sur `http://localhost:8000`.

- `/` — landing page WinMarket AI
- `/app/analyser` — nouvelle analyse (import, drag & drop, saisie libre)
- `/app/historique` — historique des analyses
- `/app/base-connaissances` — base de connaissances (RAG)
- `/app/resultats/{id}` — résultats d'une analyse (score, décision, livrables)

L'analyse s'exécute côté serveur dans un thread d'arrière-plan ; le navigateur
interroge `/api/analyze/{id}/status` pour afficher la progression réelle
(les mêmes étapes que l'orchestrateur exécute réellement), puis redirige vers
la page de résultats une fois l'analyse terminée.

## Lancement — interface Streamlit (legacy)

```bash
# Environnement virtuel actif
python -m streamlit run src/ui/app.py --browser.gatherUsageStats false
```

L'application est accessible sur `http://localhost:8501`

L'option de télémétrie évite notamment les problèmes de droits d'écriture dans
le dossier utilisateur sous Windows.

## V3 — Couche SaaS (comptes, PostgreSQL, historique personnel)

### Architecture

```
Navigateur → FastAPI → couche SaaS (auth, sessions, abonnements) → PostgreSQL
                     → orchestrateur / modules WinMarket AI existants (inchangés)
```

Le moteur métier reste partagé et gelé — aucune copie par utilisateur. La
couche SaaS ajoute uniquement : comptes, sessions, isolation des données,
documents, demandes de contact.

### 1. Base de données PostgreSQL

Fonctionne à l'identique avec un Postgres local, Docker, ou managé
(Supabase, Neon, ...) — la seule dépendance est `DATABASE_URL` :

```dotenv
DATABASE_URL=postgresql://user:password@host:5432/winmarket
```

Le driver (`pg8000`, pur Python — pas de binaire compilé à installer) est
choisi automatiquement ; il n'y a rien d'autre à configurer.

PostgreSQL local rapide via Docker (optionnel — un Postgres existant ou
managé convient tout aussi bien) :

```bash
docker compose up -d postgres
# DATABASE_URL correspondante :
# postgresql://winmarket:winmarket@localhost:5432/winmarket
```

### 2. Variables d'environnement

Copie `.env.example` en `.env` et complète, en plus des variables LLM
existantes :

```dotenv
DATABASE_URL=
SESSION_SECRET=            # python -c "import secrets; print(secrets.token_urlsafe(48))"
ADMIN_NOTIFICATION_EMAIL=adrien.khalar@bizime.com
APP_ENV=development
BASE_URL=http://localhost:8000
STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=data
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=
```

Si `SMTP_HOST`/`SMTP_FROM_EMAIL` ne sont pas renseignés, les notifications
admin (nouvelle inscription, nouveau contact) sont simplement journalisées
au lieu d'être envoyées — jamais d'erreur utilisateur, jamais de secret
dans les logs.

### 3. Migrations Alembic

```bash
# Créer les tables (users, subscriptions, analyses, analysis_documents,
# contact_requests, password_reset_tokens)
alembic upgrade head

# Revenir en arrière si besoin
alembic downgrade base

# Générer une nouvelle migration après un changement de modèle
alembic revision -m "description" --autogenerate
```

### 4. Créer ton premier compte (Starter, déjà actif)

```bash
python scripts/create_demo_user.py
```

Prénom / nom / email / mot de passe sont saisis en interactif — le mot de
passe n'est jamais un argument, jamais écrit dans un fichier, jamais commité.

### 5. Migrer l'historique existant vers PostgreSQL

```bash
python scripts/migrate_history_to_postgresql.py <ton-email>
```

- Sauvegarde `data/historique/` (JSON + détails d'analyses) dans
  `data/historique/_migration_backups/<horodatage>/` avant toute écriture.
- Une ligne PostgreSQL par analyse, rattachée à ton compte.
- Rejouable sans doublon (déduplication par `job_id`, ou une clé de
  substitution pour les entrées historiques sans `job_id`).
- Aucun fichier source n'est modifié ni supprimé.
- Affiche un rapport (détectées / migrées / ignorées / erreurs).

### 6. Validation manuelle des comptes

Pas de back-office — de simples scripts CLI :

```bash
python scripts/list_pending_users.py
python scripts/activate_user.py utilisateur@email.com
python scripts/reject_user.py utilisateur@email.com
python scripts/disable_user.py utilisateur@email.com
```

`activate_user.py` passe `users.status=active` et
`subscriptions.status=active` (+ `started_at`) dans une seule transaction
atomique.

### 7. Lancement local complet

```bash
alembic upgrade head
uvicorn main:app --reload --port 8000
```

`/` (accueil), `/pricing`, `/contact` restent publiques. `/login`,
`/register`, `/account`, `/account/pending` gèrent l'authentification.
Toutes les routes `/app/*` et `/api/*` (hors `/api/contact`) exigent un
compte `active` avec un abonnement Starter `active` — sinon redirection
vers `/login?next=...` (non connecté) ou `/account/pending` (compte pas
encore activé).

### 8. Déploiement

Architecture cible, indépendante du fournisseur (seule dépendance :
`DATABASE_URL`) :

```
GitHub → FastAPI (Render / Railway / équivalent) → PostgreSQL managé (Supabase / Neon)
```

```bash
alembic upgrade head        # migration en premier
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Mettre `APP_ENV=production` (cookies `Secure`) et `BASE_URL` sur l'URL
publique réelle.

### 9. Sauvegarde / restauration

```bash
# Sauvegarde
pg_dump "$DATABASE_URL" -Fc -f winmarket_backup.dump

# Restauration
pg_restore --clean --if-exists -d "$DATABASE_URL" winmarket_backup.dump
```

Les fichiers PDF/DOCX/JSON restent sous `data/` (mode `STORAGE_BACKEND=local`)
— à inclure dans toute sauvegarde tant qu'un stockage objet n'est pas activé.

### 10. Limites connues avant mise en production

- **Email de réinitialisation de mot de passe non envoyé** : la structure
  (table, token à usage unique, expiration 1h, hash) est fonctionnelle,
  mais `POST /forgot-password` ne fait aujourd'hui que journaliser le lien
  côté serveur — brancher `src/web/services/email_service.py` une fois le
  cœur SaaS validé.
- **`STORAGE_BACKEND=object`** (Supabase Storage / S3) n'est pas implémenté
  — seule l'interface `StorageService` est prête ; `LocalStorageService`
  est la seule implémentation actuelle.
- **Rate limiting du login** en mémoire, par process — suffisant en
  développement/mono-instance, à remplacer par une solution partagée
  (Redis, WAF) avant une mise à l'échelle multi-instances.
- **`organizations`** (comptes Business/Enterprise multi-utilisateurs) non
  modélisé — Business/Enterprise restent des prospects (`contact_requests`)
  dans cette version, comme demandé.
- Aucune infrastructure Postgres n'était disponible pour valider cette V3
  en conditions réelles ; la suite de tests tourne contre SQLite (mêmes
  modèles, mêmes requêtes — voir `tests/conftest.py`) et un test manuel
  complet a été fait en local. **Faire tourner `alembic upgrade head` et un
  cycle inscription → activation → connexion → analyse contre un vrai
  Postgres (local ou Supabase) avant la mise en production.**

## Fonctionnement du pipeline

1. **Ingestion** : fichier PDF / TXT / DOCX / MD, texte libre ou exemple intégré
2. **Sécurité et modération** : contrôle obligatoire du contenu non fiable avant tout traitement IA
3. **Préparation** : normalisation Unicode, nettoyage et déduplication prudente sans résumé agressif
4. **Extraction intelligente** : premier provider LLM disponible, sinon extracteur local par règles
5. **Enrichissement client** : API Pappers si token configuré, sinon profil estimé
6. **Analyse documentaire et RAG** : TF-IDF, sélection des références et reranking sémantique
7. **Analyse capacité** : charge actuelle et disponibilité de l'équipe
8. **Scoring enrichi** : critères pondérés, règles éliminatoires et justifications factuelles
9. **Décision** : GO (≥88) / GO SOUS RÉSERVE (≥60) / NO-GO (<60 ou critère bloquant)
10. **Livrables** : rapport PDF de décision et dossier DOCX adapté à la décision

Le moteur de scoring et ses règles métier restent déterministes. La température
basse, le RAG et les validations réduisent la variabilité, mais ne constituent
pas à eux seuls une garantie contre les hallucinations.

## Disponibilité opérationnelle

Avant une analyse, l'accueil affiche la charge globale, la disponibilité restante
et le nombre de projets en cours. Le bouton « Modifier les disponibilités » permet
de mettre à jour :

- la charge globale de l'équipe ;
- le nombre et le nom facultatif des projets en cours ;
- la disponibilité de chaque pôle.

L'enregistrement met à jour le fichier
data/reg_docs/ressources/capacite_charge_planification.md, recharge immédiatement
la base RAG et alimente CapacityAnalyzer. La prochaine analyse et son scoring
capacitaire utilisent donc les nouvelles valeurs.

## Sécurité des contenus importés

Tous les modes d'entrée empruntent la même couche de contrôle. Le document est
toujours traité comme une donnée non fiable, jamais comme une instruction système.

Le contrôle recherche notamment :

- les formulations caractéristiques d'une prompt injection ;
- les demandes d'ignorance, de révélation ou de modification des instructions ;
- les changements de rôle et pseudo-balises système ;
- les contenus manifestement étrangers à un appel d'offres.

En cas de refus, l'analyse est interrompue avant l'extraction, le RAG et le LLM.
L'utilisateur reçoit un message générique, tandis que les logs conservent seulement
des codes techniques et une empreinte non réversible — jamais le contenu ou une clé.

## Stratégie multi-provider

`llm_client.py` expose un contrat commun aux adaptateurs Anthropic, OpenAI et
Mistral. L'ordre est défini par `LLM_PROVIDER_PRIORITY`.

Le provider suivant est essayé uniquement après une erreur compatible : timeout,
erreur réseau, rate limit, indisponibilité serveur ou authentification. Une erreur
fonctionnelle, un payload invalide ou une réponse JSON incorrecte ne provoque pas
de changement automatique de provider. Le provider effectivement utilisé est
journalisé sans exposer les secrets.

## Structure du projet

```
AO_SCORING_V2/
├── main.py                        # Point d'entrée FastAPI (uvicorn main:app)
├── alembic.ini
├── migrations/                    # Migrations Alembic (schéma V3)
│   └── versions/0001_initial_schema.py
├── docker-compose.yml             # PostgreSQL local optionnel
├── scripts/                       # CLI de gestion des comptes (V3)
│   ├── create_demo_user.py, list_pending_users.py
│   ├── activate_user.py, reject_user.py, disable_user.py
│   └── migrate_history_to_postgresql.py
├── templates/                     # Pages Jinja2 (landing + application)
│   ├── layout.html / app_shell.html
│   ├── landing.html, pricing.html, contact.html
│   ├── login.html, register.html, account.html, account_pending.html
│   ├── forgot_password.html, reset_password.html
│   ├── components/site_header.html, site_footer.html, access_modal.html
│   └── app_analyze.html, app_result.html, app_history.html, app_knowledge.html, ...
├── static/
│   ├── css/                       # variables.css, base.css, components.css, landing.css, app.css, pricing.css
│   └── js/                        # main.js, analyze.js, history.js, knowledge.js, contact.js, pricing.js
├── src/
│   ├── agents/
│   │   ├── ao_extractor.py        # Extraction structurée de l'appel d'offres
│   │   ├── capacity_analyzer.py   # Analyse capacité interne
│   │   ├── company_enrichment.py  # Enrichissement client (Pappers)
│   │   ├── llm_client.py          # Façade LLM et stratégie de fallback
│   │   ├── llm_providers.py       # Adaptateurs Anthropic/OpenAI/Mistral
│   │   └── scoring_engine.py      # Moteur de scoring 12 critères
│   ├── core/
│   │   ├── capacity_repository.py # Lecture/écriture du plan de capacité RAG
│   │   ├── config.py              # Chemins et variables d'environnement (+ vars V3)
│   │   ├── content_security.py    # Modération des entrées non fiables
│   │   ├── content_preparation.py # Nettoyage et structuration sans perte métier
│   │   ├── models.py              # Modèles Pydantic (moteur métier)
│   │   └── pipeline.py            # Orchestrateur principal
│   ├── rag/
│   │   └── rag_manager.py         # RAG local TF-IDF + reranking sémantique
│   ├── livrables/
│   │   └── document_generator.py  # Génération PDF + DOCX personnalisés
│   ├── web/                       # Couche web FastAPI (pas de logique métier)
│   │   ├── routes_pages.py        # Routes HTML publiques + /app/* (protégées)
│   │   ├── routes_api.py          # Routes JSON /api/* (protégées)
│   │   ├── routes_auth.py         # /login /register /logout
│   │   ├── routes_account.py      # /account /account/pending /forgot-password /reset-password
│   │   ├── jobs.py                # Analyse en tâche de fond + double écriture JSON/PostgreSQL
│   │   ├── historique_service.py  # Historique JSON global — legacy, sert Streamlit uniquement
│   │   ├── knowledge_service.py, examples_service.py, pipeline_singleton.py, templating.py
│   │   ├── auth/                  # service.py (Argon2), session_cookie.py, dependencies.py (contrôle d'accès)
│   │   ├── database/              # models.py (SQLAlchemy), session.py, repositories/
│   │   ├── security/              # csrf.py (double-submit cookie), rate_limit.py
│   │   ├── services/               # history_service.py (Postgres, par utilisateur), email_service.py
│   │   └── storage/                # service.py — abstraction StorageService / LocalStorageService
│   └── ui/
│       ├── app.py                 # Interface Streamlit — WinMarket AI (legacy)
│       └── capacity_editor.py     # Éditeur des disponibilités et projets (Streamlit)
├── data/
│   ├── reg_docs/                  # Base documentaire ESN (services, références, équipes)
│   ├── ao_examples/                # Appels d'offres de démo
│   ├── historique/                 # Historique JSON legacy (Streamlit) + backups de migration
│   └── outputs/                    # Livrables générés (PDF/DOCX)
├── tests/                          # Suite pytest — pipeline (existant) + SaaS V3 (nouveau)
├── .env.example
├── requirements.txt
└── README.md
```

## Comportement sans clé LLM

WinMarket AI fonctionne sans clé Anthropic, OpenAI ou Mistral et utilise ses
comportements locaux déterministes :

- Extraction par règles (regex, listes de mots clés)
- Scoring algorithmique (12 critères, règles métier)
- Livrables générés sur template standard

## Avec un provider LLM

Avec au moins une clé configurée, WinMarket AI active les enrichissements IA :

- Extraction sémantique complète du document
- Reranking des références par pertinence réelle + synthèse
- Justifications de scoring enrichies et contextualisées
- Livrables entièrement rédigés sur mesure (résumé exécutif, méthodologie, équipe, conclusion)

Les coûts dépendent du provider, du modèle configuré et de la taille du document.

## Tests

```bash
python -m pytest -q
```

La suite couvre :
- **Pipeline (inchangé)** : contenu valide, prompt injection, contenu hors
  périmètre, fonctionnement du provider principal, fallback sur timeout,
  absence de fallback pour une erreur de validation, extraction, scoring,
  capacité.
- **SaaS V3** (`tests/test_saas_*.py`, `tests/test_migrate_history_script.py`) :
  inscription, statuts pending/active/rejected/disabled, connexion (bon et
  mauvais mot de passe), déconnexion, scripts d'administration, isolation de
  l'historique par utilisateur, non-visibilité d'une analyse pour un autre
  utilisateur, migration de l'historique JSON, demandes de contact Business/
  Enterprise, protection CSRF.

Ces tests tournent contre une base SQLite temporaire par test (voir
`tests/conftest.py`) — mêmes modèles, mêmes requêtes que PostgreSQL, aucune
base externe requise pour lancer la suite.

> Sur certains environnements Windows, le répertoire temporaire par défaut de
> pytest peut être restreint en écriture (erreur `PermissionError` sur
> `pytest-of-<user>`) ; dans ce cas, lance : `pytest --basetemp=.pytest_tmp`.

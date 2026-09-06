# WinMarket AI — Plateforme de Scoring des Appels d'Offres

Solution Streamlit propulsée par IA pour analyser, scorer et générer une réponse complète à un appel d'offres, à destination des ESN (Entreprises de Services Numériques).

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

## Lancement

```bash
# Environnement virtuel actif
python -m streamlit run src/ui/app.py --browser.gatherUsageStats false
```

L'application est accessible sur `http://localhost:8501`

L'option de télémétrie évite notamment les problèmes de droits d'écriture dans
le dossier utilisateur sous Windows.

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
│   │   ├── config.py              # Chemins et variables d'environnement
│   │   ├── content_security.py    # Modération des entrées non fiables
│   │   ├── content_preparation.py # Nettoyage et structuration sans perte métier
│   │   ├── models.py              # Modèles Pydantic
│   │   └── pipeline.py            # Orchestrateur principal
│   ├── rag/
│   │   └── rag_manager.py         # RAG local TF-IDF + reranking sémantique
│   ├── livrables/
│   │   └── document_generator.py  # Génération PDF + DOCX personnalisés
│   └── ui/
│       ├── app.py                 # Interface Streamlit — WinMarket AI
│       └── capacity_editor.py     # Éditeur des disponibilités et projets
├── data/
│   ├── reg_docs/                  # Base documentaire ESN (services, références, équipes)
│   ├── ao_examples/               # Appels d'offres de démo
│   └── outputs/                   # Livrables générés
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

La suite couvre notamment un contenu valide, une prompt injection, un contenu hors
périmètre, le fonctionnement du provider principal, le fallback sur timeout et
l'absence de fallback pour une erreur de validation.

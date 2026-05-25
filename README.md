# WinMarket AI — Plateforme de Scoring des Appels d'Offres

Solution Streamlit propulsée par IA pour analyser, scorer et générer une réponse complète à un appel d'offres, à destination des ESN (Entreprises de Services Numériques).

## Installation locale (VS Code / terminal)

```bash
cd AO_SCORING_V2
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt

copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux
```

Édite le fichier `.env` et renseigne tes clés :
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
PAPPERS_API_TOKEN=votre_token_pappers
```

## Lancement

```bash
streamlit run src/ui/app.py
```

L'application est accessible sur `http://localhost:8501`

## Fonctionnement du pipeline

1. **Ingestion** : lecture PDF / TXT / DOCX / MD
2. **Extraction intelligente** : Claude si clé API disponible, sinon extracteur local par règles
3. **Enrichissement client** : API Pappers si token configuré, sinon profil estimé
4. **Analyse sémantique des références** : TF-IDF + reranking Claude sur la base documentaire ESN
5. **Analyse capacité** : charge actuelle, disponibilité équipe
6. **Scoring enrichi** : 12 critères pondérés + règles éliminatoires + justifications Claude
7. **Décision** : GO (≥76) / GO SOUS RÉSERVE (≥58) / NO-GO (<58 ou critère bloquant)
8. **Livrables sur mesure** : rapport PDF de décision + dossier DOCX de candidature générés par IA

## Structure du projet

```
AO_SCORING_V2/
├── src/
│   ├── agents/
│   │   ├── ao_extractor.py        # Extraction structurée de l'appel d'offres
│   │   ├── capacity_analyzer.py   # Analyse capacité interne
│   │   ├── company_enrichment.py  # Enrichissement client (Pappers)
│   │   ├── llm_client.py          # Client Claude API (Anthropic)
│   │   └── scoring_engine.py      # Moteur de scoring 12 critères
│   ├── core/
│   │   ├── config.py              # Chemins et variables d'environnement
│   │   ├── models.py              # Modèles Pydantic
│   │   └── pipeline.py            # Orchestrateur principal
│   ├── rag/
│   │   └── rag_manager.py         # RAG local TF-IDF + reranking sémantique
│   ├── livrables/
│   │   └── document_generator.py  # Génération PDF + DOCX personnalisés
│   └── ui/
│       └── app.py                 # Interface Streamlit — WinMarket AI
├── data/
│   ├── reg_docs/                  # Base documentaire ESN (services, références, équipes)
│   ├── ao_examples/               # 6 appels d'offres de démo (GO, GO sous réserve, NO-GO)
│   └── outputs/                   # Livrables générés
├── .env.example
├── requirements.txt
└── README.md
```

## Comportement sans clé API Claude

WinMarket AI fonctionne sans clé Anthropic — le pipeline bascule automatiquement en mode local :
- Extraction par règles (regex, listes de mots clés)
- Scoring algorithmique (12 critères, règles métier)
- Livrables générés sur template standard

## Avec clé API Claude (mode optimisé)

Avec une clé Anthropic configurée, WinMarket AI active 4 étapes IA supplémentaires :
- Extraction sémantique complète du document
- Reranking des références par pertinence réelle + synthèse
- Justifications de scoring enrichies et contextualisées
- Livrables entièrement rédigés sur mesure (résumé exécutif, méthodologie, équipe, conclusion)

**Coût estimé par analyse : ~0,08 €** (Claude Sonnet, ~22 000 tokens)

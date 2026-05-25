# Service - IA générative, RAG documentaire et assistants métiers

## Positionnement
NovaSoft Conseil conçoit des solutions d'intelligence artificielle générative appliquées aux documents métiers : recherche augmentée, extraction d'informations, classification, scoring, génération de synthèses, assistants internes et automatisation de réponses structurées. Le service est orienté productivité métier et aide à la décision, avec validation humaine systématique.

## Périmètre fonctionnel
Nous réalisons des pipelines d'ingestion documentaire, OCR, chunking, vectorisation, stockage dans une base vectorielle, recherche sémantique, reranking, génération contrôlée par prompts, extraction JSON, auditabilité des sources et interface utilisateur. Les cas d'usage fréquents sont l'analyse d'appels d'offres, l'assistant support, la recherche dans documentation contractuelle, l'aide à la rédaction de réponses commerciales, la classification de tickets et l'analyse de conformité documentaire.

## Technologies
LangChain ou orchestration Python custom, ChromaDB, FAISS, PostgreSQL pgvector, sentence-transformers, OpenAI, Anthropic Claude, Mistral, Ollama pour tests locaux, PyMuPDF, Tesseract, Pydantic, FastAPI, Streamlit et React. Nous privilégions une architecture multi-modèles afin d'éviter une dépendance excessive à un fournisseur unique.

## Sécurité et gouvernance IA
Chaque solution intègre des garde-fous : prompts versionnés, schémas JSON validés, limitation du contexte envoyé au LLM, anonymisation possible, journalisation des décisions, mention explicite des incertitudes et conservation des sources utilisées. Nous évitons les décisions entièrement automatisées dans les contextes sensibles : le système recommande, l'humain décide.

## Méthode RAG
La qualité du RAG repose sur la qualité documentaire. Nous structurons les documents par type : services, offres, références, compétences, certifications, méthodologies, contraintes contractuelles, ressources et règles de décision. Chaque chunk doit contenir suffisamment de contexte pour être compréhensible indépendamment. Nous recommandons au minimum 30 à 50 documents internes pour un POC crédible, puis 150+ documents pour une V1 client.

## Points forts
Forte capacité à traiter des documents longs, à générer des sorties structurées exploitables par un moteur métier et à expliquer les scores produits. Expérience sur textes juridico-techniques, dossiers d'appels d'offres, documentation réglementaire et référentiels internes.

## Red flags
Promesse d'automatisation totale sans validation humaine, exigence d'un modèle local très performant sans budget GPU, absence de documentation interne exploitable, documents sources confidentiels sans cadre RGPD, besoin de scoring juridiquement engageant sans contrôle métier.

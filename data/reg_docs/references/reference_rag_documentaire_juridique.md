# Référence client - Assistant RAG documentaire juridique

## Secteur
Services B2B

## Contexte
Le client souhaitait moderniser un processus métier devenu trop manuel, dispersé entre emails, fichiers Excel et applications historiques. Les enjeux principaux étaient la fiabilisation des données, la traçabilité des actions, la réduction du temps de traitement et l'amélioration de l'expérience utilisateur.

## Périmètre réalisé
Mise en place d’un assistant documentaire pour interroger 4 500 documents contractuels, extraire des clauses et générer des synthèses sourcées. Architecture avec chunking contrôlé, métadonnées, score de confiance et validation humaine.

## Technologies et compétences mobilisées
Python, ChromaDB, Claude, FastAPI, OCR, Pydantic

## Budget et durée
Budget : 145 000 €
Durée : 5 mois

## Organisation projet
Équipe de 4 personnes : chef de projet, 2 consultants IA/RAG (architecture et développement), 1 développeur back-end FastAPI. L'UX est intervenu ponctuellement pour l'interface de recherche. Méthode itérative : POC en 4 semaines, puis itérations sur la qualité du chunking, du reranking et des prompts de génération. Validation humaine intégrée dès le début : les juristes validaient les synthèses avant que le système ne soit étendu.

## Enseignements réutilisables
Cette référence est directement pertinente pour tout AO demandant un assistant documentaire IA, un moteur de recherche sémantique ou une solution RAG sur corpus interne. Elle atteste de la maîtrise de l'ensemble de la chaîne RAG (ingestion, chunking, vectorisation, reranking, génération contrôlée) sur des documents longs et juridico-techniques. Elle est valorisable pour les secteurs assurance, finance, juridique, RH et secteur public disposant de gros volumes documentaires.

## Limites de comparaison
Cette référence ne couvre pas les modèles d'IA fine-tunés sur corpus propriétaire, les solutions nécessitant un hébergement souverain SecNumCloud, ni les pipelines en temps réel sur flux de données structurées.

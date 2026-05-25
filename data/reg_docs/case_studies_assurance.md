# Études de cas — Secteur Assurance et Services Financiers

Ces études de cas illustrent des projets réalisés par NovaSoft Conseil dans le secteur assurance et services financiers. Elles sont destinées à alimenter les arguments de références dans les candidatures aux appels d'offres.

---

## Cas #1 : Mutuelle Nova — Plateforme IA documentaire pour direction juridique

### Contexte client
Mutuelle de complémentaire santé, 310 000 adhérents. La direction juridique (12 juristes) gérait manuellement un corpus de 8 500 documents contractuels, réglementaires et de jurisprudence. Temps de recherche documentaire : 3 heures par juriste par jour. Aucun outil de recherche sémantique disponible.

### Solution déployée
Plateforme web sécurisée combinant un moteur RAG documentaire et un module d'analyse automatisée des contrats entrants.

**Stack technique :**
- Back-end : Python 3.11 + FastAPI
- LLM : Claude 3.5 Sonnet (Anthropic) pour la génération et l'extraction structurée
- Base vectorielle : PostgreSQL pgvector pour la recherche sémantique
- Front-end : React 18 + TypeScript
- Infrastructure : Azure France Central, Docker, Kubernetes
- Sécurité : chiffrement AES-256, SSO Azure AD, audit trail complet, conformité RGPD

**Fonctionnalités clés :**
- Assistant conversationnel en langage naturel avec citation des sources documentaires
- Extraction automatique des clauses clés des contrats entrants (parties, montants, échéances, clauses de résiliation)
- Détection des clauses atypiques ou à risque avec niveau d'alerte
- Génération automatique d'un rapport de revue contractuelle en PDF

### Résultats obtenus
- Temps de recherche documentaire réduit de 3h à 25 min par juriste par jour
- Taux de couverture documentaire : 98 % du corpus indexé dès la mise en production
- Adoption : 100 % des juristes utilisateurs actifs à 6 semaines du déploiement
- Économie estimée : 140 000 € par an en heures juristes libérées

### Organisation projet
- Durée : 6 mois (cadrage, développement, pilote, production)
- Équipe : 1 chef de projet, 1 consultant IA/RAG, 2 développeurs full-stack, 1 ingénieur DevOps, 1 QA
- Budget : 220 000 € HT

### Enseignements clés
La qualité du chunking documentaire (découpage par section juridique plutôt que par nombre de tokens) a été le facteur décisif pour la précision des réponses. La validation humaine systématique des documents à faible score de confiance a maintenu un niveau de fiabilité élevé.

---

## Cas #2 : Horizon Protection — Extranet partenaires pour réseau de courtiers

### Contexte client
Mutuelle santé et prévoyance collective, 4 200 entreprises clientes, réseau de 340 courtiers. Les demandes d'adhésion collective transitaient intégralement par email avec pièces jointes Word, ressaisies manuellement dans le système de gestion. Délai de traitement moyen : 10 jours. Taux d'erreur de saisie : 12 %.

### Solution déployée
Extranet partenaires permettant la saisie, le dépôt de pièces, le suivi en temps réel et la messagerie contextuelle, avec back-office gestionnaire et intégration au SI interne.

**Stack technique :**
- Front-end : React 18 + TypeScript, interface responsive
- Back-end : Java Spring Boot, API REST documentée
- Base de données : PostgreSQL 15
- Authentification : SSO Azure Active Directory (SAML 2.0)
- Intégrations : API référentiel partenaires + API création dossier CEGID Mutuelle
- CI/CD : GitHub Actions, environnements DEV / Recette / Production séparés
- Infrastructure : Azure App Service, Azure France Central

**Fonctionnalités clés :**
- Formulaire de souscription dynamique avec sauvegarde brouillon
- Dépôt et contrôle de cohérence des pièces justificatives
- Cycle de vie du dossier (brouillon → soumis → en analyse → validé → actif)
- Messagerie contextuelle par dossier
- Back-office gestionnaire avec file de traitement et tableau de bord manager

### Résultats obtenus
- Délai de traitement réduit de 10 jours à 2,5 jours
- Taux d'erreur de saisie réduit de 12 % à 1,8 %
- Réduction des échanges email non structurés de 70 %
- 85 % des courtiers actifs sur le portail à 3 mois du déploiement

### Organisation projet
- Durée : 8 mois (méthode agile, sprints de 2 semaines, recette progressive avec panel de courtiers)
- Équipe : 1 chef de projet, 2 développeurs full-stack, 1 UX designer, 1 QA
- Budget : 310 000 € HT

### Enseignements clés
La recette progressive avec un panel de 15 courtiers pilotes a permis d'identifier 23 points d'amélioration UX avant le déploiement général, évitant une refonte post-production coûteuse. L'accès anticipé aux API du SI client a été un facteur critique.

---

## Cas #3 : Groupe Prévoyance Régionale — Tableau de bord décisionnel et pilotage commercial

### Contexte client
Acteur de la prévoyance collective, 18 000 entreprises clientes, 280 agents commerciaux sur 22 agences. Absence d'outil de pilotage commercial consolidé : les données d'activité étaient extraites manuellement depuis 3 systèmes (CRM, ERP, tableurs Excel). Production des rapports mensuels : 2 jours par mois pour l'équipe direction.

### Solution déployée
Plateforme décisionnelle Power BI multi-sources avec ETL automatisé et espace de pilotage sécurisé pour les managers et directeurs régionaux.

**Stack technique :**
- Décisionnel : Power BI Service (tenant Microsoft 365 client)
- ETL : Python + Azure Data Factory pour l'alimentation depuis les 3 sources
- Modèle de données : star schema avec couche sémantique documentée
- Sources intégrées : CRM Salesforce (API REST), ERP Sage 100c (SQL Server), export Excel automatisé
- Rafraîchissement : schedulé toutes les 4 heures en heures ouvrées
- Sécurité : Row-Level Security Power BI (accès restreint par agence et par niveau hiérarchique)

**Livrables :**
- 4 tableaux de bord (direction nationale, directeur régional, manager agence, agent)
- Dictionnaire des 38 indicateurs avec formules, périmètres et règles de calcul
- Automatisation des rapports mensuels PDF (envoi automatique par email)
- Formation de 22 managers et 4 administrateurs

### Résultats obtenus
- Production du rapport mensuel : de 2 jours à 15 minutes (automatisée)
- Temps d'accès aux indicateurs commerciaux : de 48h à temps réel
- Adoption : 94 % des managers utilisateurs hebdomadaires à 2 mois

### Organisation projet
- Durée : 4 mois
- Équipe : 1 chef de projet, 2 data analysts/BI, 1 data engineer, 1 UX
- Budget : 95 000 € HT

### Enseignements clés
La définition partagée des indicateurs avant tout développement (atelier de gouvernance avec la direction financière et la direction commerciale) a évité 3 itérations correctives sur les formules de calcul. Les tableaux de bord non utilisés sont systématiquement ceux dont les KPI n'ont pas été co-construits avec les utilisateurs finaux.

---

## Tableau comparatif — Quand citer chaque référence

| Critère de l'AO | Référence à citer |
|---|---|
| IA documentaire, RAG, LLM, direction juridique | Cas #1 — Mutuelle Nova |
| Extranet partenaires, portail courtiers, workflow dossiers | Cas #2 — Horizon Protection |
| BI, Power BI, pilotage commercial, tableaux de bord | Cas #3 — Prévoyance Régionale |
| Secteur assurance / mutuelle (générique) | Cas #1 ou #2 selon techno demandée |
| Intégration SI, API, synchronisation multi-sources | Cas #2 ou #3 |
| React + FastAPI + Azure | Cas #1 |
| Java Spring Boot + PostgreSQL | Cas #2 |
| Python + Power BI + ETL | Cas #3 |

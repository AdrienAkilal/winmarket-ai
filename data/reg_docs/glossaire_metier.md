# Glossaire métier — Appels d'offres et ESN

Ce glossaire recense les termes clés rencontrés dans les appels d'offres et dans la pratique des ESN françaises. Il est destiné à ancrer la compréhension du LLM sur le vocabulaire métier utilisé dans les documents d'analyse.

---

## A — Termes liés aux marchés et à la procédure

**Appel d'offres (AO)**
Document émis par un client public ou privé pour solliciter des propositions de prestataires en vue de réaliser un projet ou une prestation. Synonymes : cahier des charges, dossier de consultation, RFP (Request for Proposal). Structure typique : contexte client, périmètre du besoin, critères d'évaluation, budget, délais, clauses contractuelles.

**MAPA (Marché à Procédure Adaptée)**
Procédure de passation de marché public dont les règles sont définies librement par l'acheteur dans les limites fixées par le Code de la commande publique. Utilisé pour les marchés dont le montant est inférieur aux seuils européens. Procédure plus souple et plus rapide que l'appel d'offres ouvert formalisé.

**Appel d'offres ouvert**
Procédure formalisée applicable au-delà des seuils européens dans laquelle tout opérateur économique peut soumettre une offre. Le cahier des charges est publié intégralement et les critères d'attribution sont définis à l'avance.

**Pouvoir adjudicateur / Donneur d'ordre**
Entité qui lance l'appel d'offres et qui choisira le prestataire. Peut être une administration publique (mairie, ministère, établissement public) ou une entreprise privée ayant choisi de formaliser sa mise en concurrence.

**Maître d'ouvrage (MOA)**
Le client — celui qui exprime le besoin, finance le projet et réceptionne les livrables. Il valide les jalons et signe le procès-verbal de recette.

**Maître d'œuvre (MOE)**
Le prestataire — nous — qui conçoit et réalise la solution pour le compte du MOA. Il est responsable de la conformité des livrables aux spécifications.

**CCTP (Cahier des Clauses Techniques Particulières)**
Document technique de l'AO décrivant précisément les exigences fonctionnelles et techniques du projet. C'est le document principal à analyser pour scorer l'adéquation technique.

**CCAP (Cahier des Clauses Administratives Particulières)**
Document administratif et contractuel de l'AO précisant les conditions d'exécution du marché : délais, pénalités, propriété intellectuelle, conditions de résiliation, modalités de facturation.

**DC1 / DC2**
Formulaires administratifs standard utilisés dans les marchés publics français. Le DC1 est la lettre de candidature (déclaration sur l'honneur). Le DC2 regroupe les informations sur le candidat (capacités économiques, références).

**DUME (Document Unique de Marché Européen)**
Formulaire européen permettant à un candidat de déclarer son aptitude à participer à un marché public, remplaçant une partie des documents administratifs habituels.

**Acte d'engagement**
Document signé par le candidat retenu formalisant son engagement à respecter les termes du marché. Sa signature marque le début du marché.

---

## B — Termes liés à l'évaluation et au scoring

**Critères d'attribution**
Critères pondérés utilisés par le client pour évaluer et classer les offres. Typiquement : valeur technique (40-50 %), prix (30-35 %), références et équipe (15-20 %), maintenance (5 %). La somme des pondérations est toujours égale à 100 %.

**Mémoire technique**
Document principal de la réponse à un AO, rédigé par le prestataire. Il présente la compréhension du besoin, la solution proposée, la méthodologie, l'équipe, le planning et les références. C'est le document évalué sur les critères techniques.

**Bordereau de prix (BPD)**
Document de décomposition du prix par poste, profil ou phase. Permet au client de comparer les offres et de détecter des anomalies de valorisation.

**Référence client**
Projet similaire réalisé antérieurement, présenté pour attester de l'expérience du prestataire. Une référence idéale mentionne : le client (ou le secteur si confidentiel), le périmètre technique, le budget, la durée, les résultats mesurables.

**Critère bloquant / éliminatoire**
Condition dont la non-satisfaction entraîne l'élimination automatique du candidat, indépendamment du score sur les autres critères. Typiquement : certification obligatoire absente, budget inférieur au minimum viable, incompatibilité réglementaire.

---

## C — Termes liés à l'organisation projet

**SLA (Service Level Agreement)**
Engagement contractuel de niveau de service. Exemples courants : disponibilité à 99,5 %, temps de réponse inférieur à 2 secondes, prise en charge des incidents de niveau 2 sous 4 heures. Le non-respect des SLA déclenche généralement des pénalités.

**TMA (Tierce Maintenance Applicative)**
Prestation de maintenance et d'évolution d'une application existante. Peut inclure : correction de bugs, petites évolutions fonctionnelles, supervision, support utilisateurs, mises à jour de sécurité.

**MOE déléguée / AMO**
Assistance à Maîtrise d'Ouvrage : rôle de conseil et d'accompagnement du client dans l'expression de son besoin, la rédaction du cahier des charges, le pilotage d'un appel d'offres ou la réception des livrables.

**Recette**
Phase de validation des livrables par le client avant acceptation définitive. La recette peut être fonctionnelle (le client teste les fonctionnalités) ou technique (validation des performances, de la sécurité, de l'infrastructure).

**PV de recette (Procès-verbal de recette)**
Document signé par le client attestant que les livrables sont conformes aux spécifications et acceptés. Sa signature conditionne généralement le déclenchement du paiement correspondant.

**Go-live / Mise en production**
Date à laquelle la solution est déployée en environnement de production et accessible aux utilisateurs finaux.

**Clause de réversibilité**
Clause contractuelle imposant au prestataire de fournir l'ensemble du code source, de la documentation technique et des scripts de déploiement en cas de fin de contrat, pour permettre au client de changer de prestataire sans dépendance.

---

## D — Termes techniques courants dans les AOs

**RAG (Retrieval-Augmented Generation)**
Architecture d'intelligence artificielle combinant la recherche documentaire sémantique et la génération de texte par un modèle de langage (LLM). Le système recherche les documents les plus pertinents dans un corpus, puis les fournit comme contexte au LLM pour générer une réponse sourcée et vérifiable.

**LLM (Large Language Model)**
Modèle de langage de grande taille capable de générer, analyser et transformer du texte. Exemples : Claude (Anthropic), GPT-4 (OpenAI), Mistral. Utilisé dans les projets d'IA générative, d'assistance documentaire, d'extraction structurée et de génération de contenus.

**Base vectorielle**
Base de données spécialisée dans le stockage et la recherche de représentations numériques (vecteurs) de textes. Permet la recherche sémantique : trouver des documents dont le sens est proche d'une requête, même si les mots exacts sont différents. Exemples : ChromaDB, Qdrant, PostgreSQL pgvector.

**API REST**
Interface permettant à deux systèmes informatiques de communiquer via des requêtes HTTP standardisées. Standard de facto pour l'intégration entre applications modernes.

**SSO (Single Sign-On)**
Mécanisme d'authentification unique permettant à un utilisateur de se connecter une seule fois pour accéder à plusieurs applications. Protocoles courants : SAML 2.0, OpenID Connect, OAuth2.

**RBAC (Role-Based Access Control)**
Contrôle d'accès basé sur les rôles : chaque utilisateur dispose d'un rôle (administrateur, gestionnaire, lecteur) qui détermine les fonctionnalités et les données auxquelles il peut accéder.

**CI/CD (Intégration et déploiement continus)**
Pratique DevOps consistant à automatiser les étapes de compilation, test et déploiement d'une application à chaque modification du code. Réduit les risques de régression et accélère les cycles de livraison.

**Docker / Kubernetes**
Docker : technologie de conteneurisation permettant d'empaqueter une application et ses dépendances dans une image portable et reproductible. Kubernetes : orchestrateur de conteneurs gérant le déploiement, la mise à l'échelle et la haute disponibilité des applications conteneurisées.

**PRA (Plan de Reprise d'Activité)**
Plan définissant les procédures pour restaurer un système informatique après une panne ou un sinistre. Caractérisé par deux métriques : RPO (Recovery Point Objective — perte de données maximale tolérée) et RTO (Recovery Time Objective — durée maximale d'interruption tolérée).

**MVP (Minimum Viable Product)**
Version minimale d'un produit contenant uniquement les fonctionnalités essentielles pour valider le concept et livrer une première valeur aux utilisateurs. Approche recommandée pour réduire les risques et accélérer les retours terrain.

---

## E — Certifications et réglementations

**RGPD**
Règlement Général sur la Protection des Données — réglementation européenne encadrant le traitement des données personnelles. Impose des obligations aux responsables de traitement et à leurs sous-traitants : minimisation des données, droits des personnes, registre des traitements, notification des violations.

**ISO 27001**
Norme internationale définissant les exigences d'un système de management de la sécurité de l'information (SMSI). Sa certification atteste que l'entreprise applique un processus formel de gestion des risques de sécurité. NovaSoft Conseil n'est pas certifiée à ce jour (voir fiche dédiée).

**SecNumCloud**
Qualification délivrée par l'ANSSI (Agence Nationale de la Sécurité des Systèmes d'Information) aux fournisseurs de services cloud offrant un niveau de sécurité et de souveraineté adapté aux données sensibles de l'État. NovaSoft ne détient pas cette qualification (voir fiche dédiée).

**HDS (Hébergeur de Données de Santé)**
Certification française obligatoire pour tout prestataire hébergeant des données de santé à caractère personnel. NovaSoft n'est pas certifiée HDS.

**Qualiopi**
Certification française attestant de la qualité des processus mis en œuvre par les organismes de formation professionnelle. NovaSoft est certifiée Qualiopi (voir fiche dédiée).

**OIV (Opérateur d'Importance Vitale)**
Entité publique ou privée dont les activités sont indispensables au fonctionnement de la nation (défense, énergie, transport, eau, santé, etc.). Les OIV sont soumis à des exigences de sécurité renforcées imposées par la LPM (Loi de Programmation Militaire). Les AOs émanant d'OIV comportent souvent des exigences SecNumCloud et ISO 27001 obligatoires.

---

## F — Abréviations de référence rapide

| Sigle | Signification |
|---|---|
| AO | Appel d'offres |
| MAPA | Marché à Procédure Adaptée |
| MOA | Maître d'ouvrage (client) |
| MOE | Maître d'œuvre (prestataire) |
| CCTP | Cahier des Clauses Techniques Particulières |
| CCAP | Cahier des Clauses Administratives Particulières |
| TMA | Tierce Maintenance Applicative |
| SLA | Service Level Agreement |
| PRA | Plan de Reprise d'Activité |
| RPO | Recovery Point Objective |
| RTO | Recovery Time Objective |
| RAG | Retrieval-Augmented Generation |
| LLM | Large Language Model |
| SSO | Single Sign-On |
| RBAC | Role-Based Access Control |
| MVP | Minimum Viable Product |
| CI/CD | Intégration et déploiement continus |
| OIV | Opérateur d'Importance Vitale |
| LPM | Loi de Programmation Militaire |
| ANSSI | Agence Nationale de la Sécurité des Systèmes d'Information |
| RGPD | Règlement Général sur la Protection des Données |
| DPA | Data Processing Agreement (accord de sous-traitance) |
| AIPD | Analyse d'Impact relative à la Protection des Données |
| HDS | Hébergeur de Données de Santé |
| DC1/DC2 | Formulaires administratifs marchés publics |
| DUME | Document Unique de Marché Européen |
| BPD | Bordereau de Prix Détaillé |

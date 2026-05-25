# Glossaire Métier - Appels d'Offres & ESN

## SECTION A: Termes Clients & Business

### Appel d'Offres (AO)
**Définition:** Document formalisé par un client/acheteur public ou privé décrivant un besoin et invitant des fournisseurs à proposer une solution.

**Synonymes:** Request for Proposal (RFP), Tender, Appel de compétition

**Structure typique:**
1. Contexte client
2. Besoin/scope détaillé
3. Critères évaluation
4. Budget/timeline
5. Clauses contractuelles

**Importance ESN:** Le "brief de projet" pour notre candidature

---

### Maître d'Ouvrage (MOA)
**Définition:** Client = la personne/entité qui lance l'AO et paiera pour livraison.

**Rôles typ:**
- Définir besoin
- Évaluer candidatures
- Accepter/Rejeter livrables
- Payer factures

**Antagonisme avec:** Maître d'Œuvre (nous = fournisseur)

---

### Maître d'Œuvre (MOE)
**Définition:** Nous = fournisseur service qui exécute le projet pour MOA.

**Responsabilités:**
- Comprendre besoin MOA
- Proposer solution
- Exécuter + livrer
- Supporter/Maintenir

---

### Scope (Périmètre)
**Définition:** Ensemble des fonctionnalités, modules, services inclus dans le projet.

**Exemple:** 
```
Scope inclus: Plateforme web + API + Document management
Scope exclus: Mobile app, Training utilisateurs final, Support 24/7
```

**Importance:** Clarté scope = 80% succès projet

**Related term:** Scope creep = ajouts non-contractuels

---

### SLA (Service Level Agreement)
**Définition:** Garantie contractuel sur performance service.

**Exemples:**
- "99.5% uptime" = Service dispo 99.5% du temps
- "<500ms response time p95" = 95% requêtes répondent en <500ms
- "Support L1 within 2 hours" = Réponse support rapide

**Importance:** Client besoin SLA pour budgétisation risks

---

### Go-Live (Mise en Prod)
**Définition:** Date officiel de lancement/utilisation réelle du système par client.

**Synonymes:** Production deployment, Launch date, Cutover

**Critiques:** Souvent repousser par 2-4 semaines (tests découvrent issues)

---

### Change Request (Changement)
**Définition:** Demande modification scope/design après contrat signé.

**Processus typique:**
1. Client demande change
2. ESN évalue impact (coût, délai)
3. Client approuve + budget additionnel
4. ESN exécute

**Impact:** Changement = €$ + temps additionnel

---

## SECTION B: Termes Techniques & Architecture

### Cloud
**Définition:** Infrastructure informatique externalisée chez provider (AWS, Azure, GCP).

**Avantages pour ESN response:**
- Scalabilité
- Maintenance réduite
- Coûts prévisibles (pay-as-you-go)

**Avantages pour Client:**
- CAPEX → OPEX
- Pas gérer infra physique

---

### RAG (Retrieval-Augmented Generation)
**Définition:** Technique IA combinant recherche documentaire (retrieval) + génération texte LLM.

**Processus:**
1. Utilisateur pose question
2. RAG search corpus documents pertinents
3. LLM reçoit question + documents comme contexte
4. LLM génère réponse basée contexte

**Importance croissante:** Utilisé pour customer support, documentation, RFP assistants

**Cf. notre projet:** Cas d'usage n°1 = plateforme IA RAG Mutuelle Nova

---

### API REST
**Définition:** Interface logiciel permettant 2 systèmes communiquer (requête/réponse HTTP).

**Usage ESN:** Intégration modules projet, "glue" entre systèmes legacy

**Client demande souvent:** "Votre solution expose une API REST?" = essayer intégrer avec leurs systèmes

---

### Kubernetes
**Définition:** Orchestrateur containers (gère scaling, deployment, monitoring).

**Usage ESN:** Pour applications haute-dispo, auto-scaling, multi-cloud

**Client demande si:** Infrastructure compliquée ou doit scaler beaucoup

---

### Docker
**Définition:** Containerization = packager app + dépendances dans image reproduisible.

**Importance:** Standard industrie maintenant (deployment + reproducibilité)

**Client demande:** Moins critiques que Kubernetes (plus simple)

---

### LLM (Large Language Model)
**Définition:** Model IA type GPT, Claude, LLaMA capable générer texte cohérent.

**Exemples:** OpenAI GPT-4, Anthropic Claude, Meta LLaMA

**Usage ESN:** Pour génération texte automatisée, analyse documents, chatbots

**Cf. notre projet:** Claude 3.5 utilisé pour extraction AO, scoring, generation candidature

---

### Vector Database
**Définition:** DB spécialisée stockant embeddings (représentations vectorielles texte/images).

**Usage RAG:** Pour recherche sémantique (trouver documents "similaires" même mots différents)

**Exemples:** Pinecone, Weaviate, PostgreSQL pgvector

---

### Embeddings
**Définition:** Représentation numérique (vecteur) d'un texte/mot capture signification sémantique.

**Exemple:** "chat" proche de "félin", loin de "mathématiques"

**Usage:** Recherche sémantique dans RAG

---

## SECTION C: Termes Réglementaires & Certifications

### RGPD (Règlement Général Protection Données)
**Définition:** Régulation UE protégeant données personnelles (nom, email, etc).

**Obligations ESN:**
- Consentement explicite avant traiter données
- Droit d'accès/suppression pour utilisateurs
- Breach notification <72h
- Data Protection Officer (DPO)

**Impact RFP:** Client demande RGPD compliance = nous devons prouver

---

### SecNumCloud
**Définition:** Label français pour certifier infrastructure cloud française sécurisée (vs. USA).

**Importance France/Public:** Obligatoire pour gouvernement, certains secteurs (santé, défense)

**Processus certification:** Audit annuel, très rigoureux (3-4 mois)

**Impact RFP:** Si client France + données sensibles → probably demande SecNumCloud

---

### HDS (Hébergeur Données Santé)
**Définition:** Certification française pour fournisseurs hébergeant données santé (HIPAA français).

**Obligation si:** Client = Hôpital, pharmacie, etc.

**Spécificités:** Chiffrement mandatory, audit annuel, disaster recovery plan requis

---

### ISO 27001
**Définition:** Standard international pour Information Security Management System (ISMS).

**Coverage:** Policies, risk management, incident response, etc.

**Duration:** Audit annuel, certification 3 ans

**Importance:** Demandé souvent par clients enterprise/secure

---

### Qualiopi
**Définition:** Certification française pour organisme formation professionnelle.

**Rôle ESN:** Si nous offrons formation/upskilling dans notre solution

**Process:** Audit externe, très document-heavy

---

### SOC 2 (System and Organization Controls)
**Définition:** Standard américain pour fournisseurs service (security, availability, processing integrity).

**Importance:** Demandé par clients USA ou équivalent ISO 27001

---

### Compliance
**Définition:** Conformité = respecter lois/standards applicables.

**Exemple:** "Solution doit être RGPD-compliant" = solution respecte RGPD

**Impact ESN:** Assurez conformité = coût + délai additionnel

---

## SECTION D: Termes Contractuels & Commerciaux

### Budget Estimé
**Définition:** Montant client anticipe pour projet.

**Risques ESN:**
- Trop bas = perte financière
- Trop haut = client hésite (accept pas candidature)
- Vague ("à discuter") = Scope creep risk

**Notre job:** Analyser si budget = réaliste pour scope

---

### Timeline / Durée Projet
**Définition:** Durée estimée du projet (ex: 12 mois).

**Importance:** Impacte team sizing, resource allocation

**Risk:** Client donne délai trop court = qualité souffre

---

### Deadline Réponse
**Définition:** Date limite soumettre candidature à client.

**Importance critique:** Manquer deadline = candidature rejetée automatique

**Typ range:** J+14 à J+45 après publication AO

---

### Penalty / Pénalité
**Définition:** € perte si ESN ne respecte pas engagement (retard, bug, SLA manquée).

**Exemple:** "Retard 1 jour = 1% budget penalty"

**Importance:** Haut penalties = dissuade bad projects

---

### Fixed-Price vs. Time & Materials
**Définition:** 2 modèles facturation
- **Fixed-Price:** Budget maximal défini à l'avance (client protégé, ESN risque)
- **Time & Materials:** Facturer par heure travaillée (ESN protégé, client risque)

**AO type:** Fixed-price (client contrôle budget)

**Implication ESN:** Estimation très précise nécessaire

---

### Non-Disclosure Agreement (NDA)
**Définition:** Contrat liant ESN garder infos client confidentiel.

**Typ duration:** 3-5 ans

**Importance:** Client partage secrets → NDA obligatoire

---

### Intellectual Property (IP)
**Définition:** Propriété code/designs créés pour client.

**Clarifications typ:**
- Client propriétaire = client "owns" code créé
- ESN retiens license = ESN peut réutiliser pour autres clients
- Hybrid = Mix (client owns app, ESN owns components réutilisables)

**Impact:** Enjeu legal/commercial important

---

## SECTION E: Termes Processus & Méthodologie

### Agile / Scrum
**Définition:** Méthodologie itérative (sprints 2 semaines) vs. Waterfall (phases séquentielles).

**Avantages Agile:**
- Feedback rapide
- Changes faciles
- Client engagé

**Client demande:** 80% AO modernes demandent Agile

---

### Sprint
**Définition:** Cycle développement Agile (typ 2 semaines).

**Contenu:**
- Planning (quel travail ce sprint)
- Daily standups (15 min status)
- Development
- Review (demo client)
- Retrospective (amélioration)

---

### MVP (Minimum Viable Product)
**Définition:** Version minimal du produit contenant features core seulement.

**Usage:** Livrer rapido, tester avec vrai users, puis ajouter features

**Client demande souvent:** "Pouvez-vous faire MVP d'abord?"

---

### UAT (User Acceptance Testing)
**Définition:** Client teste solution avant acceptance final (go-live).

**Duration:** Typ 2-4 semaines

**Importance:** Client rejette si UAT fails → project delayed

---

### DevOps
**Définition:** Culture + practices automatiser développement, test, deployment.

**Includes:** CI/CD pipelines, infrastructure-as-code, monitoring

**Client demande si:** Besoin déployer souvent (ex: SaaS)

---

### KPI (Key Performance Indicator)
**Définition:** Métrique business mesurant succès (ex: temps traitement, coût, satisfaction).

**Usage:** Montrer solution ROI (client satisfied) vs. coût

---

## SECTION F: Abréviations Courantes

| Abrév | Signification | Usage |
|-------|---------------|-------|
| AO | Appel d'Offres | "Répondre à un AO" |
| RFP | Request for Proposal | Anglophone = AO |
| MOA | Maître d'Ouvrage | Client |
| MOE | Maître d'Œuvre | Nous = fournisseur |
| SLA | Service Level Agreement | Garanties |
| API | Application Programming Interface | Intégration |
| REST | Representational State Transfer | Type d'API |
| RAG | Retrieval-Augmented Generation | IA + search |
| LLM | Large Language Model | GPT, Claude, etc |
| MVP | Minimum Viable Product | Version réduite |
| UAT | User Acceptance Testing | Tests client |
| KPI | Key Performance Indicator | Métriques |
| CI/CD | Continuous Integration/Deployment | Deployment automation |
| RGPD | Regulation Protection Données | Compliance données |
| SaaS | Software as a Service | Cloud software |
| IaaS | Infrastructure as a Service | Cloud infrastructure |
| PaaS | Platform as a Service | Cloud platform |
| JSON | JavaScript Object Notation | Format données |
| SQL | Structured Query Language | Database query |
| NoSQL | Non-relational SQL | Database type |
| DBA | Database Administrator | DB specialist |
| QA | Quality Assurance | Testing |
| PoC | Proof of Concept | Prototype |
| Pilot | Version test limité | Limited rollout |

---

## SECTION G: Quick Reference - Quand Utiliser Chaque Terme

### En répondant "Certification request":
"Nous sommes **ISO 27001 certified** et **RGPD-compliant**. 
Déploiement sur **infrastructure SecNumCloud-qualified**."

### En répondant "Methodology":
"Approche **Agile/Scrum** avec sprints 2-semaines. 
**CI/CD pipelines** pour **continuous deployment**.
**UAT client** à la fin pour acceptance."

### En répondant "Architecture":
"Architecture **REST API** avec **Docker containers**, 
orchestrés via **Kubernetes** en production. 
Données stockées **Vector DB** pour **RAG searches**."

### En répondant "Risk mitigation":
"Penalty clauses **capped à 10%** pour mutual protection. 
**SLA 99.5%** realistic pour infrastructure. 
**Change management process** défini pour scope clarity."

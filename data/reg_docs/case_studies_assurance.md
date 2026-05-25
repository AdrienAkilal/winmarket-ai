# Études de Cas - Secteur Assurance

## Cas #1: Mutuelle Nova - Plateforme IA Documentaire Juridique

### Contexte Client
- **Type:** Mutuelle d'assurance santé, 50k adhérents
- **Problématique:** Traitement manuel de 500+ documents juridiques/mois par équipe de 3 juristes
- **Enjeu:** Réduire temps traitement de 2 jours à 2 heures par document, tout en garantissant confidentialité absolue

### Solution Déployée
**Stack Technologique:**
- Backend: Python 3.11 + FastAPI
- LLM: Claude 3.5 Sonnet fine-tuned sur corpus juridique Mutuelle
- RAG: Vector DB PostgreSQL pgvector
- Infra: AWS ECS (Fargate) + RDS PostgreSQL
- Sécurité: AES-256 encryption at-rest/in-transit, SecNumCloud certified

**Architecture Spécifique:**
- Document chunking strategy: Par section juridique (clauses de non-responsabilité, conditions d'adhésion, etc)
- Retrieval: Hybrid search (BM25 + semantic embeddings)
- LLM prompt: 3-shot examples of correct extraction + explicit instructions on contradictions handling
- Post-processing: Validation rules (check "Date signature < Date effective") + human review queue

### Résultats
- **Timeline:** 11 mois (M1: discovery, M2-M10: dev+testing, M11: UAT+deployment)
- **Équipe:** 1 Chef Projet + 2 Lead Techs + 4 Developers + 1 QA
- **Performance:** 98% accuracy on document classification, 2h processing time (vs 2 days manual)
- **Cost Savings:** €180k/year in reduced juriste hours
- **Satisfaction Client:** 9.2/10 (NPS)

### Certifications & Compliance
- **Certifications:** SecNumCloud, ISO 27001, RGPD compliance validated
- **Data Residency:** France (aws.eu-west-1)
- **Audit:** Annual SecNumCloud audit passed without findings
- **Incident:** Zero security incidents in 18 months production

### Key Learnings
1. **Prompt engineering is critical:** First iteration accuracy was 65%, after 3 rounds of prompt refinement → 98%
2. **Chunking strategy matters:** Default chunking (500 tokens) led to context loss. Section-based chunking fixed it.
3. **Human-in-the-loop:** Don't automate 100%. Queue ambiguous documents (10% of volume) for manual review.
4. **Client expectation management:** Promised 95% → delivered 98% (pleasant surprise)

### References Disponibles
- Contact: Marie Dupont, CIO Mutuelle Nova (marie.dupont@mutuelle-nova.fr)
- Case study detaillée: 12 pages, architecture diagrams, performance charts
- Demo access: Environment UAT avec 50 documents test

---

## Cas #2: Horizon Protection - Plateforme Extranet Partenaires

### Contexte Client
- **Type:** Assurance IARD, 200+ partenaires (agents, courtiers)
- **Problématique:** Plateforme legacy (1998, ColdFusion) lente, pas de mobile, mauvaise UX
- **Enjeu:** Refonte complète en cloud, mobile-first, API-centric architecture

### Solution Déployée
**Tech Stack:**
- Frontend: React 18 + TypeScript + Tailwind CSS (responsive, PWA-ready)
- Backend: Node.js + Express + GraphQL API
- Database: PostgreSQL + Redis (session cache)
- Infra: Kubernetes on AWS EKS
- Authentication: OAuth2 + Keycloak

**Modules Clés:**
1. Dashboard: Real-time KPIs (primes en cours, taux acception, etc)
2. Document Management: Upload contrats, signatures électroniques
3. Reporting: Custom export Excel/PDF
4. Mobile App: iOS + Android via React Native

### Résultats
- **Timeline:** 9 mois (4 sprints de 2 semaines/mois)
- **Équipe:** 1 PM + 2 Lead Dev (BE + FE) + 5 Developers + 2 QA
- **Adoption:** 85% partenaires active 6 mois post-launch
- **Performance:** 99.8% uptime, <500ms response time p95
- **Cost:** €45k/month cloud infra (savings vs legacy: €15k/month)

### Metrics de Succès
- Document processing time: 10 min → 1 min
- Mobile conversion rate: 0% → 35%
- Support tickets: 150/month → 40/month (70% reduction)

### Risks & Mitigation
- **Risk:** 200+ partenaires concurrent usage → capacity planning
  - Mitigation: Load testing with 1000 simultaneous users, auto-scaling Kubernetes
- **Risk:** Data migration from legacy system (1M contracts)
  - Mitigation: Phased migration + parallel run for 2 weeks

---

## Cas #3: Assur'Complet - Refonte Infrastructure SAP Souveraine

### Contexte Client
- **Type:** Assurance multirisque (auto, habitation, santé), 150 salariés
- **Problématique:** SAP on-premises (aging hardware, maintenance coûteux). Besoin cloud mais avec contrainte régalienne
- **Enjeu:** Migration SAP → cloud public (critère national français) tout en maintenant conformité SecNumCloud

### Solution Déployée
- **Source:** SAP ECC 6.0 (legacy ERP)
- **Target:** SAP S/4HANA on Azure (France Central datacenter)
- **Middleware:** MuleSoft Anypoint pour intégrations custom

### Approche Technique
1. **Phase 0:** Application readiness (code cleanup, simplification)
2. **Phase 1:** Build S/4HANA environment + data model
3. **Phase 2:** Data migration (3-way cutover: SAP→target, validate, rollback available)
4. **Phase 3:** UAT + go-live
5. **Phase 4:** Optimization (memory tuning, batch job scheduling)

### Résultats
- **Timeline:** 16 mois
- **Équipe:** 1 Program Manager + 4 SAP consultants + 5 developers (MuleSoft) + 2 DBAs
- **Go-live:** Zero downtime migration (30 min cutover window)
- **Data:** 10M contracts migrated, data validation 99.9% match
- **Cost Savings:** €80k/year in licensing + €120k/year in maintenance

### Certification Achievements
- SecNumCloud qualified provider (Azure France Central)
- RGPD compliance: DPA signed, data controller named
- Audit ISO 27001: Passed with 0 findings

---

## Comparaison Cas / Sélection pour RFP

| Critère | Plateforme IA | Extranet Partenaires | Migration SAP |
|---------|---------------|----------------------|------------------|
| **Complexité Tech** | Haute (LLM, embeddings) | Moyenne (CRUD full-stack) | Très Haute (ERP) |
| **Timeline Optimal** | 12+ mois | 8-10 mois | 15-20 mois |
| **Team Size** | 7-8 persons | 7-8 persons | 10-15 persons |
| **Budget Range** | €400-600k | €200-400k | €800k-1.2M |
| **When to Sell** | Client has IA strategy | Legacy app modernization | ERP migration planning |
| **Success Factor** | Prompt quality + team expertise | UX/Product design | Change management + testing rigor |

### Utilisation dans RFP Responses

**Si RFP mentionne:** "IA Documentaire, RAG, confidentialité stricte"
→ Cite: **Cas #1 Mutuelle Nova** (exact match)

**Si RFP mentionne:** "Refonte UI/UX, mobile-first, partenaires externes"
→ Cite: **Cas #2 Horizon Protection** (similar stakeholder management)

**Si RFP mentionne:** "SAP cloud migration, SecNumCloud, France"
→ Cite: **Cas #3 Assur'Complet** (infrastructure + compliance expertise)

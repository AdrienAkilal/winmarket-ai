from src.core.models import AOContext, CompanyProfile, RAGEvidence, CapacityResult, CriterionScore, ScoringResult
from src.core.config import SCORING_THRESHOLD_GO, SCORING_THRESHOLD_SOUS_RESERVE, LLM_TEMPERATURE_FACTUAL
from typing import Optional


class ScoringEngine:
    weights = {
        "Adequation expertise":     20,
        "References similaires":    15,
        "Disponibilite equipe":     10,
        "Rentabilite estimee":      10,
        "Faisabilite delai":        10,
        "Certifications requises":  10,
        "Complexite technique":      5,
        "Connaissance secteur":      5,
        "Potentiel commercial":      5,
        "Risque contractuel":        5,
        "Solidite client":           3,
        "Valeur strategique":        2,
    }
    labels = {
        "Adequation expertise":     "Adequation expertise",
        "References similaires":    "References similaires",
        "Disponibilite equipe":     "Disponibilite equipe",
        "Rentabilite estimee":      "Rentabilite estimee",
        "Faisabilite delai":        "Faisabilite delai",
        "Certifications requises":  "Certifications requises",
        "Complexite technique":     "Complexite technique",
        "Connaissance secteur":     "Connaissance secteur",
        "Potentiel commercial":     "Potentiel commercial",
        "Risque contractuel":       "Risque contractuel",
        "Solidite client":          "Solidite client",
        "Valeur strategique":       "Valeur strategique",
    }
    label_display = {
        "Adequation expertise":     "Ad\u00e9quation expertise",
        "References similaires":    "R\u00e9f\u00e9rences similaires",
        "Disponibilite equipe":     "Disponibilit\u00e9 \u00e9quipe",
        "Rentabilite estimee":      "Rentabilit\u00e9 estim\u00e9e",
        "Faisabilite delai":        "Faisabilit\u00e9 d\u00e9lai",
        "Certifications requises":  "Certifications requises",
        "Complexite technique":     "Complexit\u00e9 technique",
        "Connaissance secteur":     "Connaissance secteur",
        "Potentiel commercial":     "Potentiel commercial",
        "Risque contractuel":       "Risque contractuel",
        "Solidite client":          "Solidit\u00e9 client",
        "Valeur strategique":       "Valeur strat\u00e9gique",
    }
    mastered = {
        "react", "angular", "vue", "java", "spring", "python", "django", "fastapi",
        ".net", "c#", "azure", "aws", "gcp", "docker", "kubernetes", "power bi",
        "postgresql", "oracle", "sql server", "ia", "rag", "llm", "node", "nodejs",
        "typescript", "devops", "ci/cd", "terraform", "ansible"
    }
    certs_ok = {"iso 27001", "rgpd", "qualiopi", "iso27001"}

    def score(
        self,
        ao: AOContext,
        company: CompanyProfile,
        evidences: list,
        capacity: CapacityResult,
    ) -> ScoringResult:
        import re

        # --- Adequation expertise ---
        techs = {t.lower() for t in ao.technologies_demandees + ao.competences_requises}
        matched = len([t for t in techs if t in self.mastered])
        if not techs:
            expertise, exp_just = 80, "Pas de technologies specifiques identifiees."
        else:
            ratio = matched / len(techs)
            expertise = round(100 * ratio, 1)
            exp_just = f"{matched}/{len(techs)} competences couvertes par l'ESN."

        # --- References ---
        n_ev = len(evidences)
        avg_sim = sum(min(e.score, 1.0) for e in evidences) / max(n_ev, 1)
        ref_score = min(100, 30 + n_ev * 6 + avg_sim * 40)

        # --- Disponibilite ---
        dispo = 90 if capacity.equipe_disponible else 45

        # --- Rentabilite (budget) ---
        budget_val = ao.budget_estime or 0
        if budget_val == 0:
            budget, budget_just = 65, "Budget non communique — estimation a risque."
        elif budget_val >= 200_000:
            budget, budget_just = 90, f"Budget {budget_val:,.0f}\u20ac — tres rentable."
        elif budget_val >= 100_000:
            budget, budget_just = 80, f"Budget {budget_val:,.0f}\u20ac — rentabilite correcte."
        elif budget_val >= 60_000:
            budget, budget_just = 55, f"Budget {budget_val:,.0f}\u20ac — marge serree, attention aux depassements."
        else:
            budget, budget_just = 40, f"Budget {budget_val:,.0f}\u20ac — tres limite pour ce type de projet."

        # --- Faisabilite delai ---
        tight_deadline = bool(
            re.search(r"(?i)(8|6|4)\s+semaines|imper[ae]tif|aucun\s+report|d[eé]marrage\s+imper", ao.texte_source)
        )
        deadline = 45 if tight_deadline else 75
        delai_just = "Delai tres court ou impe\u0301ratif identifie\u0301." if tight_deadline else "Delai de livraison a confirmer."

        # --- Certifications ---
        cert_missing = [c for c in ao.certifications_obligatoires if c.lower() not in self.certs_ok]
        cert_score = 100 if not cert_missing else 20
        cert_just = ("Certifications obligatoires couvertes." if not cert_missing
                     else f"Certifications manquantes : {', '.join(cert_missing)}")

        # --- Complexite ---
        complexity = 80 if len(techs) <= 4 else (60 if len(techs) <= 7 else 40)
        comp_just = f"Stack de {len(techs)} technologies identifiees."

        # --- Secteur ---
        sector = 80 if company.secteur not in ("Non renseigne", "") else 65

        # --- Commercial ---
        commercial = 85 if budget_val >= 150_000 else (60 if budget_val >= 70_000 else 40)

        # --- Contractuel ---
        contractual = 60 if re.search(r"(?i)p[eé]nalit[eé]|garantie|sla", ao.texte_source) else 80

        # --- Solidite ---
        solidite = 85 if company.solidite_financiere in ("Bonne", "A verifier") else 60

        # --- Strategique ---
        strategic = 90 if any(t in techs for t in {"ia", "rag", "llm", "cloud", "azure", "aws", "data"}) else 70

        raw = {
            "Adequation expertise":    (expertise,   exp_just),
            "References similaires":   (ref_score,   f"{n_ev} elements probants dans le RAG (similarite moy. {avg_sim:.2f})."),
            "Disponibilite equipe":    (dispo,        capacity.commentaire),
            "Rentabilite estimee":     (budget,       budget_just),
            "Faisabilite delai":       (deadline,     delai_just),
            "Certifications requises": (cert_score,   cert_just),
            "Complexite technique":    (complexity,   comp_just),
            "Connaissance secteur":    (sector,       f"Secteur client : {company.secteur or 'a identifier'}."),
            "Potentiel commercial":    (commercial,   f"Potentiel commercial {'fort' if commercial >= 80 else 'moyen' if commercial >= 55 else 'faible'}."),
            "Risque contractuel":      (contractual,  "Clauses contraignantes detectees." if contractual < 75 else "Risque contractuel standard."),
            "Solidite client":         (solidite,     f"Profil client : {company.solidite_financiere}."),
            "Valeur strategique":      (strategic,    "Projet aligne avec positionnement IA/Data/Cloud." if strategic >= 85 else "Valeur strategique moderee."),
        }

        criteres = [
            CriterionScore(
                nom=self.label_display[k],
                poids=float(w),
                score=min(100.0, float(raw[k][0])),
                justification=raw[k][1],
            )
            for k, w in self.weights.items()
        ]

        global_score = round(sum(c.score * c.poids for c in criteres) / 100, 1)

        # Blocking rules
        blockers = []
        if cert_missing:
            blockers.append("Certification obligatoire absente : " + ", ".join(cert_missing))
        if ao.budget_estime is not None and ao.budget_estime < 50_000:
            blockers.append("Budget inferieur au seuil minimal de rentabilite ESN (50 000 EUR)")
        if capacity.charge_actuelle_pct > 95:
            blockers.append("Charge equipe superieure a 95% — impossible de demarrer")
        unknown_tech = [t for t in techs if t not in self.mastered]
        if len(unknown_tech) >= 4:
            blockers.append("Trop de technologies non maitrisees : " + ", ".join(unknown_tech[:5]))

        if blockers:
            decision = "NO-GO"
        elif global_score >= SCORING_THRESHOLD_GO:
            decision = "GO"
        elif global_score >= SCORING_THRESHOLD_SOUS_RESERVE:
            decision = "GO SOUS RESERVE"
        else:
            decision = "NO-GO"

        return ScoringResult(
            decision=decision,
            score_global=global_score,
            criteres=criteres,
            criteres_bloquants=blockers,
            forces=[c.nom for c in criteres if c.score >= 78][:5],
            faiblesses=[c.nom for c in criteres if c.score < 60][:5],
            risques=blockers or ["Valider la disponibilite reelle des ressources", "Confirmer les hypotheses budgetaires"],
            recommandations=self._build_recommendations(ao, decision, cert_missing, unknown_tech, tight_deadline, budget_val),
            evidence_pack=evidences,
            company_profile=company,
            capacity=capacity,
        )

    def _build_recommendations(self, ao, decision, cert_missing, unknown_tech, tight_deadline, budget_val):
        recs = []
        if decision == "NO-GO":
            if cert_missing:
                recs.append(f"Engager dès maintenant la procédure d'obtention {cert_missing[0]} — délai moyen 6-12 mois, requis pour répondre à ce type de marché")
            if unknown_tech:
                recs.append(f"Identifier un partenaire maîtrisant {', '.join(list(unknown_tech)[:2])} pour constituer un groupement sur les prochains AO similaires")
            recs.append(f"Maintenir la relation commerciale avec {ao.client} — se positionner sur le prochain lot ou la prochaine tranche")
        elif "RESERVE" in decision:
            if cert_missing:
                recs.append(f"Résoudre le point bloquant {cert_missing[0]} avant la date limite — valider avec la direction si une attestation d'engagement suffit")
            recs.append(f"Organiser une réunion avant-vente d'ici 48h pour valider le go définitif et affecter le chef de projet")
            if ao.deadline_reponse:
                recs.append(f"Lancer la rédaction du mémoire technique immédiatement — date limite : {ao.deadline_reponse}")
            else:
                recs.append(f"Lancer la rédaction du mémoire technique immédiatement en parallèle de la levée des réserves")
        else:  # GO
            recs.append(f"Désigner le chef de projet et affecter l'équipe technique dans les 48h")
            if ao.deadline_reponse:
                recs.append(f"Préparer le mémoire technique en priorisant les références {ao.secteur or 'sectorielles'} — date limite : {ao.deadline_reponse}")
            else:
                recs.append(f"Préparer le mémoire technique en priorisant les références {ao.secteur or 'sectorielles'} similaires")
            if tight_deadline:
                recs.append("Alerter le management sur le délai serré — mobiliser les ressources immédiatement")
            elif budget_val and budget_val < 100_000:
                recs.append(f"Revalider la rentabilité avec le contrôleur de gestion — budget de {budget_val:,.0f}€ laisse peu de marge")
            else:
                recs.append("Préparer une proposition de valeur différenciante sur 2-3 points clés identifiés dans l'analyse")
        return recs[:4]

    _SCORING_SYSTEM = (
        "Tu es directeur avant-vente dans une ESN française de taille intermédiaire (200-500 collaborateurs), "
        "spécialisée en transformation digitale, développement applicatif, data/IA, cloud et cybersécurité. "
        "Tu as 20 ans d'expérience en réponses aux appels d'offres publics et privés : tu as remporté plus de "
        "300 marchés et en as perdu autant. Tu sais exactement pourquoi on gagne ou perd un marché : adéquation "
        "de l'expérience client présentée, qualité et disponibilité de l'équipe, compétitivité prix, "
        "solidité méthodologique, et maîtrise des enjeux métier du client. "
        "Ton analyse est toujours ancrée dans les faits concrets de CET appel d'offres spécifique. "
        "Tu n'utilises jamais de formules génériques ou de langue de bois. "
        "Chaque justification, point fort, risque ou recommandation doit être directement rattaché "
        "aux éléments factuels présents dans le dossier."
    )

    def enrich_with_llm(self, ao: AOContext, result: ScoringResult, llm) -> ScoringResult:
        """Enrichit les justifications, forces, faiblesses et recommandations avec Claude."""
        if not llm.enabled:
            return result

        criteres_text = "\n".join([
            f"- {c.nom} ({int(c.poids)}%) : {c.score:.0f}/100 — {c.justification}"
            for c in result.criteres
        ])

        blockers_text = (
            "CRITÈRES BLOQUANTS DÉTECTÉS :\n" + "\n".join(f"  ⛔ {b}" for b in result.criteres_bloquants)
            if result.criteres_bloquants else "Aucun critère bloquant."
        )

        prompt = f"""Tu dois enrichir l'analyse de scoring d'un appel d'offres pour notre ESN. Voici le contexte complet :

═══════════════════════════════════════════════
INFORMATIONS SUR L'APPEL D'OFFRES
═══════════════════════════════════════════════
Titre          : {ao.titre}
Client         : {ao.client}
Secteur        : {ao.secteur or 'Non précisé'}
Budget estimé  : {f"{ao.budget_estime:,.0f} €" if ao.budget_estime else 'Non communiqué'}
Durée          : {f"{ao.duree_projet_mois} mois" if ao.duree_projet_mois else 'Non précisée'}
Technologies   : {', '.join(ao.technologies_demandees) or 'Non précisées'}
Compétences    : {', '.join(ao.competences_requises[:5]) or 'Non précisées'}
Livrables      : {', '.join(ao.livrables[:4]) or 'Non précisés'}
Contraintes    : {' | '.join(ao.contraintes[:4]) or 'Aucune identifiée'}
Certif. oblig. : {', '.join(ao.certifications_obligatoires) or 'Aucune'}

═══════════════════════════════════════════════
SCORES CALCULÉS PAR CRITÈRE
═══════════════════════════════════════════════
{criteres_text}

DÉCISION ALGORITHMIQUE : {result.decision}
SCORE GLOBAL           : {result.score_global}/100
{blockers_text}

═══════════════════════════════════════════════
TA MISSION
═══════════════════════════════════════════════
Enrichis cette analyse en produisant un JSON avec les champs suivants :

**"justifications"** — Objet clé/valeur où chaque clé est le nom exact d'un critère listé ci-dessus.
Chaque justification doit :
  • Être spécifique à CET appel d'offres (citer le client, le secteur, les technologies, le budget)
  • Expliquer pourquoi le score est ce qu'il est avec des arguments factuels
  • Faire 1 à 2 phrases denses, pas des généralités
  • ÉVITER : "Notre ESN maîtrise...", "Nous avons de l'expérience dans...", "Ce projet nécessite..."
  • PRÉFÉRER : "Le budget de 120 000 € sur 8 mois implique...", "La stack SAP/Azure exigée couvre 70% de nos certifications actuelles..."

**"forces"** — Liste de 3 à 5 points forts, chacun :
  • Directement lié à un élément factuel de l'AO (technologie, secteur, budget, délai, certification)
  • Formulé comme un argument commercial percutant, pas comme une description
  • Exemple à éviter : "Bonne adéquation technologique"
  • Exemple à privilégier : "Stack React/Python entièrement couverte par nos équipes certifiées, 3 projets similaires livrés en contexte {ao.secteur or 'sectoriel'}"

**"faiblesses"** — Liste de 2 à 4 points faibles, chacun :
  • Honnête et factuel (pas défensif, pas minimisé)
  • Incluant si possible une piste de mitigation en une phrase
  • ÉVITER les faiblesses fictives si le score est fort

**"recommandations"** — Liste de 3 actions concrètes et immédiatement actionnables par l'équipe avant-vente :
  • Formulées à l'impératif
  • Chiffrées ou datées si possible
  • Liées aux spécificités de CET appel (pas des conseils génériques)
  • Exemple : "Contacter {ao.client} en amont pour clarifier le périmètre du lot 2 avant la date limite du..."

**"risques"** — Liste de 2 à 3 risques projet identifiés :
  • Risques réels et spécifiques (pas "risque de dépassement de budget" sans justification)
  • Avec probabilité implicite (élevée/modérée/faible) et impact potentiel
  • Basés sur les contraintes, délais, certifications ou technologies de l'AO

Réponds UNIQUEMENT en JSON valide, sans texte avant ni après.
"""
        try:
            data = llm.json_complete(prompt, system=self._SCORING_SYSTEM, temperature=LLM_TEMPERATURE_FACTUAL, max_tokens=4000)
        except Exception:
            return result
        if not data:
            return result

        justs = data.get("justifications", {})
        for c in result.criteres:
            nom_norm = c.nom.lower().replace('é','e').replace('è','e').replace('ê','e').replace('à','a').replace('ù','u')
            for key, val in justs.items():
                key_norm = key.lower().replace('é','e').replace('è','e').replace('ê','e').replace('à','a').replace('ù','u')
                if key_norm in nom_norm or nom_norm in key_norm:
                    c.justification = val
                    break

        if data.get("forces"):
            result.forces = data["forces"]
        if data.get("faiblesses"):
            result.faiblesses = data["faiblesses"]
        if data.get("recommandations"):
            result.recommandations = data["recommandations"]
        if data.get("risques"):
            result.risques = data["risques"]

        return result

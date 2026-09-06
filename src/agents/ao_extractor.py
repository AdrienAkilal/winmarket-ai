import re
from pathlib import Path
from src.core.models import AOContext
from src.agents.llm_client import ClaudeClient
from src.core.content_preparation import wrap_untrusted_content
from src.core.config import LLM_TEMPERATURE_FACTUAL


def read_document(path: str) -> str:
    p = Path(path)
    if p.suffix.lower() == ".pdf":
        import fitz
        doc = fitz.open(path)
        return "\n".join(page.get_text("text") for page in doc)
    if p.suffix.lower() in [".txt", ".md"]:
        return p.read_text(encoding="utf-8", errors="ignore")
    if p.suffix.lower() == ".docx":
        from docx import Document
        d = Document(path)
        return "\n".join([para.text for para in d.paragraphs])
    return p.read_text(encoding="utf-8", errors="ignore")


def _find_budget(text: str):
    m = re.search(r"(\d{1,3}(?:[\s.]\d{3})+|\d{5,})\s*€", text)
    if not m:
        return None
    return float(re.sub(r"[\s.]", "", m.group(1)))


def _extract_technologies(text: str) -> list:
    vocab = [
        "React", "Angular", "Vue", "Java", "Spring", "Python", "Django", "FastAPI",
        ".NET", "C#", "Azure", "AWS", "GCP", "Docker", "Kubernetes", "Power BI",
        "PostgreSQL", "Oracle", "SQL Server", "IA", "RAG", "LLM", "Node", "NodeJS",
        "TypeScript", "DevOps", "Terraform", "Ansible", "SAP", "SharePoint"
    ]
    low = text.lower()
    return sorted({v for v in vocab if v.lower() in low})


def _extract_certifications(text: str) -> list:
    """
    Extract MANDATORY certifications only — skip mentions of 'non requis',
    'non obligatoire', 'apprecie mais non obligatoire', etc.
    """
    certs_to_check = {
        "SecNumCloud": [
            r"(?i)secnumcloud[^\n]{0,60}(?:requis|obligatoire|exig[eé])",
            r"(?i)secnumcloud\s+(?:est\s+)?(?:requis|obligatoire|exig[eé])",
            r"(?i)qualification\s+secnumcloud\s+(?:est\s+)?(?:requis|obligatoire)",
            r"(?i)certifi[eé]\s+secnumcloud",
            r"(?i)h[eé]bergement\s+(?:qualifi[eé]|certifi[eé])\s+secnumcloud",
            r"(?i)environnement\s+qualifi[eé]\s+secnumcloud",
            r"(?i)secnumcloud\s+ou\s+partenariat",
            r"(?i)qualification\s+secnumcloud",
            r"(?i)preuve\s+de\s+qualification\s+secnumcloud",
        ],
        "HDS": [
            r"(?i)hds\s+(?:est\s+)?(?:requis|obligatoire|exig[eé])",
            r"(?i)herbergeur\s+de\s+donn[eé]es\s+de\s+sant[eé].*obligatoire",
            r"(?i)h[eé]bergeur\s+de\s+donn[eé]es\s+de\s+sant[eé][^\n]{0,80}obligatoire",
        ],
        "ISO 27001": [
            r"(?i)iso\s*27001\s+(?:est\s+)?(?:requis|obligatoire|exig[eé]e?)",
            r"(?i)certif\w*\s+iso\s*27001\s+(?:est\s+)?(?:requis|obligatoire)",
            r"(?i)iso\s*27001[^\n]{0,60}(?:requis|obligatoire|exig[eé])",
        ],
        "Qualiopi": [
            r"(?i)qualiopi\s+(?:est\s+)?(?:requis|obligatoire|exig[eé]e?)",
        ],
        "RGPD": [
            r"(?i)rgpd\s+(?:est\s+)?(?:requis|obligatoire|conformit[eé]\s+rgpd\s+obligatoire)",
            r"(?i)rgpd[^\n]{0,60}(?:n[eé]cessaire|requis|obligatoire|exig[eé])",
        ],
    }

    # Negative patterns — if any of these appear near the cert mention, skip it
    neg_patterns = [
        r"non\s+requis",
        r"non\s+obligatoire",
        r"pas\s+requis",
        r"pas\s+exig[eé]",
        r"appr[eé]ci[eé]e?\s+(?:mais\s+)?non",
        r"souhait[eé]e?\s+(?:mais\s+)?non",
        r"n'est\s+pas\s+requis",
        r"n'est\s+pas\s+obligatoire",
    ]

    found = []
    for cert, patterns in certs_to_check.items():
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                # Negation applies to the matched requirement line only; a
                # nearby optional certification must not cancel this one.
                start = text.rfind("\n", 0, m.start()) + 1
                line_end = text.find("\n", m.end())
                end = len(text) if line_end < 0 else line_end
                window = text[start:end]
                is_negated = any(re.search(neg, window) for neg in neg_patterns)
                if not is_negated:
                    found.append(cert)
                    break

    return found


_EXTRACTION_SYSTEM = """Tu es un analyste avant-vente senior dans une ESN française avec 15 ans d'expérience sur les marchés publics et privés IT. Tu maîtrises parfaitement la terminologie des appels d'offres (CCTP, CCAP, RC, DUME, DC1/DC2, BPU, DQE, AE), les procédures de marchés publics (MAPA, appel d'offres ouvert, restreint, dialogue compétitif) et les pratiques du secteur privé.

Ton rôle est d'extraire avec une précision chirurgicale les informations structurées d'un appel d'offres. Tu ne déduis pas, tu n'inventes pas, tu n'extrapolles pas. Si une information n'est pas explicitement présente dans le document, tu retournes null ou une liste vide selon le type attendu. Ta valeur ajoutée est dans la précision et la fiabilité de l'extraction, pas dans l'interprétation."""

_EXTRACTION_USER = """Analyse l'appel d'offres suivant et extrais toutes les informations structurées. Réponds UNIQUEMENT en JSON valide, sans texte avant ni après.

RÈGLES D'EXTRACTION PAR CHAMP :

**titre** : Titre exact du marché ou de la consultation. Prend le titre officiel s'il existe (souvent en en-tête ou après "Objet du marché"). Max 200 caractères. Jamais null.

**client** : Nom complet de l'entité acheteuse (pouvoir adjudicateur, maître d'ouvrage, donneur d'ordre). Inclure la forme juridique si présente (SAS, SA, Métropole, EPCI, etc.). Jamais null.

**secteur** : Secteur d'activité du client parmi : Santé, Finance/Assurance, Industrie, Collectivité/Public, Défense, Énergie, Transport, Retail/Commerce, Éducation, Immobilier, Télécoms, Autre. Déduire du contexte si non explicitement mentionné.

**budget_estime** : Montant en euros, nombre décimal ou null. Chercher : "budget", "enveloppe", "montant estimé", "valeur du marché", "prix max", "plafond". Formats acceptés : "150 000 €", "150K€", "150.000 euros", "0,15 M€". Ignorer les seuils de procédure (seuils européens). Si fourchette, prendre la valeur médiane. Si "confidentiel" ou absent → null.

**deadline_reponse** : Date limite de remise des offres, au format "DD/MM/YYYY" si trouvée, sinon description textuelle exacte ("fin du mois prochain", "dans 3 semaines"). null si absent.

**duree_projet_mois** : Durée d'exécution du marché en mois entier. Convertir : "1 an" → 12, "18 mois" → 18, "2 ans" → 24, "36 semaines" → 9. null si absent.

**technologies_demandees** : Liste des technologies, frameworks, langages, plateformes et outils techniques EXPLICITEMENT mentionnés. Normaliser les noms (ex: "React.js" → "React", "node.js" → "NodeJS"). Ne pas inventer de technologies non citées. Liste vide si aucune technologie précisée.

**competences_requises** : Liste des compétences fonctionnelles, métier et organisationnelles explicitement demandées (ex: "gestion de projet Agile", "conduite du changement", "expertise SIRH", "connaissance réglementation bancaire"). Différent des technologies : ici on parle de savoir-faire, méthodes, domaines métier. Liste vide si non précisé.

**questions_client** : Liste des questions ou exigences auxquelles le prestataire doit répondre dans son offre (souvent dans un "Cahier des charges", "Questions mémoire technique", "Critères de notation"). Copier les questions mot pour mot si possible. Liste vide si aucune question explicite.

**livrables** : Liste des livrables, rendus et productions attendus du prestataire (ex: "dossier d'architecture", "code source documenté", "rapport de recette", "formation des utilisateurs"). Ne pas inclure les jalons de suivi (comité de pilotage, réunion d'avancement). Liste vide si non précisé.

**contraintes** : Liste des contraintes projet explicitement mentionnées : délais impératifs, localisation géographique obligatoire, exigences d'interopérabilité, contraintes légales ou réglementaires, obligations de moyens, clauses de confidentialité, exigences de sécurité, limitations budgétaires. Phrases courtes et factuelles. Max 10 contraintes.

**certifications_obligatoires** : UNIQUEMENT les certifications dont l'absence entraîne l'élimination de l'offre. Critères stricts :
- Inclure si : "obligatoire", "exigé", "impératif", "requis", "éliminatoire", "condition sine qua non", "doit être certifié", "qualification requise"
- EXCLURE si : "souhaité", "apprécié", "serait un plus", "recommandé", "préférable", "non obligatoire", "optionnel", "si possible"
- Valeurs possibles : "SecNumCloud", "HDS", "ISO 27001", "ISO 27701", "Qualiopi", "RGPD", "SOC 2", "PASSI", "PRIS", "RGS"
- Liste vide si aucune certification n'est strictement obligatoire

DOCUMENT À ANALYSER :
{text}

Retourne UNIQUEMENT ce JSON :
{{
  "titre": "...",
  "client": "...",
  "secteur": "...",
  "budget_estime": null,
  "deadline_reponse": null,
  "duree_projet_mois": null,
  "technologies_demandees": [],
  "competences_requises": [],
  "questions_client": [],
  "livrables": [],
  "contraintes": [],
  "certifications_obligatoires": []
}}"""


class AOExtractor:
    def __init__(self):
        self.llm = ClaudeClient()

    def extract(self, text: str) -> AOContext:
        prompt = _EXTRACTION_USER.format(text=wrap_untrusted_content(text[:25000]))
        data = self.llm.json_complete(prompt, system=_EXTRACTION_SYSTEM, temperature=LLM_TEMPERATURE_FACTUAL, max_tokens=8000)
        if data:
            data["texte_source"] = text

            # Strip common AO prefixes that LLM sometimes adds to the title
            titre = (data.get("titre") or "").strip()
            for prefix in ["Appel d'offres : ", "Appel d'offres: ", "APPEL D'OFFRES : ",
                           "Objet : ", "Objet: ", "Marché : ", "Marché: "]:
                if titre.lower().startswith(prefix.lower()):
                    titre = titre[len(prefix):].strip()
            data["titre"] = titre

            # Fallback sector detection if LLM returned null/empty
            if not data.get("secteur"):
                _secteur_map = {
                    "Finance/Assurance": ["mutuelle", "assurance", "banque", "financ", "crédit", "credit", "caisse", "axa", "maif", "maaf", "groupama"],
                    "Santé": ["hôpital", "hopital", "santé", "sante", "médical", "medical", "clinique", "ehpad", "chu", "ars"],
                    "Collectivité/Public": ["métropole", "metropole", "commune", "mairie", "région", "region", "département", "departement", "agglo", "intercommunal", "préfecture", "ministère"],
                    "Éducation": ["université", "universite", "école", "ecole", "formation", "académie", "cfa", "lycée", "campus"],
                    "Transport": ["transport", "sncf", "ratp", "aéroport", "aeroport", "autoroute", "mobilité"],
                    "Énergie": ["énergie", "energie", "electricité", "electricite", "engie", "edf", "rte", "grdf"],
                    "Industrie": ["industrie", "manufactur", "usine", "production", "logistique"],
                    "Défense": ["défense", "defense", "armée", "armee", "militaire", "dga"],
                }
                text_lower = text.lower()
                for secteur, keywords in _secteur_map.items():
                    if any(kw in text_lower for kw in keywords):
                        data["secteur"] = secteur
                        break

            try:
                return AOContext(**data)
            except Exception as e:
                print(f"[Extractor] Erreur Pydantic: {e}")

        # Fallback local sans LLM
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        title = lines[0][:120] if lines else "Appel d'offres"
        client = ""
        for pat in [r"Client\s*:\s*(.+)", r"Acheteur\s*:\s*(.+)", r"Entreprise\s*:\s*(.+)", r"Pouvoir\s+adjudicateur\s*:\s*(.+)"]:
            m = re.search(pat, text, re.I)
            if m:
                client = m.group(1).strip()[:100]
                break

        return AOContext(
            titre=title,
            client=client or "Client non identifie",
            secteur="Non renseigne",
            budget_estime=_find_budget(text),
            technologies_demandees=_extract_technologies(text),
            competences_requises=_extract_technologies(text),
            certifications_obligatoires=_extract_certifications(text),
            contraintes=[
                l for l in lines
                if any(w in l.lower() for w in ["obligatoire", "imperatif", "exige", "deadline", "delai"])
            ][:8],
            livrables=[
                l for l in lines
                if "livrable" in l.lower() or "dossier" in l.lower()
            ][:8],
            questions_client=[l for l in lines if "?" in l][:10],
            texte_source=text,
        )

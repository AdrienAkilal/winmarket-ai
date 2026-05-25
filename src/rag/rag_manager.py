from pathlib import Path
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.core.config import REG_DIR
from src.core.models import RAGEvidence

# French stop words for better TF-IDF results
FRENCH_STOP_WORDS = [
    "le","la","les","de","du","des","un","une","et","en","au","aux","par","pour",
    "sur","dans","avec","est","sont","a","ont","ou","mais","donc","car","si",
    "que","qui","quoi","dont","où","ce","se","sa","son","ses","leur","leurs",
    "nous","vous","ils","elles","je","tu","il","elle","on","mon","ton","ma",
    "ta","mes","tes","cette","cet","ces","plus","très","aussi","comme","tout",
    "tous","bien","peut","être","fait","faire","avoir","notre","votre","leur"
]


class LocalRAGManager:
    def __init__(self, reg_dir: Path = REG_DIR):
        self.reg_dir = Path(reg_dir)
        self.docs = []
        self.sources = []
        self.vectorizer = TfidfVectorizer(
            stop_words=FRENCH_STOP_WORDS,
            ngram_range=(1, 2),
            max_features=8000,
            sublinear_tf=True
        )
        self.matrix = None
        self.load()

    def load(self):
        self.docs, self.sources = [], []
        if not self.reg_dir.exists():
            print(f"[RAG] Dossier REG introuvable : {self.reg_dir}")
            return
        for p in sorted(self.reg_dir.rglob("*.md")):
            self.sources.append(str(p.relative_to(self.reg_dir)))
            self.docs.append(p.read_text(encoding="utf-8", errors="ignore"))
        if self.docs:
            self.matrix = self.vectorizer.fit_transform(self.docs)
            print(f"[RAG] {len(self.docs)} documents chargés.")
        else:
            print("[RAG] Aucun document Markdown trouvé.")

    def search(self, query: str, top_k: int = 6) -> List[RAGEvidence]:
        if not self.docs or self.matrix is None:
            return []
        q = self.vectorizer.transform([query])
        sims = cosine_similarity(q, self.matrix).flatten()
        idx = sims.argsort()[::-1][:top_k]
        return [
            RAGEvidence(
                query=query,
                source=self.sources[i],
                score=float(sims[i]),
                content=self.docs[i][:3500]
            )
            for i in idx if sims[i] > 0.01
        ]

    _RAG_SYSTEM = (
        "Tu es responsable avant-vente dans une ESN française, expert en constitution de dossiers de réponse "
        "aux appels d'offres. Tu sélectionnes et valorises les références internes de l'entreprise pour "
        "maximiser leur impact dans les réponses aux consultations. Tu évalues la pertinence d'une référence "
        "selon quatre dimensions : (1) proximité sectorielle avec le client, (2) similarité technique des "
        "technologies déployées, (3) comparabilité de la taille et complexité du projet, (4) temporalité "
        "(une référence de moins de 3 ans vaut plus qu'une ancienne). Tu identifies précisément quels "
        "éléments de chaque référence sont réutilisables dans la réponse et lesquels ne le sont pas."
    )

    def semantic_rerank(self, ao_text: str, evidences: List[RAGEvidence], llm) -> Tuple[List[RAGEvidence], str]:
        """Reranks evidences semantically with Claude and returns a synthesis paragraph."""
        if not llm.enabled or not evidences:
            return evidences, ""

        docs_text = "\n\n".join([
            f"--- Référence {i+1} ({ev.source}) ---\n{ev.content[:800]}"
            for i, ev in enumerate(evidences[:6])
        ])

        prompt = f"""Tu dois sélectionner et prioriser nos références internes pour répondre à cet appel d'offres.

═══════════════════════════════════════════════
APPEL D'OFFRES (contexte de travail)
═══════════════════════════════════════════════
{ao_text[:2500]}

═══════════════════════════════════════════════
NOS RÉFÉRENCES INTERNES DISPONIBLES
═══════════════════════════════════════════════
{docs_text}

═══════════════════════════════════════════════
TA MISSION
═══════════════════════════════════════════════
Évalue chaque référence selon ces 4 critères de pertinence :
  1. **Secteur client** : Le client de la référence opère-t-il dans le même secteur que l'acheteur de l'AO ?
  2. **Similarité technique** : Les technologies, outils et méthodes de la référence recoupent-ils ceux demandés dans l'AO ?
  3. **Comparabilité projet** : La taille, complexité et nature du projet (TMA, développement, IA, data...) sont-ils proches ?
  4. **Transférabilité** : Quels livrables, apprentissages ou résultats de la référence sont directement valorisables dans ce dossier ?

CE QU'IL FAUT ÉVITER dans la sélection :
  • Ne pas retenir une référence seulement parce qu'elle mentionne une technologie présente dans l'AO si le contexte est totalement différent
  • Ne pas pénaliser une référence dont le secteur diffère si la technologie et la complexité correspondent
  • Ne pas inclure une référence dont la pertinence globale est inférieure à 30%

Réponds UNIQUEMENT en JSON valide :
{{
  "ranking": [liste des numéros 1-based des références, de la plus à la moins pertinente, ex: [3,1,5,2]],
  "synthese": "Paragraphe de 4 à 6 phrases rédigé au présent, professionnel et valorisant. Citer les 2-3 meilleures références par leur nom exact. Expliquer en quoi elles démontrent notre capacité à répondre à CET appel : secteur maîtrisé, technologies identiques, complexité comparable. Préciser ce qu'elles apportent concrètement au dossier (réassurance sur la stack technique, démonstration sectorielle, preuve de capacité à livrer dans les délais). Conclure sur la cohérence globale de notre portfolio par rapport à l'AO."
}}
"""
        data = llm.json_complete(prompt, system=self._RAG_SYSTEM, temperature=0.3)
        if not data:
            return evidences, ""

        ranking = data.get("ranking", [])
        if ranking:
            reranked = []
            seen = set()
            for idx in ranking:
                if isinstance(idx, int) and 1 <= idx <= len(evidences):
                    ev = evidences[idx - 1]
                    if id(ev) not in seen:
                        reranked.append(ev)
                        seen.add(id(ev))
            for ev in evidences:
                if id(ev) not in seen:
                    reranked.append(ev)
            evidences = reranked

        return evidences, data.get("synthese", "")

from __future__ import annotations
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import date

class AOContext(BaseModel):
    titre: str = ""
    client: str = ""
    secteur: str = ""
    budget_estime: Optional[float] = None
    deadline_reponse: str = ""
    duree_projet_mois: Optional[int] = None
    technologies_demandees: List[str] = Field(default_factory=list)
    competences_requises: List[str] = Field(default_factory=list)
    questions_client: List[str] = Field(default_factory=list)
    livrables: List[str] = Field(default_factory=list)
    contraintes: List[str] = Field(default_factory=list)
    certifications_obligatoires: List[str] = Field(default_factory=list)
    texte_source: str = ""

class CompanyProfile(BaseModel):
    raison_sociale: str = ""
    siret: str = ""
    effectif: str = "Non renseigné"
    ca: str = "Non renseigné"
    ville: str = "Non renseigné"
    secteur: str = "Non renseigné"
    anciennete: str = "Non renseigné"
    solidite_financiere: str = "Moyenne"
    source: str = "mock"

class RAGEvidence(BaseModel):
    query: str
    source: str
    score: float
    content: str

class CapacityResult(BaseModel):
    charge_actuelle_pct: int
    capacite_restante_pct: int
    equipe_disponible: bool
    commentaire: str

class CriterionScore(BaseModel):
    nom: str
    poids: float
    score: float
    justification: str

class ScoringResult(BaseModel):
    decision: str
    score_global: float
    criteres: List[CriterionScore]
    criteres_bloquants: List[str] = Field(default_factory=list)
    forces: List[str] = Field(default_factory=list)
    faiblesses: List[str] = Field(default_factory=list)
    risques: List[str] = Field(default_factory=list)
    recommandations: List[str] = Field(default_factory=list)
    evidence_pack: List[RAGEvidence] = Field(default_factory=list)
    company_profile: Optional[CompanyProfile] = None
    capacity: Optional[CapacityResult] = None
    rag_synthesis: str = ""
    ai_content: dict = Field(default_factory=dict)

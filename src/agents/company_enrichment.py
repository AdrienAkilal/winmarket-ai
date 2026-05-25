import requests
from src.core.models import CompanyProfile
from src.core.config import PAPPERS_API_TOKEN

class CompanyEnrichmentAgent:
    def enrich(self, company_name: str) -> CompanyProfile:
        if PAPPERS_API_TOKEN and company_name and company_name != "Client non identifié":
            try:
                r = requests.get("https://api.pappers.fr/v2/recherche", params={"api_token":PAPPERS_API_TOKEN,"q":company_name,"par_page":1}, timeout=8)
                data = r.json().get("resultats", [])
                if data:
                    e = data[0]
                    return CompanyProfile(raison_sociale=e.get("nom_entreprise", company_name), siret=e.get("siege",{}).get("siret",""), effectif=str(e.get("effectif","Non renseigné")), ca=str(e.get("chiffre_affaires","Non renseigné")), ville=e.get("siege",{}).get("ville",""), secteur=e.get("domaine_activite",""), anciennete=str(e.get("date_creation","")), solidite_financiere="À vérifier", source="pappers")
            except Exception:
                pass
        return CompanyProfile(raison_sociale=company_name or "Client démo", effectif="250-500", ca="50M€ estimés", ville="Paris", secteur="Services numériques / public", anciennete="10+ ans", solidite_financiere="Bonne", source="mock")

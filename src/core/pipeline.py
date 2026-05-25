from src.agents.ao_extractor import AOExtractor, read_document
from src.agents.company_enrichment import CompanyEnrichmentAgent
from src.agents.llm_client import ClaudeClient
from src.rag.rag_manager import LocalRAGManager
from src.agents.capacity_analyzer import CapacityAnalyzer
from src.agents.scoring_engine import ScoringEngine
from src.livrables.document_generator import DocumentGenerator

class AOPipeline:
    def __init__(self):
        self.llm = ClaudeClient()
        self.extractor = AOExtractor()
        self.company = CompanyEnrichmentAgent()
        self.rag = LocalRAGManager()
        self.capacity = CapacityAnalyzer()
        self.scoring = ScoringEngine()
        self.generator = DocumentGenerator()

    def run_text(self, text: str, generate_docs: bool = True):
        ao = self.extractor.extract(text)
        company = self.company.enrich(ao.client)
        query = " ".join([ao.titre, " ".join(ao.technologies_demandees), " ".join(ao.competences_requises), " ".join(ao.certifications_obligatoires)])
        evidences = self.rag.search(query, top_k=8)
        evidences, rag_synthesis = self.rag.semantic_rerank(ao.texte_source, evidences, self.llm)
        capacity = self.capacity.analyze(ao)
        result = self.scoring.score(ao, company, evidences, capacity)
        result.rag_synthesis = rag_synthesis
        result = self.scoring.enrich_with_llm(ao, result, self.llm)
        ai_content = self.generator._generate_ai_content(ao, result, self.llm)
        result.ai_content = ai_content
        files = {}
        if generate_docs:
            files["docx"] = self.generator.generate_docx(ao, result)
            files["pdf"] = self.generator.generate_pdf(ao, result)
        return ao, result, files

    def run_file(self, path: str, generate_docs: bool = True):
        return self.run_text(read_document(path), generate_docs)

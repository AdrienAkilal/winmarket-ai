from pathlib import Path
from dotenv import load_dotenv
import os
from typing import Dict, Any

# ============================================================================
# DIRECTORIES & PATHS
# ============================================================================
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
REG_DIR = DATA_DIR / "reg_docs"
OUTPUT_DIR = DATA_DIR / "outputs"
PROMPTS_DIR = ROOT_DIR / "prompts"
LOGS_DIR = ROOT_DIR / "logs"

# Create directories if not exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================
load_dotenv(ROOT_DIR / ".env", override=True)

# ============================================================================
# API KEYS & CREDENTIALS
# ============================================================================
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
PAPPERS_API_TOKEN = os.getenv("PAPPERS_API_TOKEN", "")

# ============================================================================
# LLM CONFIGURATION
# ============================================================================
LLM_ENABLED = os.getenv("LLM_ENABLED", "true").lower() == "true"

# Timeouts
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "60"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4096"))

# Retry policy
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))
LLM_RETRY_BACKOFF = float(os.getenv("LLM_RETRY_BACKOFF", "2.0"))
LLM_RETRY_INITIAL_DELAY = float(os.getenv("LLM_RETRY_INITIAL_DELAY", "1.0"))

# Temperature & creativity
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
LLM_TEMPERATURE_FACTUAL = float(os.getenv("LLM_TEMPERATURE_FACTUAL", "0.1"))
LLM_TEMPERATURE_GENERATION = float(os.getenv("LLM_TEMPERATURE_GENERATION", "0.3"))
LLM_TOP_P = float(os.getenv("LLM_TOP_P", "1.0"))
LLM_PROVIDER_PRIORITY = [item.strip().lower() for item in os.getenv(
    "LLM_PROVIDER_PRIORITY", "anthropic,openai,mistral"
).split(",") if item.strip()]

# ============================================================================
# RAG CONFIGURATION
# ============================================================================
RAG_ENABLED = os.getenv("RAG_ENABLED", "true").lower() == "true"
RAG_MIN_SCORE_THRESHOLD = float(os.getenv("RAG_MIN_SCORE_THRESHOLD", "0.15"))
RAG_TOP_K_RESULTS = int(os.getenv("RAG_TOP_K_RESULTS", "5"))
RAG_CACHE_TTL_SECONDS = int(os.getenv("RAG_CACHE_TTL_SECONDS", "3600"))

# Embedding model (if using semantic search)
RAG_EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
RAG_USE_EMBEDDINGS = os.getenv("RAG_USE_EMBEDDINGS", "false").lower() == "true"

# ============================================================================
# EXTERNAL API CONFIGURATION
# ============================================================================
PAPPERS_ENABLED = os.getenv("PAPPERS_ENABLED", "true").lower() == "true"
PAPPERS_TIMEOUT_SECONDS = int(os.getenv("PAPPERS_TIMEOUT_SECONDS", "8"))
PAPPERS_MAX_RETRIES = int(os.getenv("PAPPERS_MAX_RETRIES", "2"))

# Rate limiting
API_RATE_LIMIT_CALLS = int(os.getenv("API_RATE_LIMIT_CALLS", "100"))
API_RATE_LIMIT_PERIOD_SECONDS = int(os.getenv("API_RATE_LIMIT_PERIOD_SECONDS", "60"))

# ============================================================================
# FEATURE FLAGS
# ============================================================================
FEATURE_DOCUMENT_GENERATION = os.getenv("FEATURE_DOCUMENT_GENERATION", "true").lower() == "true"
FEATURE_AUTO_SCORING = os.getenv("FEATURE_AUTO_SCORING", "true").lower() == "true"
FEATURE_CAPACITY_ANALYSIS = os.getenv("FEATURE_CAPACITY_ANALYSIS", "true").lower() == "true"
FEATURE_COMPANY_ENRICHMENT = os.getenv("FEATURE_COMPANY_ENRICHMENT", "true").lower() == "true"

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT_JSON = os.getenv("LOG_FORMAT_JSON", "false").lower() == "true"
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "true").lower() == "true"
LOG_TO_CONSOLE = os.getenv("LOG_TO_CONSOLE", "true").lower() == "true"

# ============================================================================
# VALIDATION & CONSTRAINTS
# ============================================================================
MAX_DOCUMENT_SIZE_MB = int(os.getenv("MAX_DOCUMENT_SIZE_MB", "50"))
MAX_AO_TEXT_LENGTH = int(os.getenv("MAX_AO_TEXT_LENGTH", "50000"))  # Max chars for AO extraction
MIN_EXTRACTION_CONFIDENCE = float(os.getenv("MIN_EXTRACTION_CONFIDENCE", "0.5"))

# ============================================================================
# BUSINESS LOGIC CONFIGURATION
# ============================================================================
# Scoring thresholds
SCORING_THRESHOLD_GO = int(os.getenv("SCORING_THRESHOLD_GO", "88"))
SCORING_THRESHOLD_SOUS_RESERVE = int(os.getenv("SCORING_THRESHOLD_SOUS_RESERVE", "60"))

# Capacity calculation
CAPACITY_LOAD_THRESHOLD_WARNING = float(os.getenv("CAPACITY_LOAD_THRESHOLD_WARNING", "0.85"))
CAPACITY_LOAD_THRESHOLD_CRITICAL = float(os.getenv("CAPACITY_LOAD_THRESHOLD_CRITICAL", "0.95"))

# Certifications library
CERTIFICATIONS_LIBRARY = [
    "ISO 27001", "ISO 9001", "ISO 14001",
    "RGPD", "GDPR",
    "SecNumCloud", "HDS",
    "Qualiopi", "SOC 2", "CMMC",
    "PCI-DSS", "HIPAA", "FedRAMP",
]

# Technologies library (updated from hardcoded list in agents)
TECHNOLOGIES_LIBRARY = [
    # Frontend
    "React", "Angular", "Vue", "Next.js", "Svelte", "TypeScript", "JavaScript",
    # Backend
    "Java", "Spring", "Python", "Django", "FastAPI", ".NET", "C#", "Node", "NodeJS", "Go", "Rust",
    # Databases
    "PostgreSQL", "MySQL", "Oracle", "SQL Server", "MongoDB", "Redis", "DynamoDB", "Cassandra",
    # Cloud
    "AWS", "Azure", "GCP", "Kubernetes", "Docker", "OpenStack",
    # DevOps
    "Terraform", "Ansible", "Jenkins", "GitLab CI", "GitHub Actions",
    # Data & Analytics
    "Power BI", "Tableau", "Spark", "Hadoop", "Kafka",
    # AI/ML
    "IA", "AI", "RAG", "LLM", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
    # Enterprise
    "SAP", "SharePoint", "Salesforce", "ServiceNow", "Oracle EBS",
    # Security
    "Vault", "Keycloak", "OAuth2", "SAML", "SSL/TLS",
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def get_config_dict() -> Dict[str, Any]:
    """Return all configuration as dictionary."""
    return {
        "paths": {
            "root": str(ROOT_DIR),
            "data": str(DATA_DIR),
            "reg_docs": str(REG_DIR),
            "outputs": str(OUTPUT_DIR),
            "prompts": str(PROMPTS_DIR),
            "logs": str(LOGS_DIR),
        },
        "llm": {
            "enabled": LLM_ENABLED,
            "timeout_seconds": LLM_TIMEOUT_SECONDS,
            "max_tokens": LLM_MAX_TOKENS,
            "temperature": LLM_TEMPERATURE,
            "temperature_factual": LLM_TEMPERATURE_FACTUAL,
            "temperature_generation": LLM_TEMPERATURE_GENERATION,
            "provider_priority": LLM_PROVIDER_PRIORITY,
            "max_retries": LLM_MAX_RETRIES,
        },
        "rag": {
            "enabled": RAG_ENABLED,
            "min_score_threshold": RAG_MIN_SCORE_THRESHOLD,
            "top_k_results": RAG_TOP_K_RESULTS,
            "cache_ttl_seconds": RAG_CACHE_TTL_SECONDS,
        },
        "external_apis": {
            "pappers_enabled": PAPPERS_ENABLED,
            "pappers_timeout_seconds": PAPPERS_TIMEOUT_SECONDS,
            "pappers_max_retries": PAPPERS_MAX_RETRIES,
        },
        "features": {
            "document_generation": FEATURE_DOCUMENT_GENERATION,
            "auto_scoring": FEATURE_AUTO_SCORING,
            "capacity_analysis": FEATURE_CAPACITY_ANALYSIS,
            "company_enrichment": FEATURE_COMPANY_ENRICHMENT,
        },
        "logging": {
            "level": LOG_LEVEL,
            "json_format": LOG_FORMAT_JSON,
            "to_file": LOG_TO_FILE,
            "to_console": LOG_TO_CONSOLE,
        },
    }


def validate_config() -> None:
    """Validate critical configuration settings."""
    errors = []
    
    available_llm_keys = {"anthropic": ANTHROPIC_API_KEY, "openai": OPENAI_API_KEY, "mistral": MISTRAL_API_KEY}
    if LLM_ENABLED and not any(available_llm_keys.get(p) for p in LLM_PROVIDER_PRIORITY):
        errors.append("No API key configured for any provider in LLM_PROVIDER_PRIORITY")
    
    if not PAPPERS_API_TOKEN and PAPPERS_ENABLED:
        errors.append("PAPPERS_API_TOKEN not set but PAPPERS_ENABLED=true")
    
    if SCORING_THRESHOLD_GO <= SCORING_THRESHOLD_SOUS_RESERVE:
        errors.append("SCORING_THRESHOLD_GO must be > SCORING_THRESHOLD_SOUS_RESERVE")
    
    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))


# Validate on import
validate_config()

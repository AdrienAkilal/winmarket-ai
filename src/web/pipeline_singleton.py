"""Single shared AOPipeline instance for the FastAPI process.

Equivalent to the @st.cache_resource pipeline used by the Streamlit UI:
one instance is built lazily on first use and reused for every request.
"""
from functools import lru_cache

from src.core.pipeline import AOPipeline


@lru_cache(maxsize=1)
def get_pipeline() -> AOPipeline:
    return AOPipeline()

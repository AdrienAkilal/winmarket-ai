"""Presentation helpers for the RAG reference base — no RAG logic here.

Groups the already-loaded LocalRAGManager documents by top-level folder,
same grouping the Streamlit "Base de référence" page performs.
"""
from src.rag.rag_manager import LocalRAGManager


def grouped_documents(rag: LocalRAGManager) -> list[dict]:
    groups: dict[str, list[dict]] = {}
    for source, doc in zip(rag.sources, rag.docs):
        folder = source.split("/")[0] if "/" in source else "racine"
        groups.setdefault(folder, []).append({"source": source, "chars": len(doc)})
    return [
        {"folder": folder, "documents": docs}
        for folder, docs in sorted(groups.items())
    ]


def knowledge_summary(rag: LocalRAGManager) -> dict:
    return {
        "total_documents": len(rag.docs),
        "total_kb": sum(len(d) for d in rag.docs) // 1000,
        "groups": grouped_documents(rag),
    }

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

import json
import tempfile
from datetime import datetime
import streamlit as st
import pandas as pd
from src.core.pipeline import AOPipeline
from src.core.config import DATA_DIR, OUTPUT_DIR

# ─── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WinMarket AI • Plateforme de Scoring des Appels d'Offres",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

/* ── Header ── */
.aos-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 60%, #0f4c81 100%);
    padding: 2rem 2.5rem 1.8rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
    box-shadow: 0 4px 24px rgba(15,23,42,0.35);
}
.aos-header-icon { font-size: 2.8rem; line-height:1; }
.aos-header-title { color: #f8fafc; font-size: 1.8rem; font-weight: 700; letter-spacing: -0.02em; margin:0; }
.aos-header-sub   { color: #94a3b8; font-size: 0.85rem; margin-top:0.2rem; font-family:'IBM Plex Mono',monospace; }

/* ── Decision badge ── */
.badge {
    display: inline-block;
    padding: 0.35rem 1rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 1rem;
    letter-spacing: 0.04em;
}
.badge-go     { background:#dcfce7; color:#16a34a; border:2px solid #16a34a; }
.badge-reserve{ background:#fef9c3; color:#ca8a04; border:2px solid #ca8a04; }
.badge-nogo   { background:#fee2e2; color:#dc2626; border:2px solid #dc2626; }

/* ── KPI cards ── */
.kpi-row { display:flex; gap:1rem; margin-bottom:1.2rem; flex-wrap:wrap; }
.kpi-card {
    flex:1; min-width:140px;
    background:#1e293b;
    border-radius:10px;
    padding:1rem 1.2rem;
    border-left: 4px solid #3b82f6;
    box-shadow: 0 2px 8px rgba(0,0,0,.25);
}
.kpi-card.go     { border-color:#22c55e; }
.kpi-card.reserve{ border-color:#eab308; }
.kpi-card.nogo   { border-color:#ef4444; }
.kpi-card.neutral{ border-color:#3b82f6; }
.kpi-label { color:#94a3b8; font-size:0.75rem; text-transform:uppercase; letter-spacing:.08em; }
.kpi-value { color:#f8fafc; font-size:1.7rem; font-weight:700; font-family:'IBM Plex Mono',monospace; line-height:1.1; }
.kpi-sub   { color:#64748b; font-size:0.72rem; margin-top:.15rem; }

/* ── Score bar ── */
.score-row { margin-bottom:0.6rem; }
.score-label { display:flex; justify-content:space-between; font-size:.83rem; color:#cbd5e1; margin-bottom:.25rem; }
.score-track { background:#1e293b; border-radius:999px; height:10px; overflow:hidden; }
.score-fill  { height:100%; border-radius:999px; transition: width .6s ease; }
.fill-high   { background: linear-gradient(90deg,#22c55e,#4ade80); }
.fill-med    { background: linear-gradient(90deg,#eab308,#facc15); }
.fill-low    { background: linear-gradient(90deg,#ef4444,#f87171); }

/* ── Flag ── */
.flag-block {
    background:#1c0a0a;
    border-left:4px solid #ef4444;
    border-radius:0 8px 8px 0;
    padding:.7rem 1rem;
    margin-bottom:.5rem;
    color:#fca5a5;
    font-size:.85rem;
}
.flag-warn {
    background:#1c1500;
    border-left:4px solid #eab308;
    border-radius:0 8px 8px 0;
    padding:.7rem 1rem;
    margin-bottom:.5rem;
    color:#fde68a;
    font-size:.85rem;
}

/* ── History row ── */
.hist-row {
    background:#0f172a;
    border:1px solid #1e293b;
    border-radius:8px;
    padding:.75rem 1rem;
    margin-bottom:.5rem;
    display:flex;
    justify-content:space-between;
    align-items:center;
}
.hist-title { color:#e2e8f0; font-size:.88rem; font-weight:600; }
.hist-meta  { color:#64748b; font-size:.75rem; margin-top:.1rem; }

/* ── Section title ── */
.section-title {
    color:#e2e8f0;
    font-size:1rem;
    font-weight:700;
    text-transform:uppercase;
    letter-spacing:.1em;
    border-bottom:1px solid #1e293b;
    padding-bottom:.4rem;
    margin-bottom:1rem;
}

/* ── Step progress ── */
.step-bar {
    display:flex;
    gap:.5rem;
    margin-bottom:1.2rem;
    flex-wrap:wrap;
}
.step {
    flex:1;
    min-width:100px;
    background:#1e293b;
    border-radius:6px;
    padding:.4rem .6rem;
    font-size:.72rem;
    color:#64748b;
    text-align:center;
    font-family:'IBM Plex Mono',monospace;
}
.step.done   { background:#14532d; color:#86efac; }
.step.active { background:#1e3a5f; color:#93c5fd; border:1px solid #3b82f6; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0f172a !important;
    border-right: 1px solid #1e293b;
}
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }

/* ── Main background ── */
[data-testid="stAppViewContainer"] { background:#040d1a; }
[data-testid="block-container"]    { background:transparent; }

/* ── Dataframe overrides ── */
.stDataFrame { border-radius:8px; overflow:hidden; }

/* ── Expander ── */
[data-testid="stExpander"] { background:#0f172a !important; border:1px solid #1e293b !important; border-radius:8px !important; }
[data-testid="stExpander"] summary { color:#cbd5e1 !important; }
</style>
""", unsafe_allow_html=True)

# ─── Historique helpers ──────────────────────────────────────────────────────────
HIST_FILE = DATA_DIR / "historique" / "historique_ao.json"

def load_historique() -> list:
    HIST_FILE.parent.mkdir(parents=True, exist_ok=True)
    if HIST_FILE.exists():
        try:
            return json.loads(HIST_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def save_historique(records: list):
    HIST_FILE.parent.mkdir(parents=True, exist_ok=True)
    HIST_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

def append_to_historique(ao, result):
    records = load_historique()
    records.append({
        "ao_id": datetime.now().strftime("AO_%Y%m%d_%H%M%S"),
        "titre": ao.titre,
        "client": ao.client,
        "secteur": ao.secteur or "Non renseigne",
        "decision": result.decision,
        "score": result.score_global,
        "budget": ao.budget_estime,
        "techs": ao.technologies_demandees[:4],
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "resultat": "en attente",
    })
    save_historique(records)

# ─── Session state ───────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "pipeline": None,
        "current_ao": None,
        "current_result": None,
        "current_files": {},
        "view": "home",   # home | detail | history
        "history": load_historique(),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

@st.cache_resource(show_spinner=False)
def get_pipeline():
    return AOPipeline()

# ─── Helpers ─────────────────────────────────────────────────────────────────────
def decision_badge(decision: str) -> str:
    if decision == "GO":
        return '<span class="badge badge-go">✅ GO</span>'
    if "RESERVE" in decision.upper():
        return '<span class="badge badge-reserve">⚠️ GO SOUS RÉSERVE</span>'
    return '<span class="badge badge-nogo">❌ NO-GO</span>'

def score_bar(label: str, poids: float, score: float, justification: str):
    cls = "fill-high" if score >= 75 else ("fill-med" if score >= 55 else "fill-low")
    html = f"""
<div class="score-row">
  <div class="score-label">
    <span>{label} <span style="color:#475569;font-size:.75rem">({int(poids)}%)</span></span>
    <span style="font-family:'IBM Plex Mono',monospace;font-weight:600">{score:.0f}/100</span>
  </div>
  <div class="score-track">
    <div class="score-fill {cls}" style="width:{score}%"></div>
  </div>
  <div style="color:#475569;font-size:.75rem;margin-top:.2rem">{justification}</div>
</div>"""
    st.markdown(html, unsafe_allow_html=True)

def step_bar(steps: list, active: int):
    parts = []
    for i, s in enumerate(steps):
        cls = "done" if i < active else ("active" if i == active else "")
        icon = "✓ " if i < active else ""
        parts.append(f'<div class="step {cls}">{icon}{s}</div>')
    st.markdown(f'<div class="step-bar">{"".join(parts)}</div>', unsafe_allow_html=True)

# ─── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎯 WinMarket AI")
    st.markdown('<div style="color:#475569;font-size:.75rem;margin-top:-.4rem;margin-bottom:.6rem">Scoring des Appels d\'Offres</div>', unsafe_allow_html=True)
    st.markdown('<hr style="border-color:#1e293b">', unsafe_allow_html=True)

    # Navigation
    nav = st.radio("Navigation", ["Analyser un appel d'offres", "Historique", "Base de référence"], label_visibility="collapsed")

    st.markdown('<hr style="border-color:#1e293b">', unsafe_allow_html=True)

    # Stats sidebar
    hist = load_historique()
    total = len(hist)
    n_go     = sum(1 for h in hist if h.get("decision") == "GO")
    n_res    = sum(1 for h in hist if "RESERVE" in h.get("decision","").upper())
    n_nogo   = sum(1 for h in hist if h.get("decision") == "NO-GO")

    st.markdown("**📊 Statistiques**")
    c1, c2 = st.columns(2)
    c1.metric("Total analysés", total)
    c2.metric("GO", n_go)
    c3, c4 = st.columns(2)
    c3.metric("Sous réserve", n_res)
    c4.metric("NO-GO", n_nogo)

    st.markdown('<hr style="border-color:#1e293b">', unsafe_allow_html=True)

    # RAG info
    pipeline = get_pipeline()
    n_docs = len(pipeline.rag.docs)
    st.markdown(f"**📚 Base de référence** — {n_docs} documents")
    if st.button("🔄 Recharger la base", use_container_width=True):
        pipeline.rag.load()
        st.success(f"Base rechargée : {len(pipeline.rag.docs)} documents")

# ─── Main area ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="aos-header">
  <div class="aos-header-icon">🎯</div>
  <div>
    <div class="aos-header-title">WinMarket AI</div>
    <div class="aos-header-sub">Analysez vos chances de succès · Évaluez vos risques · Générez vos dossiers de réponse</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE : ANALYSER UN AO
# ═══════════════════════════════════════════════════════════════════════════════
if nav == "Analyser un appel d'offres":

    # If we have a result, offer to go back
    if st.session_state.current_ao is not None:
        if st.button("⬅ Nouvelle analyse"):
            st.session_state.current_ao = None
            st.session_state.current_result = None
            st.rerun()

    # ── Input form ──
    if st.session_state.current_ao is None:
        examples_dir = DATA_DIR / "ao_examples"
        examples = sorted(examples_dir.glob("*.txt")) if examples_dir.exists() else []

        col_src, col_go = st.columns([3, 1])
        with col_src:
            mode = st.radio("Source de l'appel d'offres", ["Exemple démo", "Importer un fichier (PDF/DOCX/TXT)", "Saisie texte libre"], horizontal=True)

        text = None
        if mode == "Exemple démo":
            if examples:
                sel = st.selectbox("Choisir un exemple", examples, format_func=lambda p: p.stem.replace("_", " "))
                text = sel.read_text(encoding="utf-8")
                with st.expander("Aperçu du contenu"):
                    st.text(text[:2500] + ("..." if len(text) > 2500 else ""))
            else:
                st.warning("Aucun exemple dans data/ao_examples/")

        elif "Importer" in mode:
            up = st.file_uploader("Déposer le fichier de l'appel d'offres", type=["pdf", "txt", "md", "docx"])
            if up:
                suffix = Path(up.name).suffix
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(up.read())
                    tmp_path = tmp.name
                from src.agents.ao_extractor import read_document
                text = read_document(tmp_path)
                st.success(f"Fichier chargé : **{up.name}** ({len(text):,} caractères)")
                with st.expander("Aperçu"):
                    st.text(text[:2500] + ("..." if len(text) > 2500 else ""))

        else:
            text = st.text_area("Coller le contenu de l'appel d'offres", height=280,
                                placeholder="Colle ici le texte brut de l'appel d'offres...")

        if text and st.button("🚀 Lancer l'analyse", type="primary", use_container_width=True):

            from src.core.content_security import ContentSecurityError
            try:
                pipeline.security.validate(text)
                text = pipeline.preparer.prepare(text).text
            except ContentSecurityError as exc:
                st.error(exc.user_message)
                st.stop()

            STEPS = ["Sécurité et préparation", "Lecture intelligente", "Recherche client", "Analyse sémantique", "Scoring enrichi", "Disponibilité équipe", "Génération documents"]
            prog_placeholder = st.empty()
            status_placeholder = st.empty()
            bar_placeholder = st.empty()

            def update_progress(step_idx: int, msg: str):
                with prog_placeholder.container():
                    step_bar(STEPS, step_idx)
                status_placeholder.markdown(f"**{msg}**")
                bar_placeholder.progress((step_idx + 1) / len(STEPS))

            update_progress(0, "Lecture du document...")
            from src.agents.ao_extractor import AOExtractor, read_document
            from src.agents.llm_client import ClaudeClient
            llm = ClaudeClient()  # Fresh instance — reads ANTHROPIC_API_KEY at call time
            ao = AOExtractor().extract(text)

            update_progress(1, f"Lecture intelligente du document — *{ao.titre[:60]}*")
            from src.agents.company_enrichment import CompanyEnrichmentAgent
            update_progress(2, f"Recherche d'informations sur le client : *{ao.client}*")
            company = CompanyEnrichmentAgent().enrich(ao.client)

            update_progress(3, "Analyse sémantique de vos références internes...")
            query = " ".join([ao.titre] + ao.technologies_demandees + ao.certifications_obligatoires)
            evidences = pipeline.rag.search(query, top_k=8)
            evidences, rag_synthesis = pipeline.rag.semantic_rerank(ao.texte_source, evidences, llm)

            update_progress(4, "Calcul et enrichissement du score de réussite...")
            from src.agents.capacity_analyzer import CapacityAnalyzer
            capacity = CapacityAnalyzer().analyze(ao)
            from src.agents.scoring_engine import ScoringEngine
            result = ScoringEngine().score(ao, company, evidences, capacity)
            result.rag_synthesis = rag_synthesis
            result = pipeline.scoring.enrich_with_llm(ao, result, llm)

            update_progress(5, "Évaluation de la disponibilité de l'équipe...")
            ai_content = pipeline.generator._generate_ai_content(ao, result, llm)
            result.ai_content = ai_content

            update_progress(6, "Génération de vos documents de réponse sur mesure...")
            from src.livrables.document_generator import DocumentGenerator
            dg = DocumentGenerator()
            files = {
                "pdf":  dg.generate_pdf(ao, result),
                "docx": dg.generate_docx(ao, result),
            }

            prog_placeholder.empty()
            status_placeholder.empty()
            bar_placeholder.empty()

            st.session_state.current_ao     = ao
            st.session_state.current_result = result
            st.session_state.current_files  = files

            # Save to history
            append_to_historique(ao, result)
            st.session_state.history = load_historique()
            st.rerun()

    # ── Results view ──
    else:
        ao     = st.session_state.current_ao
        result = st.session_state.current_result
        files  = st.session_state.current_files

        # ── Decision banner ──
        dec_class = "go" if result.decision == "GO" else ("reserve" if "RESERVE" in result.decision else "nogo")
        score_color = "#22c55e" if result.score_global >= 75 else ("#eab308" if result.score_global >= 58 else "#ef4444")

        st.markdown(f"""
<div style="background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:1.4rem 1.8rem;margin-bottom:1.2rem">
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem">
    <div>
      <div style="color:#94a3b8;font-size:.75rem;text-transform:uppercase;letter-spacing:.08em">Appel d'offres</div>
      <div style="color:#f1f5f9;font-size:1.15rem;font-weight:700;margin-top:.2rem">{ao.titre}</div>
      <div style="color:#64748b;font-size:.82rem;margin-top:.2rem">Client : {ao.client} &nbsp;|&nbsp; Secteur : {ao.secteur or "–"} &nbsp;|&nbsp; Budget : {'%s €' % f'{ao.budget_estime:,.0f}' if ao.budget_estime else 'Non renseigné'}</div>
    </div>
    <div style="text-align:right">
      {decision_badge(result.decision)}
      <div style="color:{score_color};font-size:2.2rem;font-weight:700;font-family:'IBM Plex Mono',monospace;line-height:1">{result.score_global:.1f}<span style="font-size:1rem;color:#475569">/100</span></div>
      <div style="color:#475569;font-size:.72rem">Disponibilité équipe : {result.capacity.capacite_restante_pct}%</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        # Blockers
        if result.criteres_bloquants:
            for b in result.criteres_bloquants:
                st.markdown(f'<div class="flag-block">🚨 <strong>Critère bloquant :</strong> {b}</div>', unsafe_allow_html=True)

        # Tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Évaluation détaillée",
            "📋 Contexte de l'appel d'offres",
            "🔍 Références & Preuves",
            "🏢 Profil client",
            "📦 Documents à télécharger",
            "📈 Appels d'offres similaires",
        ])

        # ── TAB 1 : Scoring ──
        with tab1:
            st.markdown('<div class="section-title">Note par critère d\'évaluation</div>', unsafe_allow_html=True)

            left, right = st.columns([3, 2])
            with left:
                for c in result.criteres:
                    score_bar(c.nom, c.poids, c.score, c.justification)

            with right:
                st.markdown('<div class="section-title">Forces / Faiblesses</div>', unsafe_allow_html=True)
                if result.forces:
                    st.markdown("**✅ Points forts**")
                    for f in result.forces:
                        st.markdown(f'<div style="color:#86efac;font-size:.85rem;padding:.2rem 0">▶ {f}</div>', unsafe_allow_html=True)
                if result.faiblesses:
                    st.markdown("**⚠️ Points faibles**")
                    for f in result.faiblesses:
                        st.markdown(f'<div style="color:#fca5a5;font-size:.85rem;padding:.2rem 0">▶ {f}</div>', unsafe_allow_html=True)

                st.markdown('<div class="section-title" style="margin-top:1.2rem">Recommandations</div>', unsafe_allow_html=True)
                for r in result.recommandations:
                    st.markdown(f'<div class="flag-warn">💡 {r}</div>', unsafe_allow_html=True)

                st.markdown('<div class="section-title" style="margin-top:1.2rem">Risques identifiés</div>', unsafe_allow_html=True)
                for r in result.risques:
                    st.markdown(f'<div class="flag-warn">⚠️ {r}</div>', unsafe_allow_html=True)

            # DataFrame view
            with st.expander("Voir le tableau détaillé"):
                df = pd.DataFrame([{
                    "Critère": c.nom,
                    "Poids (%)": int(c.poids),
                    "Score /100": f"{c.score:.0f}",
                    "Score pondéré": f"{c.score * c.poids / 100:.1f}",
                    "Justification": c.justification,
                } for c in result.criteres])
                st.dataframe(df, use_container_width=True, hide_index=True)

        # ── TAB 2 : Contexte AO ──
        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="section-title">Informations générales</div>', unsafe_allow_html=True)
                fields = [
                    ("Titre", ao.titre),
                    ("Client", ao.client),
                    ("Secteur", ao.secteur or "–"),
                    ("Budget estimé", f"{ao.budget_estime:,.0f} €" if ao.budget_estime else "Non renseigné"),
                    ("Durée projet", f"{ao.duree_projet_mois} mois" if ao.duree_projet_mois else "–"),
                    ("Date limite de réponse", ao.deadline_reponse or "–"),
                ]
                for label, val in fields:
                    st.markdown(f'<div style="margin-bottom:.5rem"><span style="color:#64748b;font-size:.8rem">{label}</span><br><span style="color:#e2e8f0">{val}</span></div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="section-title">Technologies et compétences requises</div>', unsafe_allow_html=True)
                techs = list(dict.fromkeys(ao.technologies_demandees + ao.competences_requises))
                if techs:
                    tags = "".join([f'<span style="background:#1e293b;color:#93c5fd;border:1px solid #1e3a5f;border-radius:4px;padding:.2rem .55rem;font-size:.78rem;margin:.2rem .2rem 0 0;display:inline-block">{t}</span>' for t in techs])
                    st.markdown(tags, unsafe_allow_html=True)
                else:
                    st.caption("Aucune technologie identifiée")

                st.markdown('<div class="section-title" style="margin-top:1rem">Certifications obligatoires</div>', unsafe_allow_html=True)
                if ao.certifications_obligatoires:
                    for cert in ao.certifications_obligatoires:
                        color = "#86efac" if cert.lower() in {"iso 27001","rgpd","qualiopi","iso27001"} else "#fca5a5"
                        tick  = "✓" if cert.lower() in {"iso 27001","rgpd","qualiopi","iso27001"} else "✗"
                        st.markdown(f'<div style="color:{color};font-size:.85rem">{tick} {cert}</div>', unsafe_allow_html=True)
                else:
                    st.caption("Aucune certification obligatoire détectée")

            # Contraintes
            if ao.contraintes:
                st.markdown('<div class="section-title" style="margin-top:1rem">Contraintes identifiées</div>', unsafe_allow_html=True)
                cats = {"obligatoire": [], "imperatif": [], "délai": [], "autre": []}
                for c in ao.contraintes:
                    cl = c.lower()
                    if "obligatoire" in cl: cats["obligatoire"].append(c)
                    elif "impératif" in cl or "imperatif" in cl: cats["imperatif"].append(c)
                    elif "délai" in cl or "deadline" in cl: cats["délai"].append(c)
                    else: cats["autre"].append(c)
                for cat, items in cats.items():
                    for item in items:
                        st.markdown(f'<div class="flag-warn" style="font-size:.8rem">⚡ {item}</div>', unsafe_allow_html=True)

            # Livrables AO
            if ao.livrables:
                st.markdown('<div class="section-title" style="margin-top:1rem">Livrables demandés</div>', unsafe_allow_html=True)
                for lv in ao.livrables:
                    st.markdown(f'<div style="color:#cbd5e1;font-size:.83rem;padding:.15rem 0">📎 {lv}</div>', unsafe_allow_html=True)

            # Questions
            if ao.questions_client:
                st.markdown('<div class="section-title" style="margin-top:1rem">Questions identifiées</div>', unsafe_allow_html=True)
                for i, q in enumerate(ao.questions_client[:10], 1):
                    st.markdown(f'<div style="color:#94a3b8;font-size:.82rem;padding:.2rem 0"><span style="color:#3b82f6">Q{i}</span> {q}</div>', unsafe_allow_html=True)

        # ── TAB 3 : Références & Preuves ──
        with tab3:
            st.markdown(f'<div class="section-title">{len(result.evidence_pack)} documents pertinents trouvés dans la base de référence</div>', unsafe_allow_html=True)

            if result.rag_synthesis:
                st.markdown(f"""
<div style="background:#0f2a1a;border-left:4px solid #22c55e;border-radius:0 8px 8px 0;padding:1rem 1.2rem;margin-bottom:1.2rem">
  <div style="color:#86efac;font-size:.75rem;text-transform:uppercase;letter-spacing:.08em;margin-bottom:.4rem">🤖 Analyse IA des références</div>
  <div style="color:#d1fae5;font-size:.88rem;line-height:1.6">{result.rag_synthesis}</div>
</div>""", unsafe_allow_html=True)

            if result.evidence_pack:
                for ev in result.evidence_pack[:8]:
                    pct = min(int(ev.score * 400), 100)
                    bar_cls = "fill-high" if pct >= 60 else ("fill-med" if pct >= 30 else "fill-low")
                    with st.expander(f"📄 {ev.source}  |  pertinence : {pct}%"):
                        st.markdown(f"""
<div style="margin-bottom:.6rem">
  <div class="score-track"><div class="score-fill {bar_cls}" style="width:{pct}%"></div></div>
</div>
""", unsafe_allow_html=True)
                        st.markdown(ev.content[:1400])
            else:
                st.info("Aucune référence trouvée — vérifiez que les documents de la base sont bien chargés.")

        # ── TAB 4 : Profil client ──
        with tab4:
            cp = result.company_profile
            if cp:
                st.markdown('<div class="section-title">Profil entreprise cliente</div>', unsafe_allow_html=True)
                left, right = st.columns(2)
                with left:
                    for label, val in [
                        ("Raison sociale", cp.raison_sociale),
                        ("SIRET", cp.siret or "–"),
                        ("Effectif", cp.effectif),
                        ("Chiffre d'affaires", cp.ca),
                    ]:
                        st.markdown(f'<div style="margin-bottom:.5rem"><span style="color:#64748b;font-size:.8rem">{label}</span><br><span style="color:#e2e8f0">{val}</span></div>', unsafe_allow_html=True)
                with right:
                    for label, val in [
                        ("Ville", cp.ville),
                        ("Secteur", cp.secteur),
                        ("Ancienneté", cp.anciennete),
                        ("Solidité financière", cp.solidite_financiere),
                    ]:
                        st.markdown(f'<div style="margin-bottom:.5rem"><span style="color:#64748b;font-size:.8rem">{label}</span><br><span style="color:#e2e8f0">{val}</span></div>', unsafe_allow_html=True)

                solide = cp.solidite_financiere in ("Bonne", "À vérifier", "A verifier")
                sol_color = "#86efac" if solide else "#fca5a5"
                st.markdown(f'<div style="margin-top:.8rem;color:#64748b;font-size:.75rem">Source données : <span style="color:#3b82f6">{cp.source}</span></div>', unsafe_allow_html=True)

                st.markdown('<div class="section-title" style="margin-top:1.2rem">Disponibilité et capacité de l\'équipe</div>', unsafe_allow_html=True)
                cap = result.capacity
                c1, c2, c3 = st.columns(3)
                c1.metric("Charge de travail actuelle", f"{cap.charge_actuelle_pct}%")
                c2.metric("Disponibilité restante", f"{cap.capacite_restante_pct}%")
                c3.metric("Équipe disponible", "✅ Oui" if cap.equipe_disponible else "❌ Non")
                st.caption(cap.commentaire)

        # ── TAB 5 : Livrables ──
        with tab5:
            st.markdown('<div class="section-title">Documents prêts à être téléchargés</div>', unsafe_allow_html=True)

            col_pdf, col_docx = st.columns(2)
            with col_pdf:
                st.markdown("""
<div style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:1.2rem;text-align:center">
  <div style="font-size:2.5rem">📋</div>
  <div style="color:#e2e8f0;font-weight:700;margin:.4rem 0">Rapport de décision</div>
  <div style="color:#64748b;font-size:.8rem">PDF · Note globale · Points bloquants · Atouts et faiblesses</div>
</div>""", unsafe_allow_html=True)
                if files.get("pdf") and Path(files["pdf"]).exists():
                    with open(files["pdf"], "rb") as f:
                        st.download_button("⬇️ Télécharger PDF", f, file_name=Path(files["pdf"]).name, use_container_width=True, type="primary")

            with col_docx:
                if result.decision == "NO-GO":
                    docx_label = "Mémo de non-réponse"
                    docx_desc  = "DOCX · Analyse blocages · Risques · Conditions reconsidération"
                    docx_btn   = "⬇️ Télécharger le Mémo de non-réponse"
                elif "RESERVE" in result.decision.upper():
                    docx_label = "Dossier conditionnel"
                    docx_desc  = "DOCX · Réserves et conditions · Plan d'action GO · Méthodologie"
                    docx_btn   = "⬇️ Télécharger le Dossier conditionnel"
                else:
                    docx_label = "Dossier de candidature"
                    docx_desc  = "DOCX · Réponse complète · Références · Méthodologie"
                    docx_btn   = "⬇️ Télécharger le Dossier de candidature"
                st.markdown(f"""
<div style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:1.2rem;text-align:center">
  <div style="font-size:2.5rem">📝</div>
  <div style="color:#e2e8f0;font-weight:700;margin:.4rem 0">{docx_label}</div>
  <div style="color:#64748b;font-size:.8rem">{docx_desc}</div>
</div>""", unsafe_allow_html=True)
                if files.get("docx") and Path(files["docx"]).exists():
                    with open(files["docx"], "rb") as f:
                        st.download_button(docx_btn, f, file_name=Path(files["docx"]).name, use_container_width=True)

            # Regénérer
            st.markdown("---")
            if st.button("🔁 Régénérer les documents"):
                with st.spinner("Génération en cours..."):
                    from src.livrables.document_generator import DocumentGenerator
                    dg = DocumentGenerator()
                    new_files = {
                        "pdf":  dg.generate_pdf(ao, result),
                        "docx": dg.generate_docx(ao, result),
                    }
                    st.session_state.current_files = new_files
                    st.success("Documents régénérés avec succès !")
                    st.rerun()

        # ── TAB 6 : AO similaires ──
        with tab6:
            st.markdown('<div class="section-title">Historique des appels d\'offres analysés</div>', unsafe_allow_html=True)
            hist = load_historique()
            if hist:
                for h in reversed(hist[-10:]):
                    dec = h.get("decision","")
                    dec_color = "#22c55e" if dec == "GO" else ("#eab308" if "RESERVE" in dec else "#ef4444")
                    score = h.get("score", 0)
                    techs = ", ".join(h.get("techs", [])) or "–"
                    st.markdown(f"""
<div class="hist-row">
  <div>
    <div class="hist-title">{h.get('titre','–')}</div>
    <div class="hist-meta">{h.get('client','–')} · {h.get('date','–')} · {techs}</div>
  </div>
  <div style="text-align:right">
    <div style="color:{dec_color};font-weight:700;font-size:.9rem">{dec}</div>
    <div style="color:#475569;font-family:'IBM Plex Mono',monospace;font-size:.8rem">{score}/100</div>
  </div>
</div>""", unsafe_allow_html=True)
            else:
                st.info("Aucun appel d'offres dans l'historique pour le moment.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE : HISTORIQUE
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == "Historique":
    st.markdown('<div class="section-title">Historique de tous les appels d\'offres analysés</div>', unsafe_allow_html=True)
    hist = load_historique()

    if not hist:
        st.info("Aucun appel d'offres dans l'historique. Analysez un premier appel d'offres dans l'onglet dédié.")
    else:
        # Filters
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            filter_dec = st.selectbox("Décision", ["Toutes", "GO", "GO SOUS RÉSERVE", "NO-GO"])
        with fc2:
            filter_score = st.slider("Score minimum", 0, 100, 0)
        with fc3:
            filter_search = st.text_input("Rechercher (titre, client, technologie)", "")

        filtered = hist
        if filter_dec != "Toutes":
            filtered = [h for h in filtered if filter_dec.upper().replace("É","E") in h.get("decision","").upper().replace("É","E")]
        if filter_score:
            filtered = [h for h in filtered if h.get("score", 0) >= filter_score]
        if filter_search:
            s = filter_search.lower()
            filtered = [h for h in filtered if s in h.get("titre","").lower()
                        or s in h.get("client","").lower()
                        or any(s in t.lower() for t in h.get("techs",[]))]

        st.caption(f"{len(filtered)} appels d'offres affichés sur {len(hist)}")

        for h in reversed(filtered):
            dec = h.get("decision","")
            dec_color = "#22c55e" if dec == "GO" else ("#eab308" if "RESERVE" in dec else "#ef4444")
            score = h.get("score", 0)
            score_color = "#22c55e" if score >= 75 else ("#eab308" if score >= 58 else "#ef4444")
            techs = ", ".join(h.get("techs", [])) or "–"
            budget = f"{h['budget']:,.0f} €" if h.get("budget") else "–"

            st.markdown(f"""
<div class="hist-row" style="align-items:flex-start">
  <div style="flex:1">
    <div class="hist-title">{h.get('titre','–')}</div>
    <div class="hist-meta">
      {h.get('client','–')} · {h.get('secteur','–')} · Budget : {budget}<br>
      Technologies : {techs} · Analysé le {h.get('date','–')}
    </div>
  </div>
  <div style="text-align:right;min-width:100px">
    <div style="color:{dec_color};font-weight:700;font-size:.88rem">{dec}</div>
    <div style="color:{score_color};font-family:'IBM Plex Mono',monospace;font-size:1.1rem;font-weight:700">{score}/100</div>
    <div style="color:#475569;font-size:.72rem">{h.get('resultat','en attente')}</div>
  </div>
</div>""", unsafe_allow_html=True)

        # Export CSV
        st.markdown("---")
        if st.button("📥 Exporter en tableur (CSV)"):
            df_hist = pd.DataFrame(hist)
            csv = df_hist.to_csv(index=False).encode("utf-8")
            st.download_button("Télécharger CSV", csv, "historique_ao.csv", "text/csv", use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE : BASE REG
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == "Base de référence":
    st.markdown('<div class="section-title">Base de référence documentaire — WinMarket AI</div>', unsafe_allow_html=True)

    pipeline = get_pipeline()
    docs = pipeline.rag.docs
    sources = pipeline.rag.sources

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Documents disponibles", len(docs))
    kpi2.metric("Taille totale", f"{sum(len(d) for d in docs) // 1000} Ko")
    kpi3.metric("Dernière mise à jour", "Au démarrage")

    if st.button("🔄 Recharger la base de référence", use_container_width=True):
        pipeline.rag.load()
        st.success(f"Base de référence rechargée : {len(pipeline.rag.docs)} documents")
        st.rerun()

    st.markdown("---")
    st.markdown('<div class="section-title">Documents indexés</div>', unsafe_allow_html=True)

    # Group by folder
    groups = {}
    for src, doc in zip(sources, docs):
        folder = src.split("/")[0] if "/" in src else "racine"
        if folder not in groups:
            groups[folder] = []
        groups[folder].append((src, doc))

    for folder, items in sorted(groups.items()):
        with st.expander(f"📁 {folder}  ({len(items)} documents)"):
            for src, doc in items:
                st.markdown(f'<div style="color:#94a3b8;font-size:.8rem;margin-bottom:.2rem">📄 {src} <span style="color:#475569">({len(doc):,} caractères)</span></div>', unsafe_allow_html=True)

    # Test search
    st.markdown("---")
    st.markdown('<div class="section-title">Tester une recherche dans la base</div>', unsafe_allow_html=True)
    test_query = st.text_input("Mot-clé ou phrase à rechercher", placeholder="Ex : développement web, migration cloud, cybersécurité...")
    if test_query:
        results = pipeline.rag.search(test_query, top_k=5)
        st.caption(f"{len(results)} résultats")
        for ev in results:
            pct = min(int(ev.score * 400), 100)
            bar_cls = "fill-high" if pct >= 60 else ("fill-med" if pct >= 30 else "fill-low")
            with st.expander(f"📄 {ev.source}  |  pertinence : {min(int(ev.score * 400), 100)}%"):
                st.markdown(f'<div class="score-track" style="margin-bottom:.5rem"><div class="score-fill {bar_cls}" style="width:{pct}%"></div></div>', unsafe_allow_html=True)
                st.markdown(ev.content[:800])

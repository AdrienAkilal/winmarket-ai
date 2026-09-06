"""Reusable Streamlit editor for the operational capacity plan."""
import streamlit as st

from src.core.capacity_repository import CapacityPlan, CapacityRepository


def render_capacity_editor(pipeline) -> None:
    repository = CapacityRepository()
    plan = repository.load()
    available = max(0, 100 - plan.charge_globale_pct)

    c1, c2, c3, c4 = st.columns([1, 1, 1, 1.4])
    c1.metric("Charge équipe", f"{plan.charge_globale_pct}%")
    c2.metric("Disponibilité", f"{available}%")
    c3.metric("Projets en cours", plan.nombre_projets_en_cours)

    with c4:
        editor = st.popover("⚙️ Modifier les disponibilités", use_container_width=True)

    with editor:
        st.caption("Ces valeurs seront utilisées dès la prochaine analyse et ajoutées à la base RAG.")
        with st.form("capacity_editor_form"):
            charge = st.slider("Charge globale actuelle", 0, 100, plan.charge_globale_pct, format="%d %%")
            project_count = st.number_input(
                "Nombre de projets en cours", min_value=0, max_value=999,
                value=plan.nombre_projets_en_cours, step=1,
            )
            projects_text = st.text_area(
                "Noms des projets en cours (facultatif, un par ligne)",
                value="\n".join(plan.projets_en_cours), height=110,
            )
            st.markdown("**Disponibilité par pôle**")
            poles = {
                pole: st.slider(pole, 0, 100, value, format="%d %%", key=f"capacity_{pole}")
                for pole, value in plan.capacites_par_pole.items()
            }
            submitted = st.form_submit_button("Enregistrer les disponibilités", type="primary")
        if submitted:
            repository.save(CapacityPlan(
                charge_globale_pct=charge,
                nombre_projets_en_cours=int(project_count),
                projets_en_cours=projects_text.splitlines(),
                capacites_par_pole=poles,
            ))
            pipeline.rag.load()
            st.success("Disponibilités enregistrées et base RAG rechargée.")
            st.rerun()

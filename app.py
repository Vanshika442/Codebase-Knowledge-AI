import time
from typing import Any, Dict, List

import streamlit as st

from indexer import build_index
from retriever import answer_question

st.set_page_config(
    page_title="Codebase Knowledge AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styles ----------
st.markdown("""
<style>
  .stApp {
    background:
      radial-gradient(900px 500px at 10% -10%, rgba(236,72,153,0.22), transparent 60%),
      radial-gradient(800px 480px at 95% 0%, rgba(59,130,246,0.22), transparent 58%),
      radial-gradient(700px 420px at 50% 110%, rgba(16,185,129,0.16), transparent 55%),
      #0D0B1A;
  }

  .block-container {
    padding-top: 2.4rem !important;
    padding-bottom: 2rem;
    max-width: 1240px;
  }

  .app-title {
    font-size: 2.4rem;
    font-weight: 800;
    line-height: 1.3;
    margin: 0.25rem 0 0.35rem 0;
    letter-spacing: 0.2px;
    color: #F9FAFB;
    display: block;
  }

  .app-sub {
    color: #C4B5FD;
    margin-bottom: 1.1rem;
    font-size: 1rem;
    display: block;
  }

  .kpi {
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 14px;
    padding: 14px 16px;
    background: linear-gradient(135deg, rgba(255,255,255,.06), rgba(255,255,255,.02));
    backdrop-filter: blur(6px);
  }

  .kpi-label {font-size: .78rem; color: #C4B5FD;}
  .kpi-value {font-size: 1.2rem; font-weight: 700; margin-top: 6px; color: #F9FAFB;}

  .section-title {
    font-size: 1.1rem;
    font-weight: 700;
    margin: .45rem 0 .7rem;
    color: #F9FAFB;
  }

  .hint {color:#A78BFA; font-size: .88rem; margin-bottom: 1rem; display: block;}

  .citation {
    border: 1px solid rgba(255,255,255,.14);
    border-radius: 10px;
    padding: 8px 12px;
    margin: 6px 0;
    background: rgba(255,255,255,.04);
    font-family: monospace;
    font-size: 0.85rem;
    color: #86EFAC;
  }

  .ast-hint {
    border-left: 3px solid #D946EF;
    padding: 4px 10px;
    margin: 4px 0;
    font-size: 0.875rem;
    color: #E9D5FF;
    background: rgba(217,70,239,0.07);
    border-radius: 0 8px 8px 0;
  }

  .answer-box {
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(255,255,255,.1);
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 1rem;
    color: #F3F4F6;
    line-height: 1.7;
  }
</style>
""", unsafe_allow_html=True)

# ---------- Session State ----------
if "repo_id" not in st.session_state:
    st.session_state.repo_id = ""
if "index_summary" not in st.session_state:
    st.session_state.index_summary = None
if "last_answer" not in st.session_state:
    st.session_state.last_answer = None
if "query_latency" not in st.session_state:
    st.session_state.query_latency = None

# ---------- Header ----------
st.markdown('<span class="app-title">⚡ Codebase Knowledge AI</span>', unsafe_allow_html=True)
st.markdown(
    '<span class="app-sub">Repository indexing · AST-aware retrieval · Cited code answers</span>',
    unsafe_allow_html=True,
)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### ⚙️ Workspace")
    st.markdown("Use one repository at a time for best retrieval quality.")
    st.markdown("---")
    st.markdown("### Settings")
    top_k = st.slider("Top-K retrieval", min_value=2, max_value=12, value=5)
    show_context = st.toggle("Show retrieved contexts", value=True)
    st.markdown("---")
    st.caption("Tip: Re-index after changing indexer/retriever logic.")
    st.markdown("---")
    if st.session_state.repo_id:
        st.success(f"Active: {st.session_state.repo_id}")
    else:
        st.warning("No repo indexed yet.")

# ---------- KPI Row ----------
col1, col2, col3, col4 = st.columns(4)
with col1:
    value = st.session_state.repo_id if st.session_state.repo_id else "Not selected"
    st.markdown(
        f'<div class="kpi"><div class="kpi-label">Active Repo ID</div>'
        f'<div class="kpi-value">{value}</div></div>',
        unsafe_allow_html=True,
    )
with col2:
    files_loaded = "-"
    if st.session_state.index_summary:
        files_loaded = st.session_state.index_summary.get("files_loaded", "-")
    st.markdown(
        f'<div class="kpi"><div class="kpi-label">Indexed Files</div>'
        f'<div class="kpi-value">{files_loaded}</div></div>',
        unsafe_allow_html=True,
    )
with col3:
    chunks = "-"
    if st.session_state.index_summary:
        chunks = st.session_state.index_summary.get("chunks_indexed", "-")
    st.markdown(
        f'<div class="kpi"><div class="kpi-label">Indexed Chunks</div>'
        f'<div class="kpi-value">{chunks}</div></div>',
        unsafe_allow_html=True,
    )
with col4:
    latency = st.session_state.query_latency
    latency_text = f"{latency:.2f}s" if isinstance(latency, (int, float)) else "-"
    st.markdown(
        f'<div class="kpi"><div class="kpi-label">Last Query Latency</div>'
        f'<div class="kpi-value">{latency_text}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br/>", unsafe_allow_html=True)

# ---------- Main Tabs ----------
tab_index, tab_query, tab_sources = st.tabs([
    "🗂 Index Repository",
    "💬 Ask Questions",
    "📊 Index Details",
])

# ---- Tab 1: Index ----
with tab_index:
    st.markdown('<div class="section-title">Repository Indexing</div>', unsafe_allow_html=True)
    st.markdown(
        '<span class="hint">Enter a local path or GitHub URL. '
        'Existing repo will be pulled if already cloned.</span>',
        unsafe_allow_html=True,
    )

    with st.form("index_form", clear_on_submit=False):
        repo_input = st.text_input(
            "Repository Path or URL",
            placeholder="https://github.com/user/repo.git  or  C:/projects/my-repo",
        )
        submitted = st.form_submit_button("⚡ Build / Refresh Index", use_container_width=True)

    if submitted:
        if not repo_input.strip():
            st.warning("Please provide a repository path or URL.")
        else:
            with st.spinner("Indexing repository. This may take a while on CPU..."):
                try:
                    summary = build_index(repo_input.strip())
                    st.session_state.repo_id = summary.get("repo_id", "")
                    st.session_state.index_summary = summary
                    st.success(f"Index completed. Repo ID: `{summary.get('repo_id')}`")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Total Files", summary.get("total_files_in_repo", "-"))
                    c2.metric("Indexed Files", summary.get("files_loaded", "-"))
                    c3.metric("Chunks", summary.get("chunks_indexed", "-"))
                except Exception as e:
                    st.exception(e)

# ---- Tab 2: Query ----
with tab_query:
    st.markdown('<div class="section-title">Codebase Q&A</div>', unsafe_allow_html=True)
    st.markdown(
        '<span class="hint">Ask architecture, flow, function, and module-level questions.</span>',
        unsafe_allow_html=True,
    )

    q_col1, q_col2 = st.columns([3, 1])
    with q_col1:
        repo_id = st.text_input(
            "Repo ID",
            value=st.session_state.repo_id,
            placeholder="example: fetal_prediction_app",
        )
    with q_col2:
        st.markdown("<br/>", unsafe_allow_html=True)
        ask_btn = st.button("🔍 Run Query", use_container_width=True)

    question = st.text_area(
        "Your Question",
        height=110,
        placeholder="Where is the prediction pipeline defined? How does auth flow work?",
    )

    if ask_btn:
        if not repo_id.strip():
            st.warning("Repo ID is required.")
        elif not question.strip():
            st.warning("Question is required.")
        else:
            start = time.time()
            with st.spinner("Retrieving context and generating answer..."):
                try:
                    result = answer_question(
                        repo_id=repo_id.strip(),
                        question=question.strip(),
                        top_k=top_k,
                    )
                    st.session_state.last_answer = result
                    st.session_state.query_latency = time.time() - start
                    st.rerun()
                except Exception as e:
                    st.exception(e)

    if st.session_state.last_answer:
        result: Dict[str, Any] = st.session_state.last_answer

        # Answer
        st.markdown("#### 💡 Answer")
        st.markdown(
            f'<div class="answer-box">{result.get("answer", "No answer returned.")}</div>',
            unsafe_allow_html=True,
        )

        # Citations
        st.markdown("#### 📎 Citations")
        citations: List[str] = result.get("citations", [])
        if citations:
            for c in citations:
                st.markdown(f'<div class="citation">📄 {c}</div>', unsafe_allow_html=True)
        else:
            st.info("No citations returned.")

        # AST Hints
        ast_hints: List[Dict[str, Any]] = result.get("ast_hints", [])
        if ast_hints:
            st.markdown("#### 🧠 AST Symbol Hints")
            with st.expander("View AST Hints", expanded=True):
                for h in ast_hints:
                    typ = h.get("type", "symbol")
                    name = h.get("name", "")
                    file_ = h.get("file", "unknown")
                    sl = h.get("start_line")
                    el = h.get("end_line")
                    if sl and el:
                        st.markdown(
                            f'<div class="ast-hint">'
                            f'<b>{typ}</b>: <code>{name}</code> → '
                            f'<code>{file_}:{sl}-{el}</code>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f'<div class="ast-hint">'
                            f'<b>{typ}</b>: <code>{name}</code> → '
                            f'<code>{file_}</code>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

        # Retrieved Contexts
        if show_context:
            st.markdown("#### 🔍 Retrieved Contexts")
            contexts = result.get("contexts", [])
            if contexts:
                for i, item in enumerate(contexts, start=1):
                    src = item.get("source", "unknown")
                    s = item.get("start_line", "?")
                    e = item.get("end_line", "?")
                    score = item.get("score", None)
                    score_text = f"{score:.4f}" if isinstance(score, (int, float)) else "N/A"
                    with st.expander(f"{i}. {src}:{s}-{e} | score: {score_text}"):
                        st.code(item.get("text", ""), language="python")
            else:
                st.info("No contexts returned.")

# ---- Tab 3: Index Details ----
with tab_sources:
    st.markdown('<div class="section-title">Index Build Summary</div>', unsafe_allow_html=True)
    if st.session_state.index_summary:
        summary = st.session_state.index_summary

        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Total Files", summary.get("total_files_in_repo", "-"))
        d2.metric("Indexed Files", summary.get("files_loaded", "-"))
        d3.metric("Chunks", summary.get("chunks_indexed", "-"))
        d4.metric("AST Files Parsed", summary.get("ast_files_parsed", "-"))

        st.markdown("<br/>", unsafe_allow_html=True)
        st.json(summary)

        indexed_list = summary.get("indexed_files_list", [])
        if indexed_list:
            st.markdown("#### Indexed Files")
            st.dataframe(
                {"file": indexed_list},
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.info("No index summary yet. Build index first from the Index Repository tab.")
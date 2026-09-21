
from __future__ import annotations

import os
import re
import io
import csv
import json
import math
import sqlite3
import hashlib
from pathlib import Path
from datetime import date, datetime
from typing import List, Dict, Any, Optional

import numpy as np
import pandas as pd
import streamlit as st
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"
DB_PATH = DATA_DIR / "agent.db"

DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="Agente Normativo PyC Pro",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- ESTILO --------------------
st.markdown("""
<style>
:root{
  --brand:#ff4b55;
  --brand2:#b81f2e;
  --ink:#15213a;
  --muted:#6f788c;
  --line:#e3e7ef;
  --soft:#f7f8fb;
  --ok:#14804a;
  --warn:#b76e00;
}
[data-testid="stAppViewContainer"] { background:#fff; }
[data-testid="stSidebar"] {
  background:linear-gradient(180deg,#f6f8fb 0%,#eef2f7 100%);
  border-right:1px solid #e4e8ef;
}
.block-container{
  max-width:1280px;
  padding-top:1.55rem;
  padding-bottom:2rem;
}
h1,h2,h3 { color:var(--ink); }
.hero{
  border:1px solid #e8ebf2;
  border-radius:18px;
  padding:22px 24px;
  background:
    radial-gradient(circle at 95% 10%, rgba(255,75,85,.10), transparent 28%),
    linear-gradient(135deg,#fff,#fbfcff);
  box-shadow:0 8px 30px rgba(16,24,40,.05);
  margin-bottom:14px;
}
.hero-title{
  font-weight:850;
  font-size:36px;
  color:var(--ink);
  letter-spacing:-.6px;
}
.hero-sub{ color:var(--muted); margin-top:4px; font-size:15px; }
.badge{
  display:inline-block;
  padding:5px 10px;
  border-radius:999px;
  font-size:12px;
  font-weight:700;
  background:#fff0f1;
  color:#a92431;
  border:1px solid #ffd2d7;
  margin-right:6px;
}
.kpi{
  border:1px solid #e6eaf0;
  background:#fff;
  padding:15px 16px;
  border-radius:14px;
  box-shadow:0 4px 16px rgba(16,24,40,.035);
}
.ev{
  border:1px solid #eceff4;
  border-left:4px solid var(--brand);
  border-radius:10px;
  padding:12px 14px;
  background:#fffafb;
  margin:8px 0;
}
.ev strong{ color:var(--ink); }
.muted{ color:var(--muted); font-size:13px; }
.score-high{ color:#14804a; font-weight:700; }
.score-mid{ color:#b76e00; font-weight:700; }
.score-low{ color:#b42318; font-weight:700; }
.answer-box{
  border:1px solid #e5e9f0;
  background:#fcfdff;
  padding:16px 18px;
  border-radius:12px;
}
.source-chip{
  display:inline-block;
  border:1px solid #e0e5ec;
  background:#fff;
  padding:4px 8px;
  border-radius:999px;
  margin:2px 4px 2px 0;
  font-size:12px;
}
div.stButton > button { border-radius:9px; }

/* ===== PyC hardening visual / mobile ===== */

/* Oculta controles de Streamlit Community Cloud */
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { visibility: hidden !important; }
[data-testid="stAppDeployButton"] { display: none !important; }
button[title="View app source"] { display: none !important; }
a[href*="github.com"] { display: none !important; }

/* Mantiene el header técnico invisible pero conserva el espacio necesario */
header[data-testid="stHeader"] {
  background: transparent !important;
  height: 0 !important;
}

/* Sidebar: fondo opaco y texto legible, independiente del modo del teléfono */
section[data-testid="stSidebar"] {
  background: #f3f6fa !important;
  border-right: 1px solid #e1e6ee !important;
}
section[data-testid="stSidebar"] * {
  color: #17233d !important;
}
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
  background: #ffffff !important;
  color: #17233d !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] * {
  color: #17233d !important;
}
section[data-testid="stSidebar"] hr {
  border-color: #d9dee8 !important;
}

/* Botón de cierre / apertura del sidebar */
[data-testid="stSidebarCollapseButton"] button,
[data-testid="collapsedControl"] button {
  background: #ffffff !important;
  border: 1px solid #dfe4ec !important;
  color: #17233d !important;
  border-radius: 9px !important;
}

/* Inputs principales siempre claros */
[data-testid="stAppViewContainer"] input,
[data-testid="stAppViewContainer"] textarea,
[data-testid="stAppViewContainer"] [data-baseweb="select"] > div {
  background-color: #ffffff !important;
  color: #17233d !important;
}

/* Mobile */
@media (max-width: 768px) {
  .block-container {
    padding-left: 0.85rem !important;
    padding-right: 0.85rem !important;
    padding-top: 0.8rem !important;
  }

  .hero {
    padding: 16px 16px !important;
    border-radius: 14px !important;
  }

  .hero-title {
    font-size: 27px !important;
    line-height: 1.08 !important;
  }

  .hero-sub {
    font-size: 13px !important;
  }

  section[data-testid="stSidebar"] {
    width: 86vw !important;
    min-width: 86vw !important;
    max-width: 360px !important;
    box-shadow: 8px 0 28px rgba(15, 23, 42, .14) !important;
  }

  /* evita la sensación de contenido "lavado" bajo el drawer */
  [data-testid="stSidebar"][aria-expanded="true"] {
    opacity: 1 !important;
  }

  /* Tabs desplazables y sin apretar contenido */
  [data-baseweb="tab-list"] {
    gap: 8px !important;
    overflow-x: auto !important;
    scrollbar-width: none !important;
  }
  [data-baseweb="tab-list"]::-webkit-scrollbar {
    display: none !important;
  }
  [data-baseweb="tab"] {
    flex: 0 0 auto !important;
    white-space: nowrap !important;
  }

  /* Chat e inputs cómodos en iPhone */
  [data-testid="stChatInput"] {
    padding-bottom: calc(env(safe-area-inset-bottom) + 8px) !important;
  }

  /* Métricas una debajo de otra cuando no caben */
  [data-testid="stMetric"] {
    min-width: 0 !important;
  }
}


/* V3: experiencia simplificada por perfil */
@media (max-width: 768px) {
  section[data-testid="stSidebar"] .stSelectbox,
  section[data-testid="stSidebar"] .stToggle,
  section[data-testid="stSidebar"] .stSlider,
  section[data-testid="stSidebar"] .stTextInput {
    margin-bottom: .35rem !important;
  }
  section[data-testid="stSidebar"] details {
    background: #ffffff !important;
    border: 1px solid #e4e8ef !important;
    border-radius: 10px !important;
    padding: 2px 8px !important;
  }
}

</style>
""", unsafe_allow_html=True)

# -------------------- DB --------------------
def db():
    return sqlite3.connect(DB_PATH)

def init_db():
    con = db()
    cur = con.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS documents(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        sha256 TEXT NOT NULL UNIQUE,
        area TEXT,
        tipo TEXT,
        version TEXT,
        fecha_publicacion TEXT,
        vigencia_desde TEXT,
        vigencia_hasta TEXT,
        estado TEXT,
        fuente_url TEXT,
        etiquetas TEXT,
        reemplaza_a TEXT,
        pages INTEGER DEFAULT 0,
        chars INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS chunks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER NOT NULL,
        page INTEGER NOT NULL,
        chunk_no INTEGER NOT NULL,
        text TEXT NOT NULL,
        FOREIGN KEY(document_id) REFERENCES documents(id)
    );
    CREATE TABLE IF NOT EXISTS queries(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        question TEXT NOT NULL,
        provider TEXT,
        evidence_count INTEGER,
        top_score REAL,
        avg_score REAL,
        no_evidence INTEGER DEFAULT 0,
        latency_ms INTEGER DEFAULT 0,
        filters_json TEXT
    );
    CREATE TABLE IF NOT EXISTS qa_cases(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        expected_document TEXT,
        expected_text TEXT,
        notes TEXT,
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS qa_runs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        qa_case_id INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        found_expected_doc INTEGER,
        top_score REAL,
        evidence_count INTEGER,
        FOREIGN KEY(qa_case_id) REFERENCES qa_cases(id)
    );
    """)
    con.commit()
    con.close()

init_db()

# -------------------- PERFIL / EXPERIENCIA --------------------
if "user_role" not in st.session_state:
    st.session_state["user_role"] = "Usuario"
if "show_advanced" not in st.session_state:
    st.session_state["show_advanced"] = False

# -------------------- HELPERS --------------------
def clean_text(s: str) -> str:
    s = (s or "").replace("\x00"," ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def chunk_page(text: str, max_chars=1300, overlap=180):
    text = clean_text(text)
    if not text:
        return []
    paras = re.split(r"\n\s*\n|(?<=[\.\:\;])\s+(?=[A-ZÁÉÍÓÚÑ0-9])", text)
    out, buf = [], ""
    for p in paras:
        p = clean_text(p)
        if not p:
            continue
        if len(buf) + len(p) + 1 <= max_chars:
            buf = (buf + " " + p).strip()
        else:
            if buf:
                out.append(buf)
            tail = buf[-overlap:] if buf else ""
            buf = (tail + " " + p).strip()
    if buf:
        out.append(buf)
    return out

def parse_pdf(data: bytes):
    reader = PdfReader(io.BytesIO(data))
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            txt = clean_text(page.extract_text() or "")
        except Exception:
            txt = ""
        pages.append((i, txt))
    return pages

def add_document(file, meta):
    raw = file.getvalue()
    digest = sha256_bytes(raw)
    con = db()
    cur = con.cursor()
    existing = cur.execute("SELECT id, filename FROM documents WHERE sha256=?", (digest,)).fetchone()
    if existing:
        con.close()
        return False, f"Documento duplicado: ya existe como {existing[1]}."

    pages = parse_pdf(raw)
    char_count = sum(len(t) for _, t in pages)
    saved = UPLOAD_DIR / file.name
    saved.write_bytes(raw)

    cur.execute("""
        INSERT INTO documents(
            filename, sha256, area, tipo, version, fecha_publicacion,
            vigencia_desde, vigencia_hasta, estado, fuente_url, etiquetas,
            reemplaza_a, pages, chars, created_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        file.name, digest, meta["area"], meta["tipo"], meta["version"],
        meta["fecha_publicacion"], meta["vigencia_desde"], meta["vigencia_hasta"],
        meta["estado"], meta["fuente_url"], meta["etiquetas"], meta["reemplaza_a"],
        len(pages), char_count, datetime.now().isoformat(timespec="seconds")
    ))
    doc_id = cur.lastrowid

    for page_no, txt in pages:
        for n, ch in enumerate(chunk_page(txt)):
            cur.execute(
                "INSERT INTO chunks(document_id,page,chunk_no,text) VALUES (?,?,?,?)",
                (doc_id, page_no, n, ch)
            )
    con.commit()
    con.close()
    return True, f"{file.name}: {len(pages)} páginas y {char_count:,} caracteres indexados."

def get_documents(active_only=False, area=None, as_of=None):
    con = db()
    q = "SELECT * FROM documents WHERE 1=1"
    params = []
    if active_only:
        q += " AND estado='Vigente'"
    if area and area != "Todas":
        q += " AND area=?"
        params.append(area)
    if as_of:
        q += " AND (vigencia_desde IS NULL OR vigencia_desde='' OR vigencia_desde<=?)"
        q += " AND (vigencia_hasta IS NULL OR vigencia_hasta='' OR vigencia_hasta>=?)"
        params.extend([as_of, as_of])
    rows = pd.read_sql_query(q + " ORDER BY created_at DESC", con, params=params)
    con.close()
    return rows

def get_search_corpus(active_only=True, area=None, as_of=None):
    con = db()
    q = """
    SELECT c.id chunk_id, c.page, c.chunk_no, c.text,
           d.id document_id, d.filename, d.area, d.tipo, d.version,
           d.vigencia_desde, d.vigencia_hasta, d.estado
    FROM chunks c
    JOIN documents d ON d.id=c.document_id
    WHERE 1=1
    """
    params = []
    if active_only:
        q += " AND d.estado='Vigente'"
    if area and area != "Todas":
        q += " AND d.area=?"
        params.append(area)
    if as_of:
        q += " AND (d.vigencia_desde IS NULL OR d.vigencia_desde='' OR d.vigencia_desde<=?)"
        q += " AND (d.vigencia_hasta IS NULL OR d.vigencia_hasta='' OR d.vigencia_hasta>=?)"
        params.extend([as_of, as_of])
    rows = pd.read_sql_query(q, con, params=params)
    con.close()
    return rows

STOP = set("""
de la el los las un una unos unas y o u en por para con sin sobre entre desde hasta que qué
como cómo cual cuál cuales cuáles es son fue eran será se su sus al del lo más menos muy
""".split())

def tokenize(s):
    return [x for x in re.findall(r"[a-záéíóúñ0-9]{2,}", (s or "").lower()) if x not in STOP]

def keyword_score(question, text):
    q = set(tokenize(question))
    t = set(tokenize(text))
    if not q:
        return 0.0
    return len(q & t) / max(1, len(q))

def retrieve(question, final_k, candidates, threshold, lexical_weight, area, as_of, active_only=True):
    corpus = get_search_corpus(active_only=active_only, area=area, as_of=as_of)
    if corpus.empty:
        return []

    texts = corpus["text"].fillna("").tolist()
    try:
        vect = TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            ngram_range=(1,2),
            min_df=1,
            sublinear_tf=True,
            max_features=50000
        )
        m = vect.fit_transform(texts + [question])
        semantic = cosine_similarity(m[-1], m[:-1]).flatten()
    except Exception:
        semantic = np.zeros(len(texts))

    lexical = np.array([keyword_score(question, t) for t in texts])
    hybrid = (1 - lexical_weight) * semantic + lexical_weight * lexical

    idx = np.argsort(hybrid)[::-1][:max(candidates, final_k)]
    out = []
    seen = set()
    for i in idx:
        score = float(hybrid[i])
        if score < threshold:
            continue
        row = corpus.iloc[int(i)].to_dict()
        key = (row["document_id"], row["page"], row["chunk_no"])
        if key in seen:
            continue
        seen.add(key)
        row["semantic_score"] = float(semantic[i])
        row["lexical_score"] = float(lexical[i])
        row["score"] = score
        out.append(row)
        if len(out) >= final_k:
            break
    return out

def source_label(e):
    return f"{e['filename']} · pág. {int(e['page'])}"

def local_answer(question, evidence):
    if not evidence:
        return "No encontré evidencia suficiente en la base documental cargada."
    lines = [
        "Encontré evidencia relevante en la base documental. "
        "Como el modo generativo no está activo, presento una respuesta extractiva y las fuentes asociadas.",
        ""
    ]
    for i, e in enumerate(evidence[:3], 1):
        snippet = clean_text(e["text"])
        if len(snippet) > 520:
            snippet = snippet[:520].rstrip() + "…"
        lines.append(f"**{i}. {source_label(e)}**")
        lines.append(snippet)
        lines.append("")
    return "\n".join(lines)

def gemini_answer(question, evidence, api_key):
    context = "\n\n".join(
        f"[FUENTE {i}: {source_label(e)} | score={e['score']:.3f}]\n{e['text']}"
        for i, e in enumerate(evidence, 1)
    )
    prompt = f"""
Actúa como asistente normativo bancario con política de evidencia estricta.

REGLAS:
1. Responde exclusivamente con la evidencia entregada.
2. Si falta evidencia suficiente, responde exactamente:
   "No encontré evidencia suficiente en la base documental cargada."
3. No inventes artículos, obligaciones, fechas, límites ni referencias.
4. Cuando afirmes algo relevante, agrega la cita entre paréntesis usando este formato:
   (Documento.pdf, pág. X)
5. Si las fuentes se contradicen, indícalo explícitamente y no resuelvas la contradicción por tu cuenta.
6. Distingue claramente entre una obligación normativa y una explicación contextual.
7. Sé conciso pero preciso.

PREGUNTA:
{question}

EVIDENCIA:
{context}
"""
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return resp.text
    except Exception as e:
        return f"No fue posible consultar Gemini. Detalle técnico: {e}"

def log_query(question, provider, evidence, latency_ms, filters):
    con = db()
    cur = con.cursor()
    top = max([e["score"] for e in evidence], default=0)
    avg = (sum(e["score"] for e in evidence)/len(evidence)) if evidence else 0
    cur.execute("""
    INSERT INTO queries(created_at,question,provider,evidence_count,top_score,avg_score,no_evidence,latency_ms,filters_json)
    VALUES(?,?,?,?,?,?,?,?,?)
    """, (
        datetime.now().isoformat(timespec="seconds"), question, provider, len(evidence),
        top, avg, 0 if evidence else 1, latency_ms, json.dumps(filters, ensure_ascii=False)
    ))
    con.commit()
    con.close()

def delete_doc(doc_id):
    con = db()
    cur = con.cursor()
    cur.execute("DELETE FROM chunks WHERE document_id=?", (doc_id,))
    cur.execute("DELETE FROM documents WHERE id=?", (doc_id,))
    con.commit()
    con.close()

def score_class(s):
    if s >= .55: return "score-high"
    if s >= .25: return "score-mid"
    return "score-low"

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.markdown("## ⚖️ Agente Normativo")
    st.caption("PyC · Edición Pro")
    st.divider()

    st.markdown("### Perfil")
    role = st.selectbox(
        "Modo de uso",
        ["Usuario", "Administrador"],
        index=0 if st.session_state.get("user_role","Usuario") == "Usuario" else 1,
        help="En esta demo el selector simula el perfil. En producción se reemplaza por login/SSO."
    )
    st.session_state["user_role"] = role

    # Valores por defecto seguros para usuarios normales
    final_k = 6
    candidates = 25
    threshold = 0.10
    lexical_weight = 0.30
    area_filter = "Todas"
    active_only = True
    use_asof = False
    as_of = date.today()
    as_of_str = None
    provider = "Modo extractivo local"
    api_key = ""
    strict_mode = True

    docs_df = get_documents()
    areas = ["Todas"] + sorted([x for x in docs_df["area"].dropna().unique().tolist() if x]) if not docs_df.empty else ["Todas"]

    if role == "Administrador":
        st.markdown("### Configuración avanzada")
        show_advanced = st.toggle(
            "Mostrar parámetros",
            value=st.session_state.get("show_advanced", False),
            help="Oculta los parámetros cuando no los necesitas."
        )
        st.session_state["show_advanced"] = show_advanced

        if show_advanced:
            with st.expander("🔎 Recuperación", expanded=True):
                final_k = st.slider("Fragmentos finales", 3, 12, 6)
                candidates = st.slider("Candidatos iniciales", 5, 60, 25)
                threshold = st.slider("Umbral mínimo", 0.00, 1.00, 0.10, 0.01)
                lexical_weight = st.slider(
                    "Peso búsqueda literal",
                    0.0, 1.0, 0.30, 0.05,
                    help="0 = solo similitud TF-IDF; 1 = solo coincidencia de términos."
                )

            with st.expander("📚 Filtros documentales", expanded=False):
                area_filter = st.selectbox("Área", areas)
                active_only = st.toggle("Solo documentos vigentes", value=True)
                use_asof = st.toggle("Consultar vigencia a una fecha", value=False)
                as_of = st.date_input("Fecha de consulta", value=date.today(), disabled=not use_asof)
                as_of_str = str(as_of) if use_asof else None

            with st.expander("🤖 Generación", expanded=False):
                provider = st.selectbox("Proveedor", ["Gemini", "Modo extractivo local"])
                api_key = st.text_input("API key Gemini", type="password", help="No se persiste en disco.")
                strict_mode = st.toggle(
                    "Modo evidencia estricta",
                    value=True,
                    help="Si no hay evidencia sobre el umbral, no intenta responder."
                )
        else:
            st.caption("Parámetros avanzados ocultos. Se usan valores seguros por defecto.")
            area_filter = "Todas"
            active_only = True
            as_of_str = None
            provider = "Modo extractivo local"
            api_key = ""
            strict_mode = True
    else:
        st.markdown("### Consulta")
        st.caption(
            "Modo simplificado: solo documentos vigentes, evidencia estricta y configuración protegida."
        )
        # Mantener opciones simples y útiles para usuario final
        area_filter = st.selectbox("Área", areas)
        provider = "Modo extractivo local"
        active_only = True
        as_of_str = None
        strict_mode = True

    st.divider()
    if st.button("Limpiar conversación", use_container_width=True):
        st.session_state["chat"] = []
        st.rerun()

# -------------------- HERO --------------------
st.markdown("""
<div class="hero">
  <div>
    <span class="badge">RAG auditable</span>
    <span class="badge">Control de vigencia</span>
    <span class="badge">QA incorporado</span>
  </div>
  <div class="hero-title">Agente Normativo PyC Pro</div>
  <div class="hero-sub">
    Consulta normativa con trazabilidad por documento y página, control de versiones,
    recuperación híbrida y monitoreo de calidad.
  </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.get("user_role") == "Administrador":
    tabs = st.tabs([
        "💬 Consulta",
        "📚 Base documental",
        "⬆️ Ingesta",
        "🧪 Evaluación QA",
        "📊 Monitoreo",
    ])
else:
    tabs = st.tabs([
        "💬 Consulta",
        "📚 Fuentes",
    ])

# -------------------- CONSULTA --------------------
with tabs[0]:
    st.subheader("Consulta normativa")
    st.caption("La respuesta debe poder ser auditada desde su evidencia documental.")

    if "chat" not in st.session_state:
        st.session_state["chat"] = []

    for m in st.session_state["chat"]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m.get("evidence"):
                with st.expander("🔎 Evidencia utilizada", expanded=False):
                    for e in m["evidence"]:
                        cls = score_class(e["score"])
                        st.markdown(
                            f"""<div class="ev">
                            <strong>{source_label(e)}</strong><br>
                            <span class="{cls}">Score {e['score']:.3f}</span>
                            <span class="muted"> · semántico {e['semantic_score']:.3f}
                            · literal {e['lexical_score']:.3f}</span><br><br>
                            {e['text'][:1500]}
                            </div>""",
                            unsafe_allow_html=True
                        )

    q = st.chat_input("Ej.: ¿Cuál es la exigencia aplicable al archivo D10?")
    if q:
        import time
        t0 = time.perf_counter()

        filters = {
            "area": area_filter,
            "as_of": as_of_str,
            "active_only": active_only,
            "threshold": threshold,
            "lexical_weight": lexical_weight
        }
        evidence = retrieve(
            q, final_k, candidates, threshold, lexical_weight,
            area_filter, as_of_str, active_only
        )

        if strict_mode and not evidence:
            answer = "No encontré evidencia suficiente en la base documental cargada."
        elif provider == "Gemini" and api_key and evidence:
            answer = gemini_answer(q, evidence, api_key)
        else:
            answer = local_answer(q, evidence)

        latency = int((time.perf_counter() - t0) * 1000)
        log_query(q, provider, evidence, latency, filters)

        st.session_state["chat"].append({"role":"user","content":q})
        st.session_state["chat"].append({
            "role":"assistant",
            "content":answer,
            "evidence":evidence
        })
        st.rerun()

# -------------------- BASE DOCUMENTAL --------------------
with tabs[1]:
    if st.session_state.get("user_role") == "Administrador":
        st.subheader("Base documental")
        st.caption("Inventario, vigencia, versión y estado de los documentos indexados.")
    else:
        st.subheader("Fuentes disponibles")
        st.caption("Documentos normativos disponibles para tus consultas.")

    ddf = get_documents()
    if ddf.empty:
        st.info("Aún no hay documentos cargados.")
    else:
        show = ddf.rename(columns={
            "filename":"Documento",
            "area":"Área",
            "tipo":"Tipo",
            "version":"Versión",
            "fecha_publicacion":"Publicación",
            "vigencia_desde":"Vigente desde",
            "vigencia_hasta":"Vigente hasta",
            "estado":"Estado",
            "pages":"Páginas",
            "chars":"Caracteres",
            "reemplaza_a":"Reemplaza a",
        })[[
            "Documento","Área","Tipo","Versión","Publicación","Vigente desde",
            "Vigente hasta","Estado","Páginas","Caracteres","Reemplaza a"
        ]]
        st.dataframe(show, use_container_width=True, hide_index=True)

        if st.session_state.get("user_role") == "Administrador":
            st.markdown("### Explorador de recuperación")
            test_q = st.text_input("Pregunta de prueba", value="¿Qué contiene el archivo D10?", key="base_test")
            if st.button("Probar recuperación", type="primary"):
                ev = retrieve(
                    test_q, final_k, candidates, threshold, lexical_weight,
                    area_filter, as_of_str, active_only
                )
                if not ev:
                    st.warning("No se encontraron fragmentos sobre el umbral configurado.")
                else:
                    for i, e in enumerate(ev, 1):
                        st.markdown(
                            f"""<div class="ev">
                            <strong>{i}. {source_label(e)}</strong><br>
                            Área: {e['area']} · Versión: {e['version']} ·
                            Score: {e['score']:.3f}<br><br>
                            {e['text'][:1600]}
                            </div>""",
                            unsafe_allow_html=True
                        )

            st.markdown("### Gestión")
            ids = ddf["id"].tolist()
            opts = {f"{r['filename']} · {r['version']} · ID {r['id']}": int(r["id"]) for _, r in ddf.iterrows()}
            selected = st.selectbox("Documento", list(opts.keys()))
            if st.button("Eliminar documento seleccionado"):
                delete_doc(opts[selected])
                st.success("Documento eliminado de la base y del índice.")
                st.rerun()

if st.session_state.get("user_role") == "Administrador":
    # -------------------- INGESTA --------------------
    with tabs[2]:
        st.subheader("Ingesta controlada")
        st.caption("La metadata permite distinguir versiones, vigencia y reemplazos.")

        files = st.file_uploader(
            "Selecciona uno o más PDF",
            type=["pdf"],
            accept_multiple_files=True
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            area = st.text_input("Área", placeholder="Ej.: Contables")
            tipo = st.selectbox("Tipo documental", [
                "Norma", "Circular", "Capítulo", "Manual", "Anexo", "Otro"
            ])
            version = st.text_input("Versión", value=str(date.today()))
        with c2:
            pub = st.date_input("Fecha de publicación", value=date.today())
            vig_desde = st.date_input("Vigencia desde", value=date.today())
            has_end = st.checkbox("Tiene fin de vigencia", value=False)
            vig_hasta = st.date_input("Vigencia hasta", value=date.today(), disabled=not has_end)
        with c3:
            estado = st.selectbox("Estado", ["Vigente", "Borrador", "No vigente"])
            fuente_url = st.text_input("URL oficial / fuente")
            etiquetas = st.text_input("Etiquetas", placeholder="RCD, deuda, CMF")
            reemplaza_a = st.text_input("Reemplaza a", placeholder="Nombre o versión anterior")

        if st.button("Incorporar a la base", type="primary", disabled=not files):
            messages = []
            for f in files or []:
                ok, msg = add_document(f, {
                    "area": area or "Sin clasificar",
                    "tipo": tipo,
                    "version": version,
                    "fecha_publicacion": str(pub),
                    "vigencia_desde": str(vig_desde),
                    "vigencia_hasta": str(vig_hasta) if has_end else "",
                    "estado": estado,
                    "fuente_url": fuente_url,
                    "etiquetas": etiquetas,
                    "reemplaza_a": reemplaza_a,
                })
                messages.append((ok, msg))
            for ok, msg in messages:
                st.success(msg) if ok else st.warning(msg)
            if any(ok for ok, _ in messages):
                st.rerun()

        st.divider()
        st.markdown("#### Controles de ingesta incorporados")
        st.markdown("""
    - Hash SHA-256 para evitar duplicados.
    - Extracción por página para conservar trazabilidad.
    - Fragmentación con solapamiento.
    - Metadata de publicación y vigencia.
    - Estado documental y relación de reemplazo.
    - Fuente oficial y etiquetas.
    """)

    # -------------------- QA --------------------
    with tabs[3]:
        st.subheader("Evaluación QA")
        st.caption("Convierte preguntas conocidas en una batería repetible de pruebas.")

        qa_sub = st.tabs(["Casos de prueba", "Carga masiva", "Ejecutar evaluación"])

        with qa_sub[0]:
            with st.form("qa_add"):
                qq = st.text_area("Pregunta")
                ed = st.text_input("Documento esperado", placeholder="Ej.: Deudores.pdf")
                et = st.text_input("Texto esperado (opcional)", placeholder="Palabra o frase que debería aparecer")
                nt = st.text_area("Observaciones")
                save = st.form_submit_button("Guardar caso")
            if save and qq.strip():
                con = db()
                con.execute("""
                    INSERT INTO qa_cases(question,expected_document,expected_text,notes,created_at)
                    VALUES(?,?,?,?,?)
                """, (qq.strip(), ed.strip(), et.strip(), nt.strip(), datetime.now().isoformat(timespec="seconds")))
                con.commit()
                con.close()
                st.success("Caso QA agregado.")
                st.rerun()

            con = db()
            qdf = pd.read_sql_query("SELECT * FROM qa_cases ORDER BY id DESC", con)
            con.close()
            if not qdf.empty:
                st.dataframe(qdf[["id","question","expected_document","expected_text","notes"]], use_container_width=True, hide_index=True)

        with qa_sub[1]:
            template = pd.DataFrame([
                {
                    "question":"¿Qué contiene el archivo D10?",
                    "expected_document":"Deudores.pdf",
                    "expected_text":"D10",
                    "notes":"Caso de ejemplo"
                }
            ])
            st.download_button(
                "Descargar plantilla CSV",
                data=template.to_csv(index=False).encode("utf-8-sig"),
                file_name="plantilla_qa.csv",
                mime="text/csv"
            )
            qa_file = st.file_uploader("Cargar CSV QA", type=["csv"], key="qa_csv")
            if qa_file and st.button("Importar casos QA"):
                df = pd.read_csv(qa_file)
                required = {"question","expected_document","expected_text","notes"}
                if not required.issubset(df.columns):
                    st.error("El CSV debe incluir: question, expected_document, expected_text, notes")
                else:
                    con = db()
                    for _, r in df.iterrows():
                        con.execute("""
                            INSERT INTO qa_cases(question,expected_document,expected_text,notes,created_at)
                            VALUES(?,?,?,?,?)
                        """, (
                            str(r.get("question","")).strip(),
                            str(r.get("expected_document","")).strip(),
                            str(r.get("expected_text","")).strip(),
                            str(r.get("notes","")).strip(),
                            datetime.now().isoformat(timespec="seconds")
                        ))
                    con.commit()
                    con.close()
                    st.success(f"Se importaron {len(df)} casos.")
                    st.rerun()

        with qa_sub[2]:
            con = db()
            qdf = pd.read_sql_query("SELECT * FROM qa_cases ORDER BY id", con)
            con.close()
            if qdf.empty:
                st.info("Primero agrega casos QA.")
            elif st.button("Ejecutar batería completa", type="primary"):
                results = []
                con = db()
                for _, r in qdf.iterrows():
                    ev = retrieve(
                        r["question"], final_k, candidates, threshold, lexical_weight,
                        area_filter, as_of_str, active_only
                    )
                    expected = (r["expected_document"] or "").strip().lower()
                    found = any((e["filename"] or "").lower() == expected for e in ev) if expected else None
                    top = max([e["score"] for e in ev], default=0)
                    con.execute("""
                        INSERT INTO qa_runs(qa_case_id,created_at,found_expected_doc,top_score,evidence_count)
                        VALUES(?,?,?,?,?)
                    """, (
                        int(r["id"]), datetime.now().isoformat(timespec="seconds"),
                        None if found is None else int(found), top, len(ev)
                    ))
                    results.append({
                        "ID": r["id"],
                        "Pregunta": r["question"],
                        "Documento esperado": r["expected_document"],
                        "Encontrado": "Sí" if found else ("N/A" if found is None else "No"),
                        "Top score": round(top,3),
                        "Evidencias": len(ev)
                    })
                con.commit()
                con.close()
                rdf = pd.DataFrame(results)
                st.dataframe(rdf, use_container_width=True, hide_index=True)
                valid = rdf[rdf["Encontrado"].isin(["Sí","No"])]
                if len(valid):
                    acc = (valid["Encontrado"]=="Sí").mean()*100
                    st.metric("Recall documental QA", f"{acc:.1f}%")

    # -------------------- MONITOREO --------------------
    with tabs[4]:
        st.subheader("Monitoreo")
        con = db()
        dcount = pd.read_sql_query("SELECT COUNT(*) n FROM documents", con).iloc[0]["n"]
        ccount = pd.read_sql_query("SELECT COUNT(*) n FROM chunks", con).iloc[0]["n"]
        qlog = pd.read_sql_query("SELECT * FROM queries ORDER BY id DESC", con)
        qac = pd.read_sql_query("SELECT COUNT(*) n FROM qa_cases", con).iloc[0]["n"]
        con.close()

        total_q = len(qlog)
        no_ev = int(qlog["no_evidence"].sum()) if total_q else 0
        avg_lat = int(qlog["latency_ms"].mean()) if total_q else 0
        avg_top = float(qlog["top_score"].mean()) if total_q else 0

        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("Documentos", int(dcount))
        c2.metric("Fragmentos", int(ccount))
        c3.metric("Consultas", total_q)
        c4.metric("Sin evidencia", no_ev)
        c5.metric("Latencia media", f"{avg_lat} ms")

        st.caption(f"Score superior medio: {avg_top:.3f} · Casos QA: {int(qac)}")

        if total_q:
            st.markdown("### Últimas consultas")
            show = qlog[[
                "created_at","question","provider","evidence_count","top_score",
                "avg_score","no_evidence","latency_ms"
            ]].head(100)
            st.dataframe(show, use_container_width=True, hide_index=True)

            st.markdown("### Indicadores de calidad")
            no_ev_rate = (no_ev / total_q) * 100 if total_q else 0
            st.progress(min(no_ev_rate/100, 1.0), text=f"Consultas sin evidencia: {no_ev_rate:.1f}%")

    st.divider()
    st.caption(
        "Prototipo PyC Pro. Las respuestas deben validarse contra la normativa oficial vigente. "
        "El diseño prioriza evidencia, vigencia, trazabilidad y pruebas repetibles."
    )

if st.session_state.get("user_role") != "Administrador":
    st.divider()
    st.caption(
        "Las respuestas deben validarse contra la normativa oficial vigente. "
        "El agente prioriza evidencia documental y trazabilidad."
    )

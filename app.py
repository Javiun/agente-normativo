
from __future__ import annotations

import io
import re
import json
import sqlite3
import hashlib
from pathlib import Path
from datetime import date, datetime
from typing import List, Dict, Any

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
    initial_sidebar_state="collapsed",
)

# =========================
# ESTILO RESPONSIVE
# =========================
st.markdown("""
<style>
:root{
  --brand:#ef4856;
  --brand-dark:#b52835;
  --ink:#17233d;
  --text:#28364f;
  --muted:#6f7a8f;
  --line:#e6eaf0;
  --soft:#f7f9fc;
  --soft2:#eef3f8;
  --blue:#eaf4ff;
  --blue-text:#2466a8;
  --ok:#16804c;
  --warn:#ad6c00;
  --danger:#b42318;
  --shadow:0 10px 28px rgba(22,34,61,.07);
}

/* App */
html, body, [data-testid="stAppViewContainer"] {
  background:#ffffff !important;
  color:var(--text) !important;
  overflow-x:hidden !important;
}
.block-container{
  max-width:1180px !important;
  padding-top:1rem !important;
  padding-bottom:2.5rem !important;
}

/* Ocultar chrome de Streamlit */
#MainMenu{visibility:hidden !important;}
footer{visibility:hidden !important;}
header[data-testid="stHeader"]{
  height:0 !important;
  background:transparent !important;
}
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stAppDeployButton"]{
  display:none !important;
}

/* No usamos sidebar */
section[data-testid="stSidebar"],
[data-testid="collapsedControl"]{
  display:none !important;
}

/* Tipografía */
h1,h2,h3,h4{color:var(--ink) !important;}
p,label,span{font-size:inherit;}
[data-testid="stMarkdownContainer"] p{color:var(--text);}

/* Header */
.app-header{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap:18px;
  padding:22px 24px;
  border:1px solid var(--line);
  border-radius:18px;
  background:
    radial-gradient(circle at 92% 10%, rgba(239,72,86,.11), transparent 30%),
    linear-gradient(135deg,#fff,#fbfcff);
  box-shadow:var(--shadow);
  margin-bottom:14px;
}
.app-brand{
  min-width:0;
}
.app-kicker{
  display:flex;
  flex-wrap:wrap;
  gap:7px;
  margin-bottom:10px;
}
.chip{
  display:inline-flex;
  align-items:center;
  padding:5px 10px;
  border:1px solid #f5c6cb;
  border-radius:999px;
  background:#fff6f7;
  color:#a62634;
  font-weight:700;
  font-size:12px;
  line-height:1;
}
.app-title{
  margin:0;
  color:var(--ink);
  font-size:38px;
  line-height:1.08;
  font-weight:850;
  letter-spacing:-.7px;
}
.app-subtitle{
  margin-top:7px;
  color:var(--muted);
  font-size:15px;
  line-height:1.5;
  max-width:760px;
}
.logo-box{
  flex:0 0 auto;
  min-width:78px;
  height:54px;
  border-radius:14px;
  display:flex;
  align-items:center;
  justify-content:center;
  font-weight:850;
  font-size:22px;
  color:#294a88;
  border:1px solid #e3e8f0;
  background:#fff;
}

/* Top control panel */
.topbar{
  border:1px solid var(--line);
  border-radius:14px;
  background:var(--soft);
  padding:12px 14px;
  margin-bottom:14px;
}

/* Cards */
.card{
  border:1px solid var(--line);
  border-radius:14px;
  background:#fff;
  padding:16px;
  box-shadow:0 4px 18px rgba(22,34,61,.035);
}
.info-card{
  border:1px solid #cfe4f8;
  border-radius:12px;
  background:var(--blue);
  padding:12px 14px;
  color:var(--blue-text);
}
.evidence-card{
  border:1px solid #eceff4;
  border-left:4px solid var(--brand);
  border-radius:11px;
  background:#fffafa;
  padding:13px 14px;
  margin:9px 0;
}
.source-pill{
  display:inline-flex;
  align-items:center;
  padding:4px 8px;
  border-radius:999px;
  background:#f2f5f9;
  border:1px solid #e1e6ed;
  color:#4d5a70;
  font-size:12px;
  margin:2px 4px 2px 0;
}
.score-high{color:var(--ok);font-weight:750;}
.score-mid{color:var(--warn);font-weight:750;}
.score-low{color:var(--danger);font-weight:750;}

/* Inputs */
[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
.stTextInput input,
.stTextArea textarea{
  background:#fff !important;
  color:var(--ink) !important;
  border-color:#dfe5ed !important;
}
.stButton > button{
  border-radius:9px !important;
}
.stButton > button[kind="primary"]{
  background:var(--brand) !important;
  border-color:var(--brand) !important;
}

/* Tabs */
[data-baseweb="tab-list"]{
  gap:8px !important;
  overflow-x:auto !important;
  scrollbar-width:none !important;
}
[data-baseweb="tab-list"]::-webkit-scrollbar{display:none !important;}
[data-baseweb="tab"]{
  flex:0 0 auto !important;
  white-space:nowrap !important;
}

/* Chat input */
[data-testid="stChatInput"]{
  background:#fff !important;
}

/* Metric grid via HTML */
.metric-grid{
  display:grid;
  grid-template-columns:repeat(5,minmax(0,1fr));
  gap:10px;
  margin:8px 0 18px 0;
}
.metric-box{
  border:1px solid var(--line);
  background:#fff;
  border-radius:13px;
  padding:14px;
}
.metric-label{
  color:var(--muted);
  font-size:12px;
  margin-bottom:4px;
}
.metric-value{
  color:var(--ink);
  font-size:24px;
  font-weight:800;
}

/* Mobile */
@media (max-width: 760px){
  .block-container{
    padding:0.65rem 0.75rem 2rem 0.75rem !important;
    max-width:100% !important;
  }

  .app-header{
    padding:16px 15px;
    border-radius:14px;
    gap:10px;
  }
  .logo-box{display:none;}
  .app-title{
    font-size:27px;
    line-height:1.12;
  }
  .app-subtitle{
    font-size:13px;
    line-height:1.45;
  }
  .chip{
    font-size:11px;
    padding:5px 8px;
  }

  .topbar{
    padding:10px;
    border-radius:12px;
  }

  /* Evita columnas apretadas en móvil */
  [data-testid="stHorizontalBlock"]{
    flex-wrap:wrap !important;
    gap:.55rem !important;
  }
  [data-testid="column"]{
    min-width:100% !important;
    width:100% !important;
    flex:1 1 100% !important;
  }

  .metric-grid{
    grid-template-columns:repeat(2,minmax(0,1fr));
  }
  .metric-value{font-size:21px;}

  .card{padding:13px;}
  .info-card{padding:11px 12px;}

  [data-baseweb="tab"]{
    font-size:14px !important;
  }

  /* chat input con safe area iPhone */
  [data-testid="stChatInput"]{
    padding-bottom:calc(env(safe-area-inset-bottom) + 4px) !important;
  }
}

@media (max-width: 390px){
  .app-title{font-size:24px;}
  .metric-grid{grid-template-columns:1fr;}
}
</style>
""", unsafe_allow_html=True)

# =========================
# DB
# =========================
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
        evidence_count INTEGER
    );
    """)
    con.commit()
    con.close()

init_db()

# =========================
# HELPERS
# =========================
def clean_text(s: str) -> str:
    s = (s or "").replace("\x00"," ")
    s = re.sub(r"[ \t]+"," ",s)
    s = re.sub(r"\n{3,}","\n\n",s)
    return s.strip()

def chunk_page(text: str, max_chars=1300, overlap=180):
    text = clean_text(text)
    if not text:
        return []
    parts = re.split(r"\n\s*\n|(?<=[\.\:\;])\s+(?=[A-ZÁÉÍÓÚÑ0-9])", text)
    out, buf = [], ""
    for p in parts:
        p = clean_text(p)
        if not p:
            continue
        if len(buf)+len(p)+1 <= max_chars:
            buf = (buf+" "+p).strip()
        else:
            if buf:
                out.append(buf)
            tail = buf[-overlap:] if buf else ""
            buf = (tail+" "+p).strip()
    if buf:
        out.append(buf)
    return out

def parse_pdf(data: bytes):
    reader = PdfReader(io.BytesIO(data))
    pages = []
    for i, page in enumerate(reader.pages,1):
        try:
            txt = clean_text(page.extract_text() or "")
        except Exception:
            txt = ""
        pages.append((i,txt))
    return pages

def add_document(file, meta):
    raw = file.getvalue()
    digest = hashlib.sha256(raw).hexdigest()
    con = db()
    cur = con.cursor()
    old = cur.execute("SELECT id,filename FROM documents WHERE sha256=?",(digest,)).fetchone()
    if old:
        con.close()
        return False, f"Ya existe como {old[1]}."

    pages = parse_pdf(raw)
    chars = sum(len(t) for _,t in pages)
    (UPLOAD_DIR/file.name).write_bytes(raw)

    cur.execute("""
      INSERT INTO documents(filename,sha256,area,tipo,version,fecha_publicacion,
      vigencia_desde,vigencia_hasta,estado,fuente_url,etiquetas,reemplaza_a,pages,chars,created_at)
      VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """,(
        file.name,digest,meta["area"],meta["tipo"],meta["version"],meta["fecha_publicacion"],
        meta["vigencia_desde"],meta["vigencia_hasta"],meta["estado"],meta["fuente_url"],
        meta["etiquetas"],meta["reemplaza_a"],len(pages),chars,
        datetime.now().isoformat(timespec="seconds")
    ))
    doc_id = cur.lastrowid
    for pno, txt in pages:
        for n,ch in enumerate(chunk_page(txt)):
            cur.execute(
                "INSERT INTO chunks(document_id,page,chunk_no,text) VALUES(?,?,?,?)",
                (doc_id,pno,n,ch)
            )
    con.commit()
    con.close()
    return True, f"{file.name}: {len(pages)} páginas indexadas."

def get_documents():
    con = db()
    df = pd.read_sql_query("SELECT * FROM documents ORDER BY created_at DESC",con)
    con.close()
    return df

def get_corpus(active_only=True, area="Todas", as_of=None):
    con = db()
    q = """
    SELECT c.id chunk_id,c.page,c.chunk_no,c.text,
           d.id document_id,d.filename,d.area,d.tipo,d.version,
           d.vigencia_desde,d.vigencia_hasta,d.estado
    FROM chunks c JOIN documents d ON d.id=c.document_id
    WHERE 1=1
    """
    p=[]
    if active_only:
        q += " AND d.estado='Vigente'"
    if area and area!="Todas":
        q += " AND d.area=?"
        p.append(area)
    if as_of:
        q += " AND (d.vigencia_desde='' OR d.vigencia_desde IS NULL OR d.vigencia_desde<=?)"
        q += " AND (d.vigencia_hasta='' OR d.vigencia_hasta IS NULL OR d.vigencia_hasta>=?)"
        p += [as_of,as_of]
    df = pd.read_sql_query(q,con,params=p)
    con.close()
    return df

STOP=set("""de la el los las un una unos unas y o u en por para con sin sobre entre desde hasta
que qué como cómo cual cuál cuales cuáles es son fue eran será se su sus al del lo más menos muy""".split())

def tokens(s):
    return [x for x in re.findall(r"[a-záéíóúñ0-9]{2,}",(s or "").lower()) if x not in STOP]

def literal_score(q,t):
    q=set(tokens(q)); t=set(tokens(t))
    if not q: return 0.0
    return len(q&t)/max(1,len(q))

def retrieve(question, final_k=6, candidates=25, threshold=.10, lexical_weight=.30,
             area="Todas", as_of=None, active_only=True):
    corpus=get_corpus(active_only,area,as_of)
    if corpus.empty:
        return []
    texts=corpus["text"].fillna("").tolist()
    try:
        v=TfidfVectorizer(lowercase=True,strip_accents="unicode",ngram_range=(1,2),sublinear_tf=True,max_features=50000)
        m=v.fit_transform(texts+[question])
        sem=cosine_similarity(m[-1],m[:-1]).flatten()
    except Exception:
        sem=np.zeros(len(texts))
    lit=np.array([literal_score(question,t) for t in texts])
    score=(1-lexical_weight)*sem+lexical_weight*lit
    order=np.argsort(score)[::-1][:max(candidates,final_k)]
    out=[]
    for i in order:
        if float(score[i])<threshold: continue
        r=corpus.iloc[int(i)].to_dict()
        r["semantic_score"]=float(sem[i]); r["lexical_score"]=float(lit[i]); r["score"]=float(score[i])
        out.append(r)
        if len(out)>=final_k: break
    return out

def source_label(e):
    return f"{e['filename']} · pág. {int(e['page'])}"

def local_answer(evidence):
    if not evidence:
        return "No encontré evidencia suficiente en la base documental cargada."
    lines=["Encontré evidencia relevante en la base documental:"]
    for i,e in enumerate(evidence[:3],1):
        sn=clean_text(e["text"])
        if len(sn)>520: sn=sn[:520].rstrip()+"…"
        lines += [f"\n**{i}. {source_label(e)}**",sn]
    return "\n".join(lines)

def gemini_answer(question,evidence,api_key):
    ctx="\n\n".join(
        f"[FUENTE {i}: {source_label(e)} | score={e['score']:.3f}]\n{e['text']}"
        for i,e in enumerate(evidence,1)
    )
    prompt=f"""
Eres un asistente normativo bancario. Responde solo con la evidencia entregada.
Si no es suficiente, responde: "No encontré evidencia suficiente en la base documental cargada."
Cita cada afirmación relevante con (Documento.pdf, pág. X).
Si hay contradicciones, indícalas y no las resuelvas por tu cuenta.
No inventes artículos, fechas, obligaciones ni referencias.

PREGUNTA:
{question}

EVIDENCIA:
{ctx}
"""
    try:
        from google import genai
        client=genai.Client(api_key=api_key)
        r=client.models.generate_content(model="gemini-2.0-flash",contents=prompt)
        return r.text
    except Exception as e:
        return f"No fue posible consultar Gemini: {e}"

def log_query(question,provider,evidence,latency_ms,filters):
    con=db()
    top=max([e["score"] for e in evidence],default=0)
    avg=sum([e["score"] for e in evidence])/len(evidence) if evidence else 0
    con.execute("""
      INSERT INTO queries(created_at,question,provider,evidence_count,top_score,avg_score,no_evidence,latency_ms,filters_json)
      VALUES(?,?,?,?,?,?,?,?,?)
    """,(
        datetime.now().isoformat(timespec="seconds"),question,provider,len(evidence),
        top,avg,0 if evidence else 1,latency_ms,json.dumps(filters,ensure_ascii=False)
    ))
    con.commit(); con.close()

def delete_doc(doc_id):
    con=db()
    con.execute("DELETE FROM chunks WHERE document_id=?",(doc_id,))
    con.execute("DELETE FROM documents WHERE id=?",(doc_id,))
    con.commit(); con.close()

def score_class(s):
    return "score-high" if s>=.55 else ("score-mid" if s>=.25 else "score-low")

# =========================
# ESTADO
# =========================
if "role" not in st.session_state:
    st.session_state["role"]="Usuario"
if "chat" not in st.session_state:
    st.session_state["chat"]=[]

# =========================
# HEADER
# =========================
st.markdown("""
<div class="app-header">
  <div class="app-brand">
    <div class="app-kicker">
      <span class="chip">RAG auditable</span>
      <span class="chip">Control de vigencia</span>
      <span class="chip">QA incorporado</span>
    </div>
    <div class="app-title">Agente Normativo PyC Pro</div>
    <div class="app-subtitle">
      Consulta normativa con trazabilidad por documento y página, control de versiones,
      recuperación híbrida y monitoreo de calidad.
    </div>
  </div>
  <div class="logo-box">PyC</div>
</div>
""",unsafe_allow_html=True)

# =========================
# BARRA SUPERIOR
# =========================
st.markdown('<div class="topbar">',unsafe_allow_html=True)
c1,c2 = st.columns([1,2.4])
with c1:
    role = st.selectbox(
        "Perfil de prueba",
        ["Usuario","Administrador"],
        index=0 if st.session_state["role"]=="Usuario" else 1,
        help="Demo. En producción debe reemplazarse por autenticación real."
    )
    st.session_state["role"]=role
with c2:
    if role=="Usuario":
        st.markdown(
            '<div class="info-card">Modo usuario: consulta simplificada, solo documentos vigentes y evidencia estricta.</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="info-card">Modo administrador: acceso a configuración, ingesta, QA y monitoreo.</div>',
            unsafe_allow_html=True
        )
st.markdown('</div>',unsafe_allow_html=True)

docs_df=get_documents()
areas=["Todas"]+sorted([x for x in docs_df["area"].dropna().unique().tolist() if x]) if not docs_df.empty else ["Todas"]

# Defaults
final_k=6; candidates=25; threshold=.10; lexical_weight=.30
active_only=True; area_filter="Todas"; as_of_str=None
provider="Modo extractivo local"; api_key=""; strict_mode=True

# Admin settings are in the page, never in a drawer/sidebar
if role=="Administrador":
    with st.expander("⚙️ Configuración avanzada", expanded=False):
        s1,s2 = st.columns(2)
        with s1:
            st.markdown("#### Recuperación")
            final_k=st.slider("Fragmentos finales",3,12,6)
            candidates=st.slider("Candidatos iniciales",5,60,25)
            threshold=st.slider("Umbral mínimo",0.00,1.00,.10,.01)
            lexical_weight=st.slider("Peso búsqueda literal",0.0,1.0,.30,.05)
        with s2:
            st.markdown("#### Alcance")
            area_filter=st.selectbox("Área",areas,key="admin_area")
            active_only=st.toggle("Solo documentos vigentes",True)
            use_asof=st.toggle("Consultar vigencia a una fecha",False)
            asof=st.date_input("Fecha de consulta",date.today(),disabled=not use_asof)
            as_of_str=str(asof) if use_asof else None

        g1,g2 = st.columns(2)
        with g1:
            provider=st.selectbox("Proveedor",["Modo extractivo local","Gemini"])
        with g2:
            api_key=st.text_input("API key Gemini",type="password",disabled=provider!="Gemini")
        strict_mode=st.toggle("Modo evidencia estricta",True)

# =========================
# NAVEGACIÓN
# =========================
if role=="Administrador":
    nav = st.tabs(["💬 Consulta","📚 Base documental","⬆️ Ingesta","🧪 QA","📊 Monitoreo"])
else:
    nav = st.tabs(["💬 Consulta","📚 Fuentes"])

# =========================
# CONSULTA
# =========================
with nav[0]:
    st.subheader("Consulta normativa")
    st.caption("Cada respuesta debe poder revisarse desde su evidencia documental.")

    if role=="Usuario":
        a1,a2 = st.columns([1.1,2.4])
        with a1:
            area_filter=st.selectbox("Área normativa",areas,key="user_area")
        with a2:
            st.markdown(
                '<div class="info-card">Consulta solo documentos vigentes. Las fuentes y páginas aparecen junto a la respuesta.</div>',
                unsafe_allow_html=True
            )

    for msg in st.session_state["chat"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("evidence"):
                with st.expander("Ver evidencia utilizada"):
                    for e in msg["evidence"]:
                        cls=score_class(e["score"])
                        st.markdown(
                            f"""<div class="evidence-card">
                            <strong>{source_label(e)}</strong><br>
                            <span class="{cls}">Score {e['score']:.3f}</span>
                            <span style="color:#7b8496;font-size:12px">
                            · semántico {e['semantic_score']:.3f} · literal {e['lexical_score']:.3f}
                            </span><br><br>
                            {e['text'][:1500]}
                            </div>""",
                            unsafe_allow_html=True
                        )

    q=st.chat_input("Escribe una consulta normativa…")
    if q:
        import time
        t0=time.perf_counter()
        ev=retrieve(q,final_k,candidates,threshold,lexical_weight,area_filter,as_of_str,active_only)
        if strict_mode and not ev:
            ans="No encontré evidencia suficiente en la base documental cargada."
        elif provider=="Gemini" and api_key and ev:
            ans=gemini_answer(q,ev,api_key)
        else:
            ans=local_answer(ev)
        latency=int((time.perf_counter()-t0)*1000)
        log_query(q,provider,ev,latency,{
            "area":area_filter,"as_of":as_of_str,"active_only":active_only,
            "threshold":threshold,"lexical_weight":lexical_weight
        })
        st.session_state["chat"].append({"role":"user","content":q})
        st.session_state["chat"].append({"role":"assistant","content":ans,"evidence":ev})
        st.rerun()

    if st.button("Limpiar conversación"):
        st.session_state["chat"]=[]
        st.rerun()

# =========================
# BASE / FUENTES
# =========================
with nav[1]:
    if role=="Usuario":
        st.subheader("Fuentes disponibles")
        st.caption("Documentos actualmente incorporados a la base normativa.")
    else:
        st.subheader("Base documental")
        st.caption("Inventario, vigencia, versión y estado de los documentos indexados.")

    ddf=get_documents()
    if ddf.empty:
        st.info("Aún no hay documentos cargados.")
    else:
        if role=="Usuario":
            show=ddf[["filename","area","version","vigencia_desde","estado","pages"]].rename(columns={
                "filename":"Documento","area":"Área","version":"Versión",
                "vigencia_desde":"Vigente desde","estado":"Estado","pages":"Páginas"
            })
        else:
            show=ddf[[
                "filename","area","tipo","version","fecha_publicacion","vigencia_desde",
                "vigencia_hasta","estado","pages","chars","reemplaza_a"
            ]].rename(columns={
                "filename":"Documento","area":"Área","tipo":"Tipo","version":"Versión",
                "fecha_publicacion":"Publicación","vigencia_desde":"Vigente desde",
                "vigencia_hasta":"Vigente hasta","estado":"Estado","pages":"Páginas",
                "chars":"Caracteres","reemplaza_a":"Reemplaza a"
            })
        st.dataframe(show,use_container_width=True,hide_index=True)

        if role=="Administrador":
            st.markdown("### Explorador de recuperación")
            testq=st.text_input("Pregunta de prueba",value="¿Qué contiene el archivo D10?",key="testq")
            if st.button("Probar recuperación",type="primary"):
                ev=retrieve(testq,final_k,candidates,threshold,lexical_weight,area_filter,as_of_str,active_only)
                if not ev:
                    st.warning("No se encontraron fragmentos por sobre el umbral.")
                else:
                    for i,e in enumerate(ev,1):
                        st.markdown(
                            f"""<div class="evidence-card">
                            <strong>{i}. {source_label(e)}</strong><br>
                            Área: {e['area']} · Versión: {e['version']} · Score {e['score']:.3f}<br><br>
                            {e['text'][:1600]}
                            </div>""",
                            unsafe_allow_html=True
                        )

            st.markdown("### Gestión")
            opts={f"{r['filename']} · {r['version']} · ID {r['id']}":int(r["id"]) for _,r in ddf.iterrows()}
            selected=st.selectbox("Documento",list(opts.keys()))
            if st.button("Eliminar documento seleccionado"):
                delete_doc(opts[selected])
                st.success("Documento eliminado.")
                st.rerun()

# =========================
# ADMIN TABS
# =========================
if role=="Administrador":

    with nav[2]:
        st.subheader("Ingesta controlada")
        st.caption("Carga PDF con metadata de versión, vigencia, fuente y reemplazo.")

        files=st.file_uploader("Selecciona uno o más PDF",type=["pdf"],accept_multiple_files=True)

        c1,c2 = st.columns(2)
        with c1:
            area=st.text_input("Área",placeholder="Ej.: Contables")
            tipo=st.selectbox("Tipo documental",["Norma","Circular","Capítulo","Manual","Anexo","Otro"])
            version=st.text_input("Versión",value=str(date.today()))
            fuente_url=st.text_input("URL oficial / fuente")
        with c2:
            pub=st.date_input("Fecha de publicación",date.today())
            vig_desde=st.date_input("Vigencia desde",date.today())
            has_end=st.checkbox("Tiene fin de vigencia",False)
            vig_hasta=st.date_input("Vigencia hasta",date.today(),disabled=not has_end)
            estado=st.selectbox("Estado",["Vigente","Borrador","No vigente"])

        etiquetas=st.text_input("Etiquetas",placeholder="RCD, deuda, CMF")
        reemplaza_a=st.text_input("Reemplaza a",placeholder="Nombre o versión anterior")

        if st.button("Incorporar a la base",type="primary",disabled=not files):
            for f in files or []:
                ok,msg=add_document(f,{
                    "area":area or "Sin clasificar","tipo":tipo,"version":version,
                    "fecha_publicacion":str(pub),"vigencia_desde":str(vig_desde),
                    "vigencia_hasta":str(vig_hasta) if has_end else "",
                    "estado":estado,"fuente_url":fuente_url,"etiquetas":etiquetas,
                    "reemplaza_a":reemplaza_a
                })
                st.success(msg) if ok else st.warning(msg)
            st.rerun()

    with nav[3]:
        st.subheader("Evaluación QA")
        st.caption("Batería repetible de preguntas conocidas para medir recuperación documental.")

        qa1,qa2 = st.tabs(["Casos","Ejecutar"])
        with qa1:
            with st.form("qaform"):
                qq=st.text_area("Pregunta")
                ed=st.text_input("Documento esperado")
                et=st.text_input("Texto esperado (opcional)")
                nt=st.text_area("Observaciones")
                save=st.form_submit_button("Guardar caso")
            if save and qq.strip():
                con=db()
                con.execute("""
                INSERT INTO qa_cases(question,expected_document,expected_text,notes,created_at)
                VALUES(?,?,?,?,?)
                """,(qq.strip(),ed.strip(),et.strip(),nt.strip(),datetime.now().isoformat(timespec="seconds")))
                con.commit(); con.close(); st.rerun()

            con=db()
            qdf=pd.read_sql_query("SELECT * FROM qa_cases ORDER BY id DESC",con)
            con.close()
            if not qdf.empty:
                st.dataframe(qdf[["id","question","expected_document","expected_text","notes"]],
                             use_container_width=True,hide_index=True)

        with qa2:
            con=db()
            qdf=pd.read_sql_query("SELECT * FROM qa_cases ORDER BY id",con)
            con.close()
            if qdf.empty:
                st.info("Primero agrega casos QA.")
            elif st.button("Ejecutar batería completa",type="primary"):
                rows=[]
                con=db()
                for _,r in qdf.iterrows():
                    ev=retrieve(r["question"],final_k,candidates,threshold,lexical_weight,area_filter,as_of_str,active_only)
                    expected=(r["expected_document"] or "").strip().lower()
                    found=any((e["filename"] or "").lower()==expected for e in ev) if expected else None
                    top=max([e["score"] for e in ev],default=0)
                    con.execute("""
                    INSERT INTO qa_runs(qa_case_id,created_at,found_expected_doc,top_score,evidence_count)
                    VALUES(?,?,?,?,?)
                    """,(int(r["id"]),datetime.now().isoformat(timespec="seconds"),
                         None if found is None else int(found),top,len(ev)))
                    rows.append({
                        "ID":r["id"],"Pregunta":r["question"],"Documento esperado":r["expected_document"],
                        "Encontrado":"Sí" if found else ("N/A" if found is None else "No"),
                        "Top score":round(top,3),"Evidencias":len(ev)
                    })
                con.commit(); con.close()
                rdf=pd.DataFrame(rows)
                st.dataframe(rdf,use_container_width=True,hide_index=True)
                valid=rdf[rdf["Encontrado"].isin(["Sí","No"])]
                if len(valid):
                    st.metric("Recall documental QA",f"{(valid['Encontrado']=='Sí').mean()*100:.1f}%")

    with nav[4]:
        st.subheader("Monitoreo")
        con=db()
        dcount=pd.read_sql_query("SELECT COUNT(*) n FROM documents",con).iloc[0]["n"]
        ccount=pd.read_sql_query("SELECT COUNT(*) n FROM chunks",con).iloc[0]["n"]
        qlog=pd.read_sql_query("SELECT * FROM queries ORDER BY id DESC",con)
        qac=pd.read_sql_query("SELECT COUNT(*) n FROM qa_cases",con).iloc[0]["n"]
        con.close()

        total_q=len(qlog)
        no_ev=int(qlog["no_evidence"].sum()) if total_q else 0
        avg_lat=int(qlog["latency_ms"].mean()) if total_q else 0
        avg_top=float(qlog["top_score"].mean()) if total_q else 0

        st.markdown(f"""
        <div class="metric-grid">
          <div class="metric-box"><div class="metric-label">Documentos</div><div class="metric-value">{int(dcount)}</div></div>
          <div class="metric-box"><div class="metric-label">Fragmentos</div><div class="metric-value">{int(ccount)}</div></div>
          <div class="metric-box"><div class="metric-label">Consultas</div><div class="metric-value">{total_q}</div></div>
          <div class="metric-box"><div class="metric-label">Sin evidencia</div><div class="metric-value">{no_ev}</div></div>
          <div class="metric-box"><div class="metric-label">Latencia media</div><div class="metric-value">{avg_lat} ms</div></div>
        </div>
        """,unsafe_allow_html=True)

        st.caption(f"Score superior medio: {avg_top:.3f} · Casos QA: {int(qac)}")
        if total_q:
            st.dataframe(qlog[[
                "created_at","question","provider","evidence_count","top_score",
                "avg_score","no_evidence","latency_ms"
            ]].head(100),use_container_width=True,hide_index=True)

st.divider()
st.caption(
    "Las respuestas deben validarse contra la normativa oficial vigente. "
    "El sistema prioriza evidencia, trazabilidad y control de vigencia."
)

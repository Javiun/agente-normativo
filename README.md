# Agente Normativo PyC Pro

Versión competitiva del prototipo de agente normativo.

## Diferencias respecto de una copia básica

Esta versión agrega capacidades pensadas para un contexto normativo/bancario:

- Trazabilidad por **documento + página**.
- Ingesta PDF con extracción por página.
- Búsqueda híbrida:
  - similitud TF-IDF;
  - coincidencia literal;
  - ponderación configurable.
- Modo de **evidencia estricta**.
- Control de:
  - versión;
  - fecha de publicación;
  - vigencia desde/hasta;
  - estado del documento;
  - documento reemplazado;
  - fuente oficial;
  - etiquetas.
- Detección de documentos duplicados por SHA-256.
- Explorador de recuperación sin IA generativa.
- QA incorporado con casos repetibles.
- Importación de casos QA por CSV.
- Métrica de recall documental.
- Monitoreo de consultas, score y latencia.
- Registro persistente local en SQLite.
- Gemini opcional.
- Funcionamiento local sin Gemini.

## Ejecutar en Windows

### Opción 1
Doble clic en:

`ejecutar_windows.bat`

### Opción 2

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Primer uso recomendado

1. Ir a **Ingesta**.
2. Cargar uno o más PDF reales.
3. Completar área, tipo, versión y vigencia.
4. Ir a **Base documental** y probar recuperación.
5. Ajustar:
   - fragmentos finales;
   - candidatos;
   - umbral;
   - peso literal.
6. Ir a **Evaluación QA** y crear 20–30 preguntas conocidas.
7. Medir recall documental.
8. Recién después habilitar Gemini para generación.

## Arquitectura actual

PDF
→ extracción por página
→ fragmentación
→ SQLite
→ búsqueda híbrida
→ selección de evidencia
→ respuesta extractiva o Gemini
→ citas documento/página
→ monitoreo/QA

## Evolución recomendada para producción

Para ambiente productivo empresarial:

- PostgreSQL + pgvector o motor vectorial dedicado.
- embeddings multilingües;
- reranker;
- OCR controlado para PDF escaneado;
- SSO Microsoft Entra ID / Azure AD;
- RBAC;
- cifrado de secretos;
- auditoría por usuario;
- almacenamiento de documentos en SharePoint / Blob Storage;
- workflow de aprobación;
- ingestión incremental;
- detección de normas derogadas;
- comparación entre versiones;
- respaldo y observabilidad;
- pruebas de seguridad y pentesting.

# V5 — Rediseño responsive completo

Esta versión reemplaza el enfoque anterior de sidebar por una interfaz realmente responsive.

## Cambio principal

**Se eliminó por completo el sidebar de Streamlit.**

En iPhone el problema era que el drawer lateral de Streamlit y algunos controles BaseWeb producían:
- recortes;
- contenido desplazado;
- controles fuera del panel;
- transparencia/overlay;
- problemas de ancho en Safari iOS.

V5 mueve toda la navegación y configuración al contenido principal.

## Usuario
- Header compacto y responsive.
- Selector de perfil arriba.
- Solo dos tabs:
  - Consulta
  - Fuentes
- Filtro Área dentro de Consulta.
- Sin controles técnicos.
- Sin sidebar.
- Chat adaptado a safe-area de iPhone.

## Administrador
- Tabs:
  - Consulta
  - Base documental
  - Ingesta
  - QA
  - Monitoreo
- Configuración avanzada dentro de un `expander`.
- Ninguna dependencia del sidebar.

## Responsive
- Escritorio: ancho máximo 1180 px.
- Tablet: layout flexible.
- Móvil: columnas apiladas automáticamente.
- Métricas 2 por fila y 1 por fila en pantallas muy angostas.
- Tabs horizontales con scroll.
- Hero simplificado.
- Toolbar/Fork/GitHub ocultos por CSS cuando Streamlit permite hacerlo.

## Publicación
Reemplaza:
- `app.py`
- `.streamlit/config.toml`

Luego commit + push y reinicia la app en Streamlit Cloud.

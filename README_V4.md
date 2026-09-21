# V4 — corrección móvil

Correcciones específicas para el problema visto en iPhone:

- El sidebar ahora fuerza un ancho real de 86–88% de la pantalla.
- Los controles internos no pueden desbordarse hacia el contenido principal.
- Selectbox, inputs, sliders, toggles y botones respetan 100% del ancho disponible.
- Se bloquea el overflow horizontal de la app.
- El botón de cerrar sidebar mantiene tamaño compacto.
- En perfil Usuario, el filtro Área salió del sidebar y pasó a la pantalla principal.
- El sidebar de Usuario queda casi vacío: solo perfil y acciones básicas.
- Administrador conserva la configuración avanzada en el menú lateral.

Para publicar:
1. Reemplazar `app.py` en GitHub.
2. Mantener `.streamlit/config.toml`.
3. Commit + push.
4. En Streamlit Cloud usar **Reboot app** si el cambio no aparece inmediatamente.
5. En iPhone cerrar y volver a abrir la pestaña o recargar sin caché.

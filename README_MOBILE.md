## Ajuste V2 móvil / Streamlit Cloud

Esta versión corrige específicamente:

- Oculta `Fork`, GitHub, menú principal y toolbar de Streamlit cuando el frontend lo permite.
- Fuerza tema claro desde `.streamlit/config.toml`, evitando que el modo oscuro/sistema del iPhone vuelva ilegible el sidebar.
- Sidebar con fondo opaco y texto oscuro.
- Ancho del sidebar adaptado a móvil.
- Tabs horizontales desplazables.
- Mejor padding en iPhone.
- Inputs claros y legibles aunque el dispositivo esté en modo oscuro.
- Compatibilidad con `safe-area-inset-bottom` para el cuadro de chat.

### Para actualizar la versión publicada

Reemplaza en GitHub:

- `app.py`
- agrega la carpeta `.streamlit/config.toml`

Luego haz commit/push. Streamlit Community Cloud redeployará automáticamente.

Si el despliegue no se actualiza de inmediato:
1. Abre el menú de la app en Streamlit Cloud.
2. Selecciona **Reboot app**.
3. Recarga Safari.

Nota: algunos elementos de la barra superior pertenecen al shell de Streamlit Community Cloud y pueden cambiar de selector entre versiones. Esta V2 oculta los selectores más habituales sin romper la aplicación.

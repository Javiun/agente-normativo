# V3 — perfiles y experiencia simplificada

Esta versión agrega dos modos:

## Usuario
- Solo ve **Consulta** y **Fuentes**.
- No ve sliders ni parámetros técnicos.
- Usa valores seguros por defecto:
  - 6 fragmentos finales
  - 25 candidatos
  - umbral 0.10
  - peso literal 0.30
  - solo documentos vigentes
  - evidencia estricta
- Puede filtrar por área.
- No puede:
  - cargar/eliminar documentos
  - ejecutar QA
  - ver monitoreo
  - modificar configuración de recuperación

## Administrador
- Ve todas las pestañas.
- Tiene un interruptor **Mostrar parámetros**.
- La configuración avanzada queda organizada en:
  - Recuperación
  - Filtros documentales
  - Generación
- Puede gestionar documentos, QA y monitoreo.

## Importante
El selector Usuario/Administrador es solo para la demo.
En producción debe reemplazarse por autenticación real, idealmente:
- Microsoft Entra ID / Azure AD
- o Supabase Auth
- con roles persistentes.

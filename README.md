# Evaluación crediticia Grupo 1 UGR

Aplicación Streamlit de la fase 6 del trabajo de Ingeniería de Software. Reutiliza el Pipeline y los umbrales auditados del notebook. Tiene dos apartados: Evaluar solicitud y Resultados del modelo.

## Ejecutar en la computadora

Usar Python 3.12. Abrir una terminal dentro de esta carpeta:

```bash
python -m venv .venv
```

En Windows PowerShell, activar con `.venv\Scripts\Activate.ps1`. En Linux/macOS, con `source .venv/bin/activate`.

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

La terminal muestra la dirección local para abrir en el navegador. La aplicación carga los archivos de `artifacts/`; no necesita subir el CSV ni ejecutar el entrenamiento.

## Publicar en Streamlit Community Cloud

1. Crear un repositorio de GitHub exclusivo para este trabajo, por ejemplo `ugr-riesgo-crediticio`.
2. Subir el contenido extraído de esta carpeta, con `app.py` en la raíz. Incluir `core.py`, `requirements.txt`, `.streamlit/` y la carpeta `artifacts/` completa. No subir solamente el ZIP.
3. En https://share.streamlit.io/ crear una aplicación y autorizar el acceso a ese repositorio.
4. Seleccionar la rama correspondiente, `app.py` como archivo de entrada y Python 3.12 en las opciones avanzadas.
5. Desplegar, comprobar el acceso como visitante y copiar el enlace en la fase 6 del notebook.
6. Ejecutar los casos de aceptación sobre la URL desplegada, tomar capturas de ambos apartados y reemplazar el estado pendiente del documento de fase 6 por las evidencias reales.

El paquete está preparado para publicación; no incluye una URL ya desplegada ni credenciales. No se modificó el repositorio Strelia.

## Artefactos y reproducibilidad

- `modelo_riesgo.joblib`: Pipeline auditado con nueve predictores, incluido el preprocesamiento.
- `modelo_config.json`: umbrales, esquema y versión originales.
- `resultados.json`: métricas históricas, rangos de referencia, versiones del entrenamiento y SHA-256 del CSV.
- `integridad.json`: hashes de los artefactos y gráficos. La app falla de forma explícita si no coinciden.

El modelo conserva los árboles entrenados. Se usa un solo hilo de inferencia por visitante para evitar sobrecarga; esto no cambia las reglas ni los parámetros aprendidos. El ingreso de ocho campos deriva automáticamente monto/ingreso anual.

Las etiquetas y su horizonte temporal no tienen documentación primaria suficiente para un uso operativo. La moneda de entrenamiento no está documentada: no interpretar los montos como ARS. Los rangos son los del dataset limpio, con la proporción recalculada. El aviso fuera de rango no prueba que un valor sea inválido ni garantiza representatividad dentro del rango. La decisión final corresponde al operador.

## Pruebas

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
```

Se comprueban validaciones, datos faltantes, fronteras de umbrales, integridad, equivalencia con el Pipeline, navegación, consulta válida y bloqueo de una consulta inválida después de una válida. `PRUEBAS.json` registra diez consultas de AppTest local; no certifica latencia de Internet ni el despliegue.

## Actualizar el modelo

Repetir la evaluación del notebook sin ajustar decisiones con la prueba ya observada; aceptar la versión únicamente si cumple los criterios documentados. Exportar el modelo, configuración, resultados y gráficos como un único paquete coherente. Regenerar los hashes, ejecutar las pruebas y desplegar. Conservar la versión anterior completa para volver atrás si falla una comprobación. Nunca cargar archivos joblib proporcionados por visitantes.

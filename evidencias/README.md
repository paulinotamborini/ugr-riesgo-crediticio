# Evidencias de publicación — Fase 6

Fecha: 29/10/2026, America/Buenos_Aires.

Aplicación: https://ugr-riesgo-crediticio.streamlit.app/

Código y artefactos publicados en el commit `6fd86bb` de `paulinotamborini/ugr-riesgo-crediticio`. El modelo original no se modificó ni se reentrenó. Los seis artefactos conservaron los hashes del paquete recuperado.

## Capturas del navegador

| Archivo | Evidencia |
|---|---|
| [01_evaluar_resultado.png](01_evaluar_resultado.png) | Consulta con monto 7.000, ingreso anual 55.000; probabilidad 9,6 %, nivel Bajo y proporción 12,7 %. |
| [02_formulario.png](02_formulario.png) | Encabezado y formulario de solicitud publicado. |
| [03_validacion.png](03_validacion.png) | Rechazo del ingreso anual cero tras una consulta válida. |
| [04_resultados_modelo.png](04_resultados_modelo.png) | AP 0,7761; Brier 0,0935; captura al priorizar 20 %: 64,5 %. |
| [05_niveles_matriz.png](05_niveles_matriz.png) | Niveles y matriz de confusión publicados. |
| [06_importancia_global.png](06_importancia_global.png) | Gráfico de importancia y advertencias de alcance. |
| [07_fuera_rango.png](07_fuera_rango.png) | Edad 100: entrada válida con advertencia por superar el máximo histórico de 94. |

Las capturas conservan el tamaño de la ventana utilizada; los gráficos completos también están en `artifacts/`. Las imágenes se cargaron con sus dimensiones originales verificadas en el navegador.

## Verificación

- Suite original: `python -m pytest tests -q`, **21 passed in 3.86s**, Python 3.12.10 sobre Windows.
- Diez consultas públicas: probabilidades y niveles coincidentes con el Pipeline local, incluidos los tres niveles de riesgo. Entradas y tiempos en [consultas_publicas.json](consultas_publicas.json).
- Consulta inválida: ingreso anual cero bloqueado; al finalizar la actualización no quedó la métrica de la consulta anterior.
- Advertencia histórica: edad 100 aceptada con aviso de representatividad.
- [acceso_sin_sesion.json](acceso_sin_sesion.json): cliente HTTP nuevo sin credenciales ni cookies iniciales; termina con HTTP 200 en la URL pública. El servicio emite su sesión de visitante. Se omiten parámetros transitorios de redirección.
- [despliegue_streamlit.txt](despliegue_streamlit.txt): registro de Cloud, Python 3.12.16, instalación y arranque. El servicio ajustó PyArrow de 26.0.0 a 24.0.0 automáticamente.
- [resultados_publicos.txt](resultados_publicos.txt) y [validacion_publica.txt](validacion_publica.txt): estado de la interfaz observado.

## Pendientes de aceptación

La medición pública observada incluye control remoto y espera de automatización: mínimo 0,811 s, máximo 2,399 s, tres consultas por encima de 2 s. No equivale a latencia pura de red ni certifica el límite de 2 s. El servidor informó entre 0,037 y 0,059 s de inferencia en las nueve consultas con ese dato registrado. Falta una medición específica desde el navegador del operador y su prueba de usabilidad. La carga inicial y el despertar de una app suspendida quedan fuera de esta muestra.

La asignación nominal de responsables y la validación para uso operativo continúan pendientes, conforme al documento de fase 6. El enlace y las evidencias están incorporados al Markdown para Colab; no se editó un notebook remoto porque no se proporcionó su enlace en esta conversación.

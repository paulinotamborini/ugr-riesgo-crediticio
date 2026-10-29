# Fase 6 Despliegue

## 6.1 Solución implementada

Se desarrolló una aplicación web con Streamlit que utiliza el Pipeline entrenado y los umbrales obtenidos en la fase 4. Su finalidad es apoyar la revisión de solicitudes, manteniendo la decisión final en el operador.

La interfaz cuenta con dos apartados:

| Apartado | Funcionalidad |
|---|---|
| Evaluar solicitud | Ingreso y validación de ocho campos, cálculo automático de monto/ingreso, estimación de la probabilidad y recomendación según nivel de riesgo. |
| Resultados del modelo | Métricas, niveles, matriz de confusión, importancia global y límites de la evaluación histórica. |

El ingreso exige edad entre 18 y 100 años, valores monetarios positivos, coherencia de antigüedades y categorías admitidas. La antigüedad laboral desconocida se procesa mediante la imputación del Pipeline. Los valores fuera de los rangos históricos producen una advertencia de representatividad.

## 6.2 Arquitectura e integración

`app.py` contiene la interfaz; `core.py`, validación y predicción. `artifacts/` conserva modelo, configuración, resultados y gráficos. Se verifican sus hashes antes de cargarlos y se almacena el modelo en memoria para las consultas posteriores.

La aplicación utiliza nueve predictores a partir de ocho entradas. La proporción se calcula como monto del préstamo dividido por ingreso anual. Se excluyen tasa y calificación, conforme a las fases anteriores. Los dos umbrales se leen de la configuración y mantienen las mismas fronteras del notebook.

## 6.3 Verificación de los requisitos

| Requisito | Evidencia disponible | Estado |
|---|---|---|
| RF01 Ingreso y validación | Pruebas de valores inválidos, faltantes, categorías y coherencia. | Verificado localmente. |
| RF02 Estimación y versión | Equivalencia con el Pipeline y prueba de consulta desde la interfaz. | Verificado localmente. |
| RF03 Tres niveles y recomendación | Pruebas de ambos límites y zona intermedia; recomendación con decisión humana. | Verificado localmente. |
| RF04 Visualización | Tablero con resultados y gráficos históricos versionados. | Verificado mediante AppTest; capturas del navegador pendientes. |
| RNF01 Tiempo de respuesta | Diez consultas consecutivas medidas en AppTest, registradas en PRUEBAS.json. | Medición local disponible; verificar nuevamente en el despliegue. |
| RNF02 Usabilidad | Se completa la consulta sin editar código, con etiquetas, unidades y errores. | Flujo automático verificado; prueba con operador pendiente. |
| RNF03 Mantenibilidad | Separación de interfaz y modelo, dependencias fijadas y comprobación de integridad. | Estructura implementada; publicación y versionado remoto pendientes. |

## 6.4 Publicación y vistas

La aplicación está preparada para publicarse desde GitHub en Streamlit Community Cloud. Al terminar el despliegue, incorporar en esta sección el enlace real, la versión publicada, la fecha y las capturas de Evaluar solicitud y Resultados del modelo.

Estado actual: implementación y pruebas locales completas; publicación pendiente. No se afirma disponibilidad pública hasta verificar la URL.

## 6.5 Mantenimiento y monitoreo

| Actividad | Frecuencia o disparador | Acción |
|---|---|---|
| Disponibilidad y errores | Antes de la presentación y después de cada despliegue. | Ejecutar una consulta válida y una inválida; revisar los registros técnicos del servicio. |
| Dependencias y seguridad | Revisión mensual propuesta y ante una alerta relevante. | Evaluar actualización en entorno de pruebas, comprobar compatibilidad y registrar las versiones. |
| Calidad de entradas | Si se habilita una prueba piloto. | Revisar faltantes, categorías desconocidas y valores fuera de los rangos de referencia; acordar los datos de monitoreo antes de almacenarlos. |
| Rendimiento analítico | Cuando haya suficientes resultados observados de nuevas solicitudes. | Comparar AP, Brier, captura y errores por grupo con la referencia aprobada, considerando incertidumbre y población. |
| Umbrales | Ante cambios de capacidad de revisión o costos de error. | Validar propuestas con Riesgos y documentar la evaluación antes de publicar una nueva versión. |
| Fallos tras una actualización | Ante error de integridad, carga o comportamiento inesperado. | Volver al paquete anterior completo y registrar el motivo. |

La asignación nominal de responsables se completará con el equipo. El desarrollo no incluye una base de solicitudes ni un proceso de monitoreo productivo ya activo. La prueba piloto y la validación del uso de variables personales continúan siendo condiciones para un uso operativo.

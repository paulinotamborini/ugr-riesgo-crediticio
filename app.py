from pathlib import Path
import json
import time
import pandas as pd
import streamlit as st
from core import load_artifacts,evaluate,outside_reference,ARTIFACTS

st.set_page_config(page_title='Evaluación crediticia | Grupo 1 UGR',page_icon='◈',layout='wide')
st.markdown('''<style>
.stApp{background:#f5f7fb;color:#172d43}h1,h2,h3{color:#172d43!important}
[data-testid="stMetric"]{background:white;border:1px solid #e1e7ef;border-radius:12px;padding:18px}
[data-testid="stForm"]{background:white;border-radius:14px}
.eyebrow{color:#0a7e83;letter-spacing:2px;font-size:12px;font-weight:700}
.intro{color:#536779;max-width:850px;line-height:1.65}
</style>''',unsafe_allow_html=True)

@st.cache_resource
def resources():return load_artifacts()

try:
    model,config=resources()
    results=json.loads((ARTIFACTS/'resultados.json').read_text())
except Exception:
    st.error('No se pudieron cargar los archivos del modelo. Revisá la instalación y la integridad de los artefactos.')
    st.stop()

st.markdown('<div class="eyebrow">UGR · GRUPO 1 · APOYO A LA DECISIÓN</div>',unsafe_allow_html=True)
st.title('Evaluación crediticia')
st.markdown('<p class="intro">Consultá el riesgo estimado de una solicitud y la evidencia histórica del modelo. La recomendación orienta la revisión; la decisión final corresponde al operador.</p>',unsafe_allow_html=True)
st.caption(f"Modelo {config['version']} · {config['modelo']} · {config['registros_entrenamiento']:,} registros de entrenamiento".replace(',','.'))
evaluar,resultados=st.tabs(['Evaluar solicitud','Resultados del modelo'])

with evaluar:
    st.subheader('Datos de la solicitud')
    st.info('Usá las unidades monetarias del dataset de referencia. Su moneda no está documentada: no interpretes los importes como pesos ni conviertas monedas sin validar la fuente.')
    with st.form('solicitud'):
        a,b=st.columns(2)
        with a:
            age=st.number_input('Edad (años)',value=30,step=1,key='age')
            income=st.number_input('Ingreso anual (unidades del dataset)',value=55000.0,step=1000.0,key='income')
            unknown=st.checkbox('Antigüedad laboral desconocida',key='unknown')
            emp=st.number_input('Antigüedad laboral (años)',value=4.0,step=1.0,key='emp',help='Si marcás desconocida, se usa la imputación aprendida durante el entrenamiento.')
            amount=st.number_input('Monto del préstamo (unidades del dataset)',value=8000.0,step=500.0,key='amount')
        with b:
            housing=st.selectbox('Situación de vivienda',['RENT','MORTGAGE','OWN','OTHER'],format_func=lambda x:{'RENT':'Alquiler','MORTGAGE':'Hipoteca','OWN':'Propiedad','OTHER':'Otra'}[x],key='housing')
            purpose=st.selectbox('Destino del préstamo',['PERSONAL','EDUCATION','MEDICAL','VENTURE','HOMEIMPROVEMENT','DEBTCONSOLIDATION'],format_func=lambda x:{'PERSONAL':'Personal','EDUCATION':'Educación','MEDICAL':'Salud','VENTURE':'Emprendimiento','HOMEIMPROVEMENT':'Mejora de vivienda','DEBTCONSOLIDATION':'Consolidación de deudas'}[x],key='purpose')
            default=st.selectbox('Antecedentes de incumplimiento',['N','Y'],format_func=lambda x:'No' if x=='N' else 'Sí',key='default')
            history=st.number_input('Antigüedad del historial crediticio (años)',value=8,step=1,key='history')
        submitted=st.form_submit_button('Evaluar solicitud',type='primary')
    if submitted:
        values=dict(edad=age,ingresos_anuales=income,antiguedad_empleo=None if unknown else emp,monto_prestamo=amount,longitud_historial=history,situacion_vivienda=housing,motivo_prestamo=purpose,historial_default=default)
        try:
            start=time.perf_counter()
            result=evaluate(values,model,config)
            elapsed=time.perf_counter()-start
        except ValueError as exc:
            st.error(str(exc))
        except Exception:
            st.error('No se pudo evaluar la solicitud. Revisá los datos o contactá al responsable del modelo.')
        else:
            st.divider()
            st.subheader('Resultado de la evaluación')
            c1,c2,c3=st.columns(3)
            c1.metric('Probabilidad estimada',f"{result['probabilidad']:.1%}")
            c2.metric('Nivel de riesgo',result['nivel'])
            c3.metric('Monto / ingreso anual',f"{result['proporcion']:.1%}")
            advice={'Bajo':'Revisión habitual. El nivel bajo conserva riesgo de incumplimiento.','Intermedio':'Revisión adicional antes de tomar una decisión.','Alto':'Revisión prioritaria por el operador de crédito.'}
            st.info(advice[result['nivel']])
            if outside_reference(values,config,results['rangos_predictores']):
                st.warning('Hay valores fuera de los rangos históricos de referencia. Revisá su representatividad antes de interpretar la estimación.')
            st.caption(f"Versión {result['version']} · Cálculo local de la predicción: {elapsed:.3f} s. Este tiempo excluye red y carga de la página.")
            st.caption('La probabilidad corresponde a la etiqueta histórica de incumplimiento. No representa un riesgo a 12 meses ni a otro plazo documentado.')
    with st.expander('Cómo se interpreta el nivel'):
        st.write(f"Bajo: probabilidad ≤ {config['umbral_bajo']:.4f}. Alto: probabilidad ≥ {config['umbral_alto']:.4f}. Intermedio: valores entre ambos límites.")
        st.write('La proporción monto/ingreso se calcula automáticamente. No se solicitan la tasa de interés ni la calificación crediticia, excluidas del modelo inicial.')

with resultados:
    st.subheader('Evaluación histórica del modelo')
    st.caption('Resultados de la prueba reservada de 6.483 préstamos. No son indicadores de solicitudes ingresadas en esta aplicación.')
    metrics=results['comparacion']['Random forest (prueba)']
    a,b,c=st.columns(3)
    a.metric('Average Precision',f"{metrics['Average Precision']:.4f}")
    b.metric('Brier score',f"{metrics['Brier score']:.4f}")
    c.metric('Captura al priorizar 20 %',f"{metrics['Captura al 20 %']:.1%}")
    comparison=pd.DataFrame(results['comparacion']).T
    st.dataframe(comparison, width='stretch')
    st.image(str(ARTIFACTS/'fase5_evaluacion.png'),caption='Captura, precisión-recall y calibración en prueba.')
    st.subheader('Niveles y errores')
    st.dataframe(pd.DataFrame(results['niveles_test']).T,width='stretch')
    st.image(str(ARTIFACTS/'fase5_matriz_confusion.png'),caption='Matriz de confusión para la alerta de riesgo alto.')
    st.dataframe(pd.DataFrame(results['metricas_alerta']).T,width='stretch')
    st.subheader('Importancia global de las variables')
    st.image(str(ARTIFACTS/'fase5_importancia.png'),caption='Importancia por permutación. Describe el modelo global; no explica causalmente una solicitud individual.')
    with st.expander('Alcance, límites y trazabilidad',expanded=True):
        st.write('El archivo original contiene 32.581 registros; la base limpia, 32.411. Se entrenó con 25.928 observaciones y nueve predictores. Las etiquetas, la moneda y el horizonte temporal no cuentan con documentación primaria suficiente para un uso operativo.')
        st.write('La revisión por grupos es exploratoria y no acredita ausencia de sesgos. En prueba, el grupo alto registró 59,38 % de incumplimiento, frente a la meta de validación de 60 %. La última franja de calibración subestima el riesgo observado.')
        st.write('Los umbrales y la utilización operativa requieren validación de Riesgos y Auditoría. Los resultados observados no garantizan desempeño futuro.')
        st.code('SHA-256 del CSV: '+results['csv_sha256'],language=None)
        st.json(results['versiones'],expanded=False)
st.divider()
st.caption('Ingeniería de Software · Grupo 1 UGR · Modelo versionado y decisión humana')

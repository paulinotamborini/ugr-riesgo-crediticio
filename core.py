"""Validación y predicción del modelo de riesgo auditado."""
from pathlib import Path
import hashlib
import json
import math
import joblib
import pandas as pd

ARTIFACTS=Path(__file__).resolve().parent/'artifacts'
HOUSING={'RENT','MORTGAGE','OWN','OTHER'}
PURPOSES={'PERSONAL','EDUCATION','MEDICAL','VENTURE','HOMEIMPROVEMENT','DEBTCONSOLIDATION'}
LABELS={'edad':'Edad','ingresos_anuales':'Ingreso anual','antiguedad_empleo':'Antigüedad laboral',
 'monto_prestamo':'Monto','longitud_historial':'Antigüedad del historial'}

def load_artifacts(directory=ARTIFACTS):
    directory=Path(directory)
    manifest=json.loads((directory/'integridad.json').read_text())
    for name in ['modelo_riesgo.joblib','modelo_config.json','resultados.json',
                 'fase5_evaluacion.png','fase5_matriz_confusion.png','fase5_importancia.png']:
        if hashlib.sha256((directory/name).read_bytes()).hexdigest()!=manifest.get(name):
            raise ValueError('Falló el control de integridad de los artefactos.')
    config=json.loads((directory/'modelo_config.json').read_text())
    if not 0<=config['umbral_bajo']<config['umbral_alto']<=1:
        raise ValueError('Umbrales inválidos.')
    model=joblib.load(directory/'modelo_riesgo.joblib')
    # Una consulta es pequeña; evita crear cientos de hilos por visitante.
    model.named_steps['clf'].n_jobs=1
    if list(model.feature_names_in_)!=config['predictores']:
        raise ValueError('Esquema del modelo y configuración incompatibles.')
    return model,config

def prepare(values,config):
    row=dict(values)
    for key in LABELS:
        value=row.get(key)
        if key=='antiguedad_empleo' and value is None:
            row[key]=float('nan');continue
        if isinstance(value,bool):raise ValueError(f'{LABELS[key]} debe ser numérico.')
        try:value=float(value)
        except (ValueError,TypeError):raise ValueError(f'Completá {LABELS[key].lower()}.') from None
        if not math.isfinite(value):raise ValueError(f'{LABELS[key]} debe ser un valor finito.')
        row[key]=value
    if not row['edad'].is_integer() or not 18<=row['edad']<=100:
        raise ValueError('La edad debe ser un entero entre 18 y 100 años.')
    if row['ingresos_anuales']<=0 or row['monto_prestamo']<=0:
        raise ValueError('El ingreso anual y el monto deben ser mayores que cero.')
    emp=row['antiguedad_empleo']
    if not math.isnan(emp) and not 0<=emp<=row['edad']:
        raise ValueError('La antigüedad laboral debe estar entre cero y la edad.')
    hist=row['longitud_historial']
    if not hist.is_integer() or not 0<=hist<=row['edad']:
        raise ValueError('La antigüedad del historial debe ser un entero entre cero y la edad.')
    for key,allowed in [('situacion_vivienda',HOUSING),('motivo_prestamo',PURPOSES),('historial_default',{'N','Y'})]:
        if row.get(key) not in allowed:raise ValueError('Seleccioná una opción válida para '+key+'.')
    row['porcentaje_ingreso']=row['monto_prestamo']/row['ingresos_anuales']
    if not math.isfinite(row['porcentaje_ingreso']):raise ValueError('La proporción monto/ingreso no es finita.')
    return pd.DataFrame([row]).loc[:,config['predictores']]

def risk_level(probability,config):
    if probability>=config['umbral_alto']:return 'Alto'
    if probability<=config['umbral_bajo']:return 'Bajo'
    return 'Intermedio'

def outside_reference(values,config,ranges):
    row=prepare(values,config).iloc[0]
    return any(not pd.isna(row[key]) and not limits['min']<=row[key]<=limits['max']
               for key,limits in ranges.items())

def evaluate(values,model,config):
    frame=prepare(values,config)
    positive=list(model.classes_).index(1)
    probability=float(model.predict_proba(frame)[0,positive])
    return {'probabilidad':probability,'nivel':risk_level(probability,config),
            'proporcion':float(frame.iloc[0]['porcentaje_ingreso']),'version':config['version']}

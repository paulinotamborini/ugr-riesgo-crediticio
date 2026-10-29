import math
import numpy as np
import pandas as pd
import pytest
import core

VALID = dict(edad=30, ingresos_anuales=55000, antiguedad_empleo=4,
             monto_prestamo=8000, longitud_historial=8,
             situacion_vivienda='RENT', motivo_prestamo='PERSONAL', historial_default='N')

def test_ratio_y_equivalencia_real():
    model,config=core.load_artifacts()
    frame=core.prepare(VALID,config)
    assert frame.iloc[0]['porcentaje_ingreso']==8000/55000
    result=core.evaluate(VALID,model,config)
    assert result['probabilidad']==pytest.approx(model.predict_proba(frame)[0,1])

@pytest.mark.parametrize('key,value', [('edad',17),('edad',101),('edad',float('nan')),
 ('ingresos_anuales',0),('ingresos_anuales',float('inf')),('monto_prestamo',-1),
 ('antiguedad_empleo',31),('antiguedad_empleo',-1),('longitud_historial',31),
 ('longitud_historial',2.5),('situacion_vivienda','DESCONOCIDO'),('historial_default','SI')])
def test_entrada_invalida(key,value):
    _,cfg=core.load_artifacts()
    with pytest.raises(ValueError):core.prepare({**VALID,key:value},cfg)

def test_empleo_desconocido():
    model,cfg=core.load_artifacts()
    result=core.evaluate({**VALID,'antiguedad_empleo':None},model,cfg)
    assert 0<=result['probabilidad']<=1

def test_fronteras():
    _,cfg=core.load_artifacts();lo=cfg['umbral_bajo'];hi=cfg['umbral_alto']
    assert core.risk_level(lo,cfg)=='Bajo'
    assert core.risk_level(hi,cfg)=='Alto'
    assert core.risk_level((lo+hi)/2,cfg)=='Intermedio'

def test_requeridos_y_no_mutacion():
    _,cfg=core.load_artifacts()
    bad=VALID.copy();bad.pop('edad')
    with pytest.raises(ValueError):core.prepare(bad,cfg)
    original=VALID.copy();core.prepare(VALID,cfg)
    assert VALID==original

def test_integridad_artifacto(tmp_path):
    import shutil
    for f in core.ARTIFACTS.iterdir():
        if f.is_file():shutil.copy2(f,tmp_path/f.name)
    (tmp_path/'modelo_config.json').write_text('{}')
    with pytest.raises(ValueError,match='integridad'):core.load_artifacts(tmp_path)

def test_ratio_y_empleo_fuera_del_rango_historico():
    import json
    _,cfg=core.load_artifacts()
    ranges=json.loads((core.ARTIFACTS/'resultados.json').read_text())['rangos_predictores']
    assert core.outside_reference({**VALID,'ingresos_anuales':4000,'monto_prestamo':35000},cfg,ranges)
    assert core.outside_reference({**VALID,'edad':60,'antiguedad_empleo':50},cfg,ranges)
    assert not core.outside_reference(VALID,cfg,ranges)

def test_integridad_resultados(tmp_path):
    import shutil
    for f in core.ARTIFACTS.iterdir():
        if f.is_file():shutil.copy2(f,tmp_path/f.name)
    (tmp_path/'resultados.json').write_text('{}')
    with pytest.raises(ValueError,match='integridad'):core.load_artifacts(tmp_path)

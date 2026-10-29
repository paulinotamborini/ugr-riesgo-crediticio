from pathlib import Path
from streamlit.testing.v1 import AppTest
APP=Path(__file__).resolve().parents[1]/'app.py'

def test_formulario_y_resultados():
    assert APP.exists()
    at=AppTest.from_file(str(APP),default_timeout=60).run()
    assert not at.exception
    assert len(at.tabs)==2
    at.button[0].click().run()
    assert not at.exception
    assert any(m.label=='Probabilidad estimada' for m in at.metric)

def test_bloquea_error_y_limpia_resultado_anterior():
    assert APP.exists()
    at=AppTest.from_file(str(APP),default_timeout=60).run()
    at.button[0].click().run()
    at.number_input(key='income').set_value(0)
    at.button[0].click().run()
    assert not at.exception
    assert at.error
    assert not any(m.label=='Probabilidad estimada' for m in at.metric)

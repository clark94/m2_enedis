"""Le rafraîchissement respecte la date et conserve le jeu en cas d'échec réseau."""
import sys
from pathlib import Path
import pandas as pd
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import refresh_data

class Response:
    def raise_for_status(self): pass
    def json(self):
        return {'results':[
            {'numero_dpe':'new','date_reception_dpe':'2026-10-01','etiquette_dpe':'F','_geopoint':'45.7,4.8'},
            {'numero_dpe':'old-date','date_reception_dpe':'2020-01-01','etiquette_dpe':'A','_geopoint':'45.7,4.8'}]}
class Session:
    def get(self,*args,**kwargs): return Response()

def test_merge_by_identifier_and_date(monkeypatch,tmp_path):
    path=tmp_path/'data.csv'
    pd.DataFrame([{'numero_dpe':'original','date_reception_dpe':'2025-01-01','etiquette_dpe':'D','latitude':45.,'longitude':4.,'passoire_energetique':0}]).to_csv(path,index=False)
    monkeypatch.setattr(refresh_data,'OUT',path)
    monkeypatch.setattr(refresh_data,'create_session',lambda:Session())
    report=refresh_data.refresh('2026-01-01')
    df=pd.read_csv(path)
    assert set(df.numero_dpe)=={'original','new'}
    assert report['rows']==2
    assert df.loc[df.numero_dpe=='new','passoire_energetique'].iloc[0]==1

def test_network_failure_preserves_dataset(monkeypatch,tmp_path):
    path=tmp_path/'data.csv';path.write_text('original')
    monkeypatch.setattr(refresh_data,'OUT',path)
    def fail(): raise RuntimeError('Réseau indisponible')
    monkeypatch.setattr(refresh_data,'create_session',fail)
    with pytest.raises(RuntimeError): refresh_data.refresh('2026-01-01')
    assert path.read_text()=='original'

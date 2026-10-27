"""Contrat de l'application livrée : vraie prédiction multiclasse et API."""
from app import app, server, explore
from src.service import dataset, predict
from src.config import FEATURES

def test_routes():
    client=server.test_client()
    for route in ['/', '/_dash-layout','/health','/api/schema']:
        assert client.get(route).status_code==200

def test_api_prediction():
    client=server.test_client()
    body=client.get('/api/schema').json['body']
    result=client.post('/api/predict',json=body)
    assert result.status_code==200
    assert result.json['etiquette_dpe'] in 'ABCDEFG'
    assert set(result.json['probabilites'])==set('ABCDEFG')
    assert abs(sum(result.json['probabilites'].values())-1)<1e-6
    assert result.json['conso_chauffage_ef']>=0
    assert client.post('/api/predict',json={}).status_code==400

def test_empty_filters_and_chart_types():
    assert explore([],[],[0,1000],'Barres')[3]==[]
    for name in ['Barres','Histogramme','Boîte à moustaches','Nuage de points']:
        figure,*rest=explore(['69'],['A'],[0,1000],name)
        assert len(figure.data)>0

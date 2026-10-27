"""Actualisation incrémentale par date de réception, sans supprimer le jeu existant."""
import argparse
from datetime import date, datetime, timezone
import json
import tempfile
import pandas as pd
from download_ademe import create_session, API_ROOT, DATASETS, DEPARTEMENTS, extract_next_url
from build_app_dataset import KEEP, OUT

def refresh(since):
    date.fromisoformat(since)
    session=create_session(); frames=[]
    for name,identifier in DATASETS.items():
        for dep in DEPARTEMENTS:
            url=f'{API_ROOT}/{identifier}/lines'
            params={'size':1000,'code_departement_ban_eq':dep,'q':f'date_reception_dpe:[{since} TO *]'}
            count=0
            while url and count<10000:
                response=session.get(url,params=params,timeout=90); response.raise_for_status()
                payload=response.json(); rows=payload.get('results',[])
                if not rows: break
                part=pd.DataFrame(rows); part['source_dataset']='existant' if name=='existants' else 'neuf'
                frames.append(part); count+=len(rows)
                url=extract_next_url(payload,url); params=None
    if not frames: return {'added_or_updated':0,'since':since}
    new=pd.concat(frames,ignore_index=True)
    if not {'numero_dpe','date_reception_dpe','etiquette_dpe','_geopoint'} <= set(new):
        raise ValueError('Schéma API incomplet ; données existantes conservées.')
    new=new[pd.to_datetime(new.date_reception_dpe,errors='coerce')>=pd.Timestamp(since)].copy()
    geo=new['_geopoint'].astype('string').str.split(',',n=1,expand=True)
    new['latitude']=pd.to_numeric(geo[0],errors='coerce'); new['longitude']=pd.to_numeric(geo[1],errors='coerce')
    old=pd.read_csv(OUT,low_memory=False)
    new=new.reindex(columns=old.columns)
    new['passoire_energetique']=new.etiquette_dpe.isin(['F','G']).astype(int)
    combined=pd.concat([old,new],ignore_index=True).drop_duplicates('numero_dpe',keep='last')
    # Écriture atomique : ne remplace jamais le jeu valide par un téléchargement partiel échoué.
    temporary=OUT.with_suffix('.tmp'); combined.to_csv(temporary,index=False); temporary.replace(OUT)
    report={'since':since,'added_or_updated':len(new),'rows':len(combined),'fetched_at':datetime.now(timezone.utc).isoformat(),'limit_per_dataset_department':10000}
    (OUT.parent/'refresh_metadata.json').write_text(json.dumps(report,indent=2))
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--since',required=True)
    print(json.dumps(refresh(parser.parse_args().since),indent=2))

"""Population communale agrégée par département, API Découpage administratif."""
from pathlib import Path
from datetime import datetime, timezone
import json
import requests
ROOT=Path(__file__).resolve().parents[1]
def main():
    records=[]
    for dep in ['38','42','69']:
        url=f'https://geo.api.gouv.fr/communes?codeDepartement={dep}&fields=population,code'
        response=requests.get(url,timeout=60); response.raise_for_status(); rows=response.json()
        records.append({'code_departement_ban':dep,'population_departement':sum(x.get('population',0) or 0 for x in rows),'source':url,'communes':len(rows)})
    payload={'retrieved_at':datetime.now(timezone.utc).isoformat(),'description':'Population publiée par API État ; millésime non exposé dans la réponse. Variable de contexte sans causalité présumée.','departements':records}
    (ROOT/'data/processed/population.json').write_text(json.dumps(payload,indent=2))
    print('Population téléchargée pour trois départements.')
if __name__=='__main__': main()

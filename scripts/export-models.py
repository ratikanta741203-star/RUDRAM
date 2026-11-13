"""Export trusted repository estimators to portable JSON and parity fixtures."""
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
root = Path(__file__).resolve().parent.parent
rf = joblib.load(root / 'ml/models/flood_risk_random_forest.joblib')
xgb = joblib.load(root / 'ml/models/flood_risk_xgboost.joblib')
booster = xgb.get_booster()
config = json.loads(booster.save_config())
base = config['learner']['learner_model_param']['base_score']
base = float(base.strip('[]'))
trees = []
for estimator in rf.estimators_:
    t = estimator.tree_
    trees.append({'left': t.children_left.tolist(), 'right': t.children_right.tolist(), 'feature': t.feature.tolist(), 'threshold': t.threshold.tolist(), 'values': [float(v[0][1] / v.sum()) for v in t.value]})
features = list(rf.feature_names_in_)
model = {'features': features, 'rf': trees, 'xgb': [json.loads(t) for t in booster.get_dump(dump_format='json')], 'base_score': base}
(root / 'web/flood-model.json').write_text(json.dumps(model, separators=(',', ':')))
rng = np.random.default_rng(42)
low = [0,0,0,0,18,40,0,0,0,0,0,100,0,0]
high = [120,350,600,200,40,100,100,120,25,15,1,12000,1,25]
values = rng.uniform(low,high,size=(30,14))
frame = pd.DataFrame(values,columns=features)
expected = .65*xgb.predict_proba(frame)[:,1] + .35*rf.predict_proba(frame)[:,1]
(root / 'tests/model-parity.json').write_text(json.dumps([{'input':dict(zip(features,map(float,row))), 'expected':float(e)} for row,e in zip(values,expected)]))

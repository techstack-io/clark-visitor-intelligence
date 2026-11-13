import pandas as pd
from src.visitor_intelligence.cleaning import clean_visits, company_features

def test_visit_ids_are_not_deduplicated():
    raw = pd.DataFrame({'Company ID':['a','a'],'Company Name':['A','A'],'Visit ID':['v','v'],'Visit country':['US','US'],'Visit region':['California','California'],'Page URL':['/product/1','/contact'],'Visit start time':['2026-11-01 10:00:00 -0600']*2})
    clean, audit = clean_visits(raw)
    assert len(clean) == 2
    feat = company_features(clean)
    assert feat.iloc[0]['distinct_visits'] == 1
    assert feat.iloc[0]['pageviews'] == 2
    assert feat.iloc[0]['product_pageviews'] == 1
    assert clean['is_western_visit'].all()

"""Deterministic, auditable cleaning of Leadfeeder pageview exports."""
import re
from urllib.parse import urlsplit
import pandas as pd

REQUIRED = ['Company ID', 'Visit ID', 'Visit country', 'Visit region', 'Page URL', 'Visit start time']
WEST = {'Alaska','Arizona','California','Colorado','Hawaii','Idaho','Montana','Nevada','New Mexico','Oregon','Utah','Washington','Wyoming'}


def clean_visits(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    missing = sorted(set(REQUIRED) - set(raw.columns))
    if missing:
        raise ValueError('Missing required columns: ' + ', '.join(missing))
    df = raw.copy()
    for col in df.select_dtypes(include=['object','string']).columns:
        df[col] = df[col].astype('string').str.strip().replace('', pd.NA)
    # Pageviews can legitimately share visit IDs and URLs. Only exact row duplicates are flagged.
    exact_duplicates = int(df.duplicated(keep=False).sum())
    df['visit_timestamp_utc'] = pd.to_datetime(df['Visit start time'], utc=True, errors='coerce')
    df['time_on_page_seconds'] = pd.to_numeric(df.get('Time on page (seconds)'), errors='coerce')
    df['invalid_page_time'] = df['time_on_page_seconds'].lt(0).fillna(False)
    df['is_western_visit'] = df['Visit country'].str.upper().eq('US').fillna(False) & df['Visit region'].isin(WEST)
    url = df['Page URL'].fillna('').str.lower()
    df['is_product_page'] = url.str.contains(r'/product/', regex=True)
    df['is_contact_page'] = url.str.contains(r'/contact', regex=True)
    df['is_technical_page'] = url.str.contains(r'technical|document|\.pdf(?:$|\?)', regex=True)
    df['product_id'] = url.str.extract(r'/product/([^/?#]+)', expand=False)
    report = {
        'rows': len(df), 'columns_original': len(raw.columns),
        'exact_duplicate_rows_flagged': exact_duplicates,
        'missing_company_ids': int(df['Company ID'].isna().sum()),
        'missing_visit_ids': int(df['Visit ID'].isna().sum()),
        'unparseable_timestamps': int(df['visit_timestamp_utc'].isna().sum()),
        'negative_page_times': int(df['invalid_page_time'].sum()),
        'missing_visit_regions': int(df['Visit region'].isna().sum()),
    }
    return df, report


def company_features(df: pd.DataFrame) -> pd.DataFrame:
    # Group by stable company ID, not name. Missing IDs cannot be safely joined.
    valid = df.dropna(subset=['Company ID']).copy()
    if valid.empty:
        return pd.DataFrame()
    group = valid.groupby('Company ID', dropna=True)
    result = group.agg(
        company_name=('Company Name', 'first'),
        pageviews=('Page URL','size'),
        distinct_visits=('Visit ID','nunique'),
        product_pageviews=('is_product_page','sum'),
        contact_pageviews=('is_contact_page','sum'),
        technical_pageviews=('is_technical_page','sum'),
        distinct_products=('product_id','nunique'),
        first_seen=('visit_timestamp_utc','min'),
        last_seen=('visit_timestamp_utc','max'),
    ).reset_index()
    return result.sort_values(['distinct_visits','pageviews'], ascending=False)

"""Streamlit research UI; no uploads are sent to a server by this application."""
import io
import pandas as pd
import streamlit as st
from src.visitor_intelligence.cleaning import WEST, REQUIRED, clean_visits, company_features

st.set_page_config(page_title='Clark | Visitor Intelligence Lab', page_icon='📊', layout='wide')
st.markdown('<style>h1,h2,h3{color:#0047BA} div[data-testid="stMetricValue"]{color:#0047BA}</style>', unsafe_allow_html=True)
st.title('Clark | Visitor Intelligence Lab')
st.caption('Research prototype · Leadfeeder Excel upload → quality audit → company features · No model training yet')
file = st.file_uploader('Upload a Leadfeeder Excel export', type=['xlsx'])
if file is None:
    st.info('Upload your Leadfeeder .xlsx export to begin. The raw workbook is not modified.')
    st.stop()
try:
    raw = pd.read_excel(file, sheet_name='Leadfeeder Visits', engine='openpyxl')
    clean, audit = clean_visits(raw)
except Exception as exc:
    st.error(f'Unable to process this workbook: {exc}')
    st.stop()

st.subheader('1 · Data quality audit')
a,b,c,d = st.columns(4)
a.metric('Pageview rows', f'{audit["rows"]:,}')
b.metric('Columns in export', audit['columns_original'])
c.metric('Exact duplicate rows flagged', audit['exact_duplicate_rows_flagged'])
d.metric('Unparseable timestamps', audit['unparseable_timestamps'])
st.caption('Repeated visit IDs are normal; they represent multiple pageviews. Exact duplicates are flagged, not automatically deleted.')
with st.expander('Detailed quality checks', expanded=True):
    st.dataframe(pd.DataFrame([{'check':k,'count':v} for k,v in audit.items()]), hide_index=True, use_container_width=True)
    missing = raw.isna().sum().rename('missing_count').to_frame()
    missing['missing_pct'] = (missing['missing_count'] / len(raw) * 100).round(1) if len(raw) else 0
    st.dataframe(missing.sort_values('missing_count',ascending=False), use_container_width=True)

st.subheader('2 · Select geographic scope')
region = st.radio('Visit location (not company headquarters)', ['Western U.S.','All U.S.','All locations'], horizontal=True)
if region == 'Western U.S.':
    subset = clean[clean['is_western_visit']].copy()
elif region == 'All U.S.':
    subset = clean[clean['Visit country'].str.upper().eq('US').fillna(False)].copy()
else:
    subset = clean.copy()

x,y,z = st.columns(3)
x.metric('Visits', f'{subset["Visit ID"].nunique():,}')
y.metric('Company IDs', f'{subset["Company ID"].nunique():,}')
z.metric('Pageviews', f'{len(subset):,}')
if region == 'Western U.S.':
    st.caption('Western states: ' + ', '.join(sorted(WEST)))

st.subheader('3 · Geographic activity')
if not subset.empty:
    counts = subset.groupby('Visit region',dropna=False)['Visit ID'].nunique().sort_values(ascending=False)
    st.bar_chart(counts)

st.subheader('4 · Company-level features')
features = company_features(subset)
st.caption('Descriptive engagement only; these values are not conversion probabilities or sales-qualified lead scores.')
st.dataframe(features, use_container_width=True, hide_index=True)

st.subheader('5 · Export research datasets')
left,right = st.columns(2)
left.download_button('Download cleaned pageviews (CSV)', data=subset.to_csv(index=False).encode('utf-8-sig'), file_name='clark_cleaned_pageviews.csv', mime='text/csv')
right.download_button('Download company features (CSV)', data=features.to_csv(index=False).encode('utf-8-sig'), file_name='clark_company_features.csv', mime='text/csv')
with st.expander('Inspect cleaned pageviews'):
    st.dataframe(subset.head(300), use_container_width=True)

st.warning('Research prototype: company identifiers and visitor information may be commercially sensitive. Run locally; do not publish a public Streamlit app with production exports. Product/document flags are heuristic and require validation.')

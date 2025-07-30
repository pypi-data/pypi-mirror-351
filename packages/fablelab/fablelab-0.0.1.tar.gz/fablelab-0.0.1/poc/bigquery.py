from google.cloud import bigquery

_bigquery_client = None

def _initialize_client():
    global _bigquery_client
    
    if _bigquery_client is None:
        _bigquery_client = bigquery.Client()
    return _bigquery_client

def query_to_dataframe(query):
    client = _initialize_client()
    
    try:
        query_job = client.query(query)
        return query_job.result().to_dataframe()
    except Exception as e:
        print(e)
        return pd.DataFrame()

def load_from_dataframe(df, table, write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE):
    if df.empty:
        return False
    
    client = _initialize_client()
    job_config = bigquery.LoadJobConfig(
        write_disposition=write_disposition,
        create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED
    )

    try:
        job = client.load_table_from_dataframe(df, table, job_config=job_config)
        job.result()
        print(f'uploaded {len(df)} rows to {table}')
        return True
    except Exception as e:
        print(e)
        return False
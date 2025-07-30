from google.cloud import bigquery

def initialize_bigquery_client():
    global _bigquery_client
    
    if _bigquery_client is None:
        _bigquery_client = bigquery.Client()
    return _bigquery_client

def get_from_bigquery(query):
    client = initialize_bigquery_client()
    
    try:
        query_job = client.query(query)
        return query_job.result().to_dataframe(), None
    except Exception as e:
        return pd.DataFrame(), e

def load_from_dataframe(df, table, write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE):
    if df.empty:
        return False, 'df.empty'
    
    client = initialize_bigquery_client()
    job_config = bigquery.LoadJobConfig(
        write_disposition=write_disposition,
        create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED
    )

    try:
        job = client.load_table_from_dataframe(df, table, job_config=job_config)
        job.result()
        return True, f'uploaded {len(df)} rows to {table_id}'
    except Exception as e:
        return False, e
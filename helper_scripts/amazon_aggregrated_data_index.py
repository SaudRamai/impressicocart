import pandas as pd
from opensearchpy import OpenSearch
import numpy as np

csv_file_path = 'deduplicate' 
df = pd.read_csv(csv_file_path)

df = df[['main_category', 'sub_category']]

df = df.replace({np.nan: ''})

client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_auth=('admin', 'admin@123'),  
    use_ssl=False
)

index_name = 'amazon_aggregated_index'

index_mapping = {
    "mappings": {
        "_meta": {
            "created_by": "file-data-visualizer"
        },
        "properties": {
            "main_category": {"type": "keyword"},
            "sub_category": {"type": "keyword"}
        }
    }
}

if not client.indices.exists(index=index_name):
    client.indices.create(index=index_name, body=index_mapping)

for i, row in df.iterrows():
    doc = row.to_dict()
    try:
        response = client.index(
            index=index_name,
            body=doc,
            id=i
        )
        print(response)
    except Exception as e:
        print(f"Error indexing document ID {i}: {e}")

print("Data insertion completed.")

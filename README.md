## Django Application with OpenSearch Integration
This project integrates a Django application with OpenSearch using Docker for efficient data storage and retrieval. It enhances search functionality with both normal and AI-powered smart search capabilities, leveraging OpenSearch and advanced AI models.

![Screenshot from 2024-06-17 14-58-40](https://github.com/SaudRamai/impressicocart/assets/136465879/0f508712-ea87-40e2-942b-1c88ff95c521)

## Project Structure
Django_and_OpenSearch
```bash

├── docker-compose.yml
├── image.json
├── mysite
│   ├── db.sqlite3
│   ├── http_ca.crt
│   ├── manage.py
│   ├── myapp
│   │   ├── admin.py
│   │   ├── document.py
│   │   ├── migrations
│   │   ├── smartsearch.py
│   │   ├── tests.py
│   │   ├── views.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── templates
│   │   └── url.py
│   ├── mysite
│   │   ├── asgi.py
│   │   ├── form.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── server.key
│   └── static  
├── README.md
└── requirements.txt
```

## Prerequisites

Ensure you have the following installed on your system:
- Docker
- Docker Compose


## Installation
1. Clone the Repository
```bash
git clone https://github.com/SaudRamai/impressicocart.git
cd Django_and_OpenSearch
```

2. Setup Environment Variables
   
Create a .env file in the root directory and add any necessary environment variables. Refer to es_env for any required variables specific to OpenSearch.

4. Build and Run the Containers
```bash
docker-compose up --build
```
This command will build the Docker images and start the containers as defined in docker-compose.yml.

4. Migrate the Database
Once the containers are up and running, apply the database migrations:
```bash
python manage.py migrate
```
5. Create a Superuser

Create a superuser to access the Django admin:
```bash
python manage.py createsuperuser
```
6. Run the Django development server:
```bash
python manage.py runserver 0.0.0.0:8000
```
This command starts the Django development server.
7. Access the Application
You can now access the application at http://localhost:8000 and the OpenSearch dashboard at http://localhost:9200.

## Requirements
The project dependencies are listed in requirements.txt:
```bash
opensearch-dsl==1.4.1
django-opensearch-dsl==1.0.0
django==3.2.8
opensearchpy==1.0.5
langchain==0.4.1
langchain-openai==0.1.0
langchain-core==0.4.1
openai
```
Install these dependencies using pip if you are running the application outside of Docker:
```bash
pip install -r requirements.txt
```

## Docker Configuration
#### Docker Compose
The docker-compose.yml file defines the services required for the application, including the Django web service and OpenSearch.

## OpenSearch Configuration
Configuration specific to OpenSearch can be found in es_env. Ensure all necessary environment variables are set correctly.

Start the development server:
```bash
docker-compose up
```
Stop the development server:
```bash
docker-compose down
```

## Interacting with OpenSearch from Django
To interact with OpenSearch in your Django application, use django-opensearch-dsl. Configure it in your Django settings (settings.py):
```python
INSTALLED_APPS = [
    ...
    'django_opensearch_dsl',
]

OPENSEARCH_DSL = {
    'default': {
        'hosts': 'http://localhost:9200'
        "http_auth": ('username', 'password'),

    },
}
```

Example usage in Django models:

```python
from django_opensearch_dsl import Document, fields
from django_opensearch_dsl.registries import registry
from .models import Customer, AggregatedCategory, Product

@registry.register_document
class CustomerDocument(Document):
    class Index:
        name = 'customer'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = Customer
        fields = [
            
            'name',
            'date_created',
        ]

@registry.register_document
class AggregatedIndex(Document):
    id = fields.IntegerField()

    class Index:
        name = 'your_index_name'

    class Django:
        model = AggregatedCategory
        fields = [
            'main_category',
            'sub_category'
        ]


@registry.register_document
class ProductDocument(Document):
    class Index:
        name = 'your_index_name'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = Product  
        fields = [
            'sub_category',
            'name',
            'actual_price',
            'discount_price',
            'ratings',
            'no_of_ratings',
            'link',
        ]

    def save(self, **kwargs):
        return super(ProductDocument, self).save(**kwargs)
```
## Ingesting Data into OpenSearch

For detailed steps on ingesting data into OpenSearch, please refer to the following document which outlines the entire process: [Data Ingestion into OpenSearch](https://github.com/SaudRamai/impressicocart/blob/master/Ingesting_Data_into_OpenSearch.pdf).

### Summary of the Process

### Data Preparation
1. **Retrieve data from the [Amazon Products Dataset on Kaggle](https://www.kaggle.com/datasets/lokeshparab/amazon-products-dataset).**
2. **Clean the data** by removing duplicates, filling missing values, fixing errors, standardizing formats, and removing unnecessary fields.

### OpenSearch Index Creation
1. Create the `amazon_data` index for detailed product information.
2. Create the `amazon_aggregated_index` for aggregated category data.

### Data Ingestion Steps
1. **Convert the CSV data to JSON format** using a Python script.
2. **Bulk index the JSON data** into OpenSearch.
3. **Load data into the `amazon_aggregated_index`** using another Python script.

### Ingest Pipeline for Reindexing
1. **Set up an ingest pipeline** to handle invalid field values during reindexing.

### Reindexing Data
1. **Reindex data from the `amazon_data` index** to `amazon_data_v2` using the ingest pipeline.

## Search Functionality
### Overview
This Django application provides enhanced search capabilities using both traditional keyword-based search and AI-powered smart search.

### Normal Search
Users can perform traditional keyword-based searches using the search bar. Queries are processed directly against the OpenSearch index to retrieve relevant products based on matching keywords, categories, and other specified criteria.

Users can perform traditional keyword-based searches using the search bar:

1. **Input:** Users enter search queries in the search bar located on the application's navbar.

![Screenshot from 2024-06-18 11-11-04](https://github.com/SaudRamai/impressicocart/assets/136465879/770e84d2-f400-46fd-a0b4-2bb0c1ed4bbf)

2. **Processing:** The system processes the query against the OpenSearch index.

3. **Execution and Display:** Queries are executed to retrieve relevant products based on matching keywords, categories, and criteria. Results are then displayed in a user-friendly format on the search results page.

![Screenshot from 2024-06-18 11-11-23](https://github.com/SaudRamai/impressicocart/assets/136465879/06511db9-6af1-483f-9821-d6c53ed72b1d)



### Smart Search
This project enhances the search functionality of an e-commerce platform by enabling users to input queries in natural language. The system uses AI to convert these queries into structured OpenSearch queries, retrieving relevant products efficiently from an OpenSearch database.It  provides a user-friendly search experience where users can input queries in natural language. The system translates these queries into OpenSearch queries to retrieve products matching user intent accurately and efficiently.

Enhanced AI-powered search capabilities:

#### Enabling Premium Smart Search
To activate premium smart search features:


<img src="https://github.com/SaudRamai/impressicocart/assets/136465879/ba347937-3e37-4def-8f21-98eb61440f88" width="492" height="40" />   
➜  
<img src="https://github.com/SaudRamai/impressicocart/assets/136465879/43db4b14-ac9c-420d-ba5b-d303a0e81295" width="492"  height="40"  />




1. **Input:** Users input queries in natural language through the search interface.

   ![Screenshot from 2024-06-18 11-12-27](https://github.com/SaudRamai/impressicocart/assets/136465879/e62ff924-0cf5-47dd-ab6e-8d6feb9ed060)

2. **Query Interpretation:** AI processes the query to understand user intent (product names, categories, etc.).

3. **Query Generation:** Converts information into valid OpenSearch query DSL.

4. **Execution:** Executes the generated query against the OpenSearch database.

5. **Display:** Displays results formatted for user-friendly navigation with pagination.

   ![Screenshot from 2024-06-18 11-12-36](https://github.com/SaudRamai/impressicocart/assets/136465879/d40fa5dd-f137-4935-875e-c1a0df7c1b21)

##### Components
- An AI language model interprets user natural language queries.

##### Query Parser
- Converts extracted information into valid OpenSearch queries.



### Implementation

**Step 1: Set Up OpenAI** 

Store Your API Key Securely:

Create a .env file in your project directory if you don't have one.

Add your OpenAI API key to this file. For example:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```
Replace your_openai_api_key_here with the actual API key you obtained from OpenAI.

Define the prompt template for query generation.

**Step 2: Configure OpenSearch** 

Set up the OpenSearch instance with appropriate mappings and categories.

Ensure data is indexed correctly for efficient searching.

**Step 3: Develop Smart Search Function**

Create the function to handle user input and interact with OpenAI.

Implement query execution against OpenSearch.

Manage pagination and result display

## Usage
- Input: Users enter search queries in the search bar located on the application's navbar.
- Processing: Depending on the type of search selected (normal or smart), the system processes the query accordingly.
- Execution: Queries are executed against the OpenSearch database to fetch matching products.
- Display: Search results are displayed to users in a user-friendly format on the search results page, supporting pagination for ease of navigation.




















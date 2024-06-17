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
## Search Functionality
### Overview
This Django application provides enhanced search capabilities using both traditional keyword-based search and AI-powered smart search.

### Normal Search
Users can perform traditional keyword-based searches using the search bar. Queries are processed directly against the OpenSearch index to retrieve relevant products based on matching keywords, categories, and other specified criteria.

![Screenshot from 2024-06-17 15-04-04](https://github.com/SaudRamai/impressicocart/assets/136465879/ac06169d-5cfb-488d-a789-0302fb253577)

### Smart Search
This project enhances the search functionality of an e-commerce platform by enabling users to input queries in natural language. The system uses AI to convert these queries into structured OpenSearch queries, retrieving relevant products efficiently from an OpenSearch database.It  provides a user-friendly search experience where users can input queries in natural language. The system translates these queries into OpenSearch queries to retrieve products matching user intent accurately and efficiently.

![Screenshot from 2024-06-17 15-04-10](https://github.com/SaudRamai/impressicocart/assets/136465879/8861a93e-4ebf-4b63-bf82-72dd3e5ef000)

##### Components
- An AI language model interprets user natural language queries.

##### Query Parser
- Converts extracted information into valid OpenSearch queries.

##### OpenSearch Database
- Input: Users enter search queries in the search bar located on the application's navbar.

##### Process Flow
- Input: Users enter search queries in the search bar located on the application's navbar.
- User Input: Users input search queries in natural language through the search interface.
- Query Interpretation: AI processes the query to understand user intent and extract key details like product names, categories, price ranges, and ratings.
- Query Generation: The query parser converts extracted information into a valid OpenSearch query DSL, ensuring adherence to schema and constraints.
- Query Execution: The generated query is executed against the OpenSearch database, establishing a connection to the OpenSearch cluster to retrieve matching products.
- Result Retrieval: Search results are fetched and formatted for display, ensuring a user-friendly experience with support for pagination to navigate through multiple result pages.

### Implementation

Frontend: The search bar is implemented using Django templates, allowing users to input search queries directly on the application's navbar.

Backend: Django views handle the logic for both normal and smart search functionalities, interacting with the OpenSearch database through django-opensearch-dsl.

Integration: Configuration in settings.py ensures seamless integration with OpenSearch, enabling efficient querying and retrieval of product data.

## Usage
- Input: Users enter search queries in the search bar located on the application's navbar.
- Processing: Depending on the type of search selected (normal or smart), the system processes the query accordingly.
- Execution: Queries are executed against the OpenSearch database to fetch matching products.
- Display: Search results are displayed to users in a user-friendly format on the search results page, supporting pagination for ease of navigation.




















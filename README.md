## Django Application with OpenSearch Integration
This project integrates a Django application with OpenSearch using Docker for efficient data storage and retrieval.

## Project Structure
Django_and_Elasticsearch
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
cd Django_and_Elasticsearch
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

## Usage
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





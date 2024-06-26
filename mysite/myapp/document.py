from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Customer, AggregatedCategory, Product, Image

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
            'id',
            'name',
            'date_created',
        ]

@registry.register_document
class AggregatedIndex(Document):
    id = fields.IntegerField()

    class Index:
        name = 'amazon_aggregated_index'

    class Django:
        model = AggregatedCategory
        fields = [
            'main_category',
            'sub_category'
        ]


@registry.register_document
class ProductDocument(Document):
    class Index:
        name = 'amazon_data_2'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = Product  
        fields = [
            'name',
            'actual_price',
            'discount_price',
            'ratings',
            'no_of_ratings',
            'link',
        ]

    def save(self, **kwargs):
        return super(ProductDocument, self).save(**kwargs)

@registry.register_document
class ImageDocument(Document):
    class Index:
        name = 'image'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = Image
        fields = [
            'id',
            'image',
        ]

import os
import json
# import streamlit as st
from openai import OpenAI
from opensearchpy import OpenSearch
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Dict, Optional

from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))
# load_dotenv()

openapi_key = os.getenv("OPEN_API_KEY")

class Match(BaseModel):
    name: str

class Term(BaseModel):
    main_category: Optional[str]
    sub_category: Optional[str]

class RangeValue(BaseModel):
    lte: Optional[float]
    gt: Optional[float]

class Range(BaseModel):
    actual_price: Optional[RangeValue]
    discount_price: Optional[RangeValue]
    no_of_ratings: Optional[RangeValue]
    ratings: Optional[RangeValue]

class Script(BaseModel):
    source: str
    params: Dict

class FilterClause(BaseModel):
    term: Optional[Term]
    range: Optional[Range]
    # script: Optional[Script]

class BoolQuery(BaseModel):
    must: List[Match]
    filter: List[FilterClause]

class Query(BaseModel):
    bool: BoolQuery

class QueryStructure(BaseModel):
    query: Query


    


structured_index_name = "amazon_data_v2"


def chat_gpt2(query):

    model = ChatOpenAI(api_key=openapi_key, temperature=0)
    # print("hello  ::   *************     ", query)

    # And a query intented to prompt a language model to populate the data structure.
    # query = f"read this text extracted from a user resume carefully and classify this based on different criteria into the json format.   text : {text} \n\n"

    # Set up a parser + inject instructions into the prompt template.
    parser = JsonOutputParser(pydantic_object=QueryStructure)

    prompt = PromptTemplate(
        template="take the given user query in human language and generate an Open search quey from it according to the given instructions \n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | model | parser

    response = chain.invoke({"query": query})
    

    return response


def es_connect():
    try:
        es = OpenSearch(
            hosts=[{'host': 'localhost', 'port': 9200}],
            http_auth=('admin', 'admin@123'),
            use_ssl=False,
            verify_certs=False,  # Set to True if you have proper SSL certificates
            ssl_show_warn=False
        )
        # Optional: Check if the connection is successful by making a simple request
        es.info()
        print("Connection established")
        return es

    except Exception as e:
        # st.error(f"Failed to connect to OpenSearch cluster: {e}")
        return None



es = es_connect()



def execute_query(index_name, query_dsl):
    try:
        # Execute the search query
        response = es.search(index=index_name, body=query_dsl)
        return response
    except Exception as e:
        # st.error(f"Failed to execute OpenSearch query: {e}")
        return []



def execute_count_query(index_name, query_dsl):
    try:
        # Execute the count query
        response = es.count(index=index_name, body=query_dsl)
        return response['count']
    except Exception as e:
        print(f"Failed to execute OpenSearch count query: {e}")
        return 0


open_search_data ={
    "mappings": {
        "amazon_data_v2": {
            "mappings": {
                "properties": {
                    "actual_price": {
                        "type": "double"
                    },
                    "discount_price": {
                        "type": "double"
                    },
                    "id": {
                        "type": "integer"
                    },
                    "link": {
                        "type": "text"
                    },
                    "main_category": {
                        "type": "keyword"
                    },
                    "name": {
                        "type": "search_as_you_type",
                        "doc_values": "false",
                        "max_shingle_size": 3
                    },
                    "no_of_ratings": {
                        "type": "integer"
                    },
                    "ratings": {
                        "type": "double"
                    },
                    "sub_category": {
                        "type": "keyword"
                    }
                }
            }
        }
    },
    "categories": {
        "toys & baby products": [
            "nursing & feeding",
            "diapers",
            "toys gifting store",
            "strollers & prams",
            "baby bath, skin & grooming",
            "baby products",
            "international toy store",
            "stem toys store",
            "toys & games"
        ],
        "home & kitchen": [
            "all home & kitchen",
            "home d\u00e9cor",
            "kitchen & dining",
            "garden & outdoors",
            "indoor lighting",
            "bedroom linen",
            "sewing & craft supplies",
            "furniture",
            "home furnishing",
            "home improvement",
            "home storage",
            "kitchen storage & containers"
        ],
        "appliances": [
            "washing machines",
            "refrigerators",
            "all appliances",
            "heating & cooling appliances",
            "kitchen & home appliances"
        ],
        "stores": [
            "women's fashion",
            "the designer boutique",
            "sportswear",
            "amazon fashion",
            "men's fashion"
        ],
        "sports & fitness": [
            "cricket",
            "fitness accessories",
            "running",
            "badminton",
            "cardio equipment",
            "camping & hiking",
            "cycling",
            "all exercise & fitness",
            "all sports, fitness & outdoors",
            "football",
            "strength training",
            "yoga"
        ],
        "car & motorbike": [
            "car & bike care",
            "all car & motorbike products",
            "car accessories",
            "car electronics",
            "car parts",
            "motorbike accessories & parts"
        ],
        "women's clothing": [
            "clothing",
            "western wear",
            "lingerie & nightwear",
            "ethnic wear"
        ],
        "beauty & health": [
            "health & personal care",
            "make-up",
            "luxury beauty",
            "beauty & grooming",
            "diet & nutrition",
            "household supplies",
            "personal care appliances",
            "value bazaar"
        ],
        "accessories": [
            "watches",
            "sunglasses",
            "handbags & clutches",
            "fashion & silver jewellery",
            "jewellery",
            "bags & luggage",
            "gold & diamond jewellery"
        ],
        "grocery & gourmet foods": [
            "snack foods",
            "coffee, tea & beverages",
            "all grocery & gourmet foods"
        ],
        "bags & luggage": [
            "travel duffles",
            "suitcases & trolley bags",
            "wallets",
            "backpacks",
            "rucksacks",
            "travel accessories"
        ],
        "industrial supplies": [
            "industrial & scientific supplies",
            "lab & scientific",
            "janitorial & sanitation supplies",
            "test, measure & inspect"
        ],
        "men's clothing": [
            "innerwear",
            "shirts",
            "jeans",
            "t-shirts & polos"
        ],
        "kids' fashion": [
            "kids' watches",
            "baby fashion",
            "school bags",
            "kids' clothing",
            "kids' fashion",
            "kids' shoes"
        ],
        "women's shoes": [
            "shoes",
            "ballerinas",
            "fashion sandals"
        ],
        "tv, audio & cameras": [
            "headphones",
            "all electronics",
            "camera accessories",
            "cameras",
            "home audio & theater",
            "home entertainment systems",
            "security cameras",
            "speakers",
            "televisions"
        ],
        "music": [
            "musical instruments & professional audio"
        ],
        "home, kitchen, pets": [
            "refurbished & open box"
        ],
        "pet supplies": [
            "all pet supplies",
            "dog supplies"
        ],
        "men's shoes": [
            "casual shoes",
            "formal shoes",
            "sports shoes"
        ]
    }
}




def smartsearch(query):


    if query:

        example = {
            "query": {
                "function_score": {
                    "query": {
                        "bool": {
                        "must": [
                            {
                            "match": {
                                "name": {
                                "query": "Peter England slim fit t-shirts",
                                "fuzziness": "AUTO"
                                }
                            }
                            }
                        ],
                        "should": [
                            {
                            "terms": {
                                "main_category": [
                                "men's clothing",
                                "women's clothing"
                                ]
                            }
                            },
                            {
                            "terms": {
                                "sub_category": [
                                "shirts",
                                "t-shirts & polos"
                                ]
                            }
                            }
                        ],
                        "filter": [
                            {
                            "range": {
                                "actual_price": {
                                "lte": 500
                                }
                            }
                            },
                            {
                            "range": {
                                "discount_price": {
                                "lte": 500
                                }
                            }
                            },
                            {
                            "range": {
                                "no_of_ratings": {
                                "gt": 0
                                }
                            }
                            },
                            {
                            "range": {
                                "ratings": {
                                "gt": 0
                                }
                            }
                            }
                        ]
                        }
                    },
                    "functions": [
                        {
                        "script_score": {
                            "script": {
                            "source": """
                                        double actualPrice = doc['actual_price'].size() > 0 ? doc['actual_price'].value : -1;
                                        double discountPrice = doc['discount_price'].size() > 0 ? doc['discount_price'].value : -1;
                                        if (actualPrice <= 0 || discountPrice <= 0) {
                                            return 0;
                                        }
                                        double discountPercentage = (actualPrice - discountPrice) / actualPrice * 100;
                                        double discountThreshold = params.discount_threshold;
                                        if (discountPercentage > discountThreshold) {
                                            return discountPercentage;
                                        } else {
                                            return 0;
                                        }
                                    """,
                            "params": {
                                "discount_threshold": 10
                            },
                            "lang": "painless"
                            }
                        }
                        }
                    ]
                }
            }
        }



        prompt2 = f"""

            act as a Open search query generator whose task is to Generate OpenSearch queries from user queries (in human language) for an e-commerce website. 

            Now your task is to :
            1. carefully understand and analyze the user query to extract any data provided in the user query like the product description, price range, rating etc..
            2. Map the extracted product description to the appropriate category in the OpenSearch index as provided below.
            3. Generate an OpenSearch query based on the extracted product description and mapped category.
            4. Ensure the query filters relevant products based on the provided category and matches the user's description.
            5. Return the OpenSearch query for further processing and execution.


            Below is the mapping of the index in Open search that contains the products
            mappings : {json.dumps(open_search_data.get('mappings', {}), indent=4)}

            Below JSON data contains categories and their corresponding subcategories from which you have to choose from (most important to only choose strictly from given options). The top-level keys represent main categories, and each main category maps to a list of its underlying subcategories do not confuse , choose main and sub category(s) differently carefully:
            categories_info: {json.dumps(open_search_data.get('categories', {}), indent=4)}

            note: it is important you have to choose man and sub category or categories. you cant leave it empty

            [Note]
            '- Only print the Query, nothing else. No explanation and opening text etc.
            '- The "must" clause should only contain the "name" field  also enhance the names (so that it matches the product user is reffering to more closely)'
            '- also give special care to main and sub category (important) fill it with the values you think have most chances of containing the categories among the provided list you can select multiple main_categories and also multiple sub_categories'
            - Also ensure to strictly follow the OpenSearch Mapping.
            - refrain from employing nested queries important.
            - Also under no circumstances are you allowed to make up any data by yourself in the query only and only use the data i provided you strictly
            - always remember the only thing that comes under must field is only and only name nothing else everything else will go under filter clause 
            - if the user query ask products based on discount percentage then use source script query like in the below example (you only have to change the discount_thershold according to query) then write it accordingly and if the source script query is not required then dont include it (most important) 
            
            [Schema]
            - main_category and sub_category should be inside (should clause)
            - for any Range or sorting, number of rating, actual price, discounted price, or any other integer fields should be inside (filter clause)
            - Name should be inside must/match clause.



            NOTE : TREAT ACTUAL_PRICE AND DISCOUNTED_PRICE AS THE SAME FIELD both contains the price 
            give extra care to always filling the price range fields dont leave them empty if user query includes a price if user did not include price then take it as greater then >0 otherwise whatever range the user specified
            similarly give extra care to always filling the rating range field dont leave them empty if user query includes a rating if user did not include rating then take it as greater then >0 otherwise whatever range the user specified
            similarly do it with number of ratings


            example :

                for user query = peter england slim fit tshirts under 3000 having more than 10% discount
                answer {json.dumps(example, indent=4)}



            just return me the query nothing else
            now Generate the output below:



            
            USER_QUERY = {query}

        """
        

        final_answer = chat_gpt2(prompt2)

        if final_answer :

            try :
                query_dsl = final_answer
                total_results = execute_count_query(structured_index_name, query_dsl)
                if total_results == 0:
                    return False, 0
                    
                total_pages = (total_results // 5)



                # final_answer["sort"] = [{"ratings": {"order": "desc"}}]
                final_answer['from'] = 0
                final_answer["size"] = 5
                query_dsl = final_answer
                # print("helloooooooooooo                   :            ",json.dumps(final_answer, indent=4))

                # results = execute_query(structured_index_name, query_dsl)
                
                    
                return query_dsl, total_pages

            except Exception as e:

                    return False, 0 
            

    return False, 0 



def re_execute_search(query_dsl, start_index, end_index, page_size):
    if query_dsl:
        query_dsl['from'] = start_index
        query_dsl['size'] = page_size
        results = execute_query(structured_index_name, query_dsl)

        if results : 

            hits = results['hits']['hits']

            # Extracting only the source data and creating a list
            results = [hit['_source'] for hit in hits]

            print(start_index, end_index, page_size)
            
            return results
from functools import cache
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from mysite.form import createuserform, createcustomerform
from myapp.document import ProductDocument, AggregatedIndex
from .models import AggregatedCategory, Product
from django.http import JsonResponse
from django_opensearch_dsl import Document
from opensearch_dsl import Q
import json
from django.core.cache import cache
from collections import defaultdict
from .smartsearch import re_execute_search,smartsearch

with open('../image.json', 'r') as json_file:
    subcategories_image_urls = json.load(json_file)

def home(request):
    def get_products(criteria_query, unique_categories, size=20):
        products = []
        response = criteria_query[:size].execute()
        for hit in response:
            product_id = getattr(hit, 'id')
            if product_id not in unique_categories:
                product_data = {
                    'id': product_id,
                    'name': getattr(hit, 'name', None),
                    'actual_price': getattr(hit, 'actual_price', None),
                    'discount_price': getattr(hit, 'discount_price', None),
                    'ratings': getattr(hit, 'ratings', None),
                    'no_of_ratings': getattr(hit, 'no_of_ratings', None),
                    'link': getattr(hit, 'link', None),
                    'image_url': subcategories_image_urls.get(getattr(hit, 'sub_category', ''), '')
                }
                products.append(product_data)
                unique_categories.add(product_id)
        return products

    search = AggregatedIndex.search()[:100].execute()
    main_categories_with_subcategories = defaultdict(list)
    for hit in search:
        main_categories_with_subcategories[hit.main_category].append(hit.sub_category)

    data = [{'main_category': main_category, 'sub_categories': sub_categories}
            for main_category, sub_categories in main_categories_with_subcategories.items()]

    top_products, unique_categories = [], set()
    for main_category, sub_categories in main_categories_with_subcategories.items():
        for sub_category in sub_categories:
            sub_query = ProductDocument.search().filter('term', sub_category=sub_category)
            top_prods = sub_query.sort({'ratings': {'order': 'desc'}}).execute()
            if top_prods:
                top_prod = top_prods[0]
                discount_query = sub_query.filter('range', discount_price={'gt': 0})
                discounted_prods = discount_query.sort({'discount_price': {'order': 'desc'}}).execute()
                discount_prod = discounted_prods[0] if discounted_prods else None

                for prod in [top_prod, discount_prod]:
                    if prod and prod.id not in unique_categories:
                        product_data = {
                            'id': prod.id,
                            'name': prod.name,
                            'actual_price': prod.actual_price,
                            'discount_price': prod.discount_price,
                            'ratings': prod.ratings,
                            'no_of_ratings': prod.no_of_ratings,
                            'link': prod.link,
                            'image_url': subcategories_image_urls.get(prod.sub_category, '')
                        }
                        top_products.append(product_data)
                        unique_categories.add(prod.id)
        if len(top_products) >= 5:
            break

    biggest_discounts = get_products(ProductDocument.search().sort('-discount_price'), unique_categories)
    top_mens_rated_products = get_products(
        ProductDocument.search()
        .filter('term', main_category="men's shoes")
        .sort('-ratings', '-no_of_ratings'),
        unique_categories
    )

    context_home = {
        'data': data,
        'biggest_discounts': biggest_discounts,
        'top_mens_rated_products': top_mens_rated_products,
    }
    return render(request, 'customapp/home.html', context_home)

def products_thumbnails(request):
    category = request.GET.get('category', '')

    def get_product_thumbnails(criteria_query, size=10):
        thumbnails = []
        unique_categories = set()
        response = criteria_query[:size].execute()
        for hit in response:
            product_id = hit.meta.id
            if product_id not in unique_categories:
                thumbnail_data = {
                    'id': product_id,
                    'name': hit.name,
                    'actual_price': hit.actual_price,
                    'discount_price': hit.discount_price,
                    'image_url': subcategories_image_urls.get(hit.sub_category, '')
                }
                thumbnails.append(thumbnail_data)
                unique_categories.add(product_id)
        return thumbnails

    context = {}

    if category == 'top_rated_products':
        query = ProductDocument.search().filter('range', ratings={'gte': 4}).sort('-ratings')
        top_rated_products = get_product_thumbnails(query, size=14)
        context = {'top_rated_products': top_rated_products}

    elif category == 'products_50_off':
        query = ProductDocument.search().filter('script', script={
            "source": """
                if (doc.containsKey('actual_price') && doc.containsKey('discount_price') && !doc['actual_price'].empty && !doc['discount_price'].empty) {
                    double actualPrice = doc['actual_price'].value;
                    double discountPrice = doc['discount_price'].value;
                    if (actualPrice != 0) {
                        double discountPercentage = ((actualPrice - discountPrice) / actualPrice) * 100;
                        return Math.abs(discountPercentage - 50) < 0.1; 
                    } else {
                        return false; 
                    }
                } else {
                    return false; 
                }
            """,
            "lang": "painless"
        })
        products_50_off = get_product_thumbnails(query, size=100)
        context = {'products_50_off': products_50_off}

    elif category == 'products_30_off':
        query = ProductDocument.search().filter('script', script={
            "source": """
                if (doc.containsKey('actual_price') && doc.containsKey('discount_price') && !doc['actual_price'].empty && !doc['discount_price'].empty) {
                    double actualPrice = doc['actual_price'].value;
                    double discountPrice = doc['discount_price'].value;
                    if (actualPrice != 0) {
                        double discountPercentage = ((actualPrice - discountPrice) / actualPrice) * 100;
                        return Math.abs(discountPercentage - 30) < 0.1; 
                    } else {
                        return false; 
                    }
                } else {
                    return false; 
                }
            """,
            "lang": "painless"
        })
        products_30_off = get_product_thumbnails(query, size=150)
        context = {'products_30_off': products_30_off}

    elif category == 'under_299':
        query = ProductDocument.search().filter('range', actual_price={'lte': 299}).sort('-actual_price')
        products_under_299 = get_product_thumbnails(query, size=14)
        context = {'products_under_299': products_under_299}

    elif category == 'top_10_women_shoes':
        query = ProductDocument.search().filter('term', main_category="women's shoes").filter('term', sub_category="shoes").sort('-ratings')[:10]
        top_10_women_shoes = get_product_thumbnails(query, size=14)
        context = {'top_10_women_shoes': top_10_women_shoes}

    elif category == 'under_199':
        query = ProductDocument.search().filter('range', actual_price={'lte': 199}).sort('-actual_price')
        products_under_199 = get_product_thumbnails(query, size=14)
        context = {'products_under_199': products_under_199}

    elif category == 'biggest_discounts':
        query = ProductDocument.search().sort('-discount_price')
        products_biggest_discounts = get_product_thumbnails(query, size=14)
        context = {'products_biggest_discounts': products_biggest_discounts}

    return render(request, 'customapp/products_thumbnails.html', context)


def product_search_view(request):
    search = AggregatedIndex.search()
    response = search[:100].execute()
    main_categories_with_subcategories = {}
    for hit in response:
        main_category = hit.main_category
        sub_category = hit.sub_category
        if main_category not in main_categories_with_subcategories:
            main_categories_with_subcategories[main_category] = set()
        main_categories_with_subcategories[main_category].add(sub_category)

    data = [{'main_category': main_category, 'sub_categories': list(sub_categories)}
            for main_category, sub_categories in main_categories_with_subcategories.items()]

    main_category = request.GET.get('main_category', '')
    subcategory = request.GET.get('subcategory', '')
    current_page = int(request.GET.get('page', 1))

    query = Q('bool', must=[
        Q('match', main_category=main_category),
        Q('match', sub_category=subcategory)
    ]).to_dict()
    start_index = (current_page - 1) * 12
    end_index = current_page * 12

    search = ProductDocument.search().query(query)[start_index:end_index]
    response = search.execute()

    products = []
    unique_names = set()

    for hit in response:
        name = getattr(hit, 'name')

        if name not in unique_names:
            product_data = {
                'name': name,
                'actual_price': getattr(hit, 'actual_price'),
                'discount_price': getattr(hit, 'discount_price'),
                'ratings': getattr(hit, 'ratings'),
                'no_of_ratings': getattr(hit, 'no_of_ratings'),
                'link': getattr(hit, 'link'),
                'image_url': subcategories_image_urls.get(hit.sub_category, '')
            }
            products.append(product_data)
            unique_names.add(name)

    total_products = response.hits.total.value
    total_pages = (total_products // 12) + (1 if total_products % 12 else 0)

    page_range_start = max(1, current_page - 0)
    page_range_end = min(total_pages + 1, page_range_start + 5)

    context = {
        'data': data,
        'products': products,
        'selected_main_category': main_category,
        'selected_subcategory': subcategory,
        'current_page': current_page,
        'total_pages': total_pages,
        'page_range': range(page_range_start, page_range_end)
    }
    return render(request, 'customapp/products.html', context)



def search_view(request):
    print(request)
    query = request.GET.get('q', '')
    smartsearchx = request.GET.get('smartsearchx', 'off')
    results = []
    current_page = int(request.GET.get('page', 1))
    page_size = 12

    if query and smartsearchx:
        
        cache_key = f"smart_results_{query}_{smartsearchx}"
        cached_data = cache.get(cache_key)
        
        if not cached_data:
            query_dsl, total_pages = smartsearch(query)
            if query_dsl:
                cached_data = {'query_dsl': query_dsl, 'total_pages': total_pages}
                cache.set(cache_key, cached_data, timeout=None)  
        else:
            query_dsl = cached_data['query_dsl']
            total_pages = cached_data['total_pages']


        start_index = (current_page - 1) * page_size
        end_index = current_page * page_size

        paginated_results = re_execute_search(query_dsl, start_index, end_index, page_size)

        for result_data in paginated_results:
            result_data['image_url'] = subcategories_image_urls.get(result_data["sub_category"], '')

        page_range_start = max(1, current_page - 0)
        page_range_end = min(total_pages + 1, page_range_start + 5)

        context = {
            'results': paginated_results,
            'current_page': current_page,
            'total_pages': total_pages,
            'query': query,
            'smartsearchx':smartsearchx,
            'page_range': range(page_range_start, page_range_end),
        }

        print("entered in smart search")
        return render(request, 'customapp/search.html', context)

        
    if query:
        search = ProductDocument.search().query(
            "multi_match",
            query=query,
            fields=['name', 'main_category', 'sub_category']
        )
        start_index = (current_page - 1) * page_size
        end_index = current_page * page_size
        

        search = search[start_index:end_index]
        response = search.execute()
        results = []
        for hit in response:
            result_data = hit.to_dict()
            result_data['image_url'] = subcategories_image_urls.get(hit.sub_category, '')
            results.append(result_data)
        total_results = response.hits.total.value
    else:
        total_results = 0
        total_pages = 0

    total_pages = (total_results // page_size) + (1 if total_results % page_size > 0 else 0)

    page_range_start = max(1, current_page - 0)
    page_range_end = min(total_pages + 1, page_range_start + 5)
    
    context = {
        'results': results,
        'current_page': current_page,
        'total_pages': total_pages,
        'query': query,
        'page_range': range(page_range_start, page_range_end),

    }
    return render(request, 'customapp/search.html', context)



        
def autosuggest(request):
    query = request.GET.get('query_string', '')
    suggestions = []
    current_page = int(request.GET.get('page', 1))
    page_size = 5

    if query:
        search = ProductDocument.search().query("multi_match", query=query, fields=['name', 'main_category', 'sub_category'])
        start_index = (current_page - 1) * page_size
        end_index = current_page * page_size

        search = search[start_index:end_index]
        response = search.execute()
        results = [hit.to_dict() for hit in response]

        for result in results:
            sub_category = result.get('sub_category', '')
            image_url = subcategories_image_urls.get(sub_category, '')
            suggestions.append((result['name'], result['main_category'], image_url))

            print(f"Product: {result['name']}, Main Category: {result['main_category']}, Sub Category: {sub_category}, Image URL: {image_url}")

    total_results = search.count()
    total_pages = (total_results // page_size) + (1 if total_results % page_size > 0 else 0)
    
    return JsonResponse({
        'autocomplete_terms': suggestions,
        'current_page': current_page,
        'total_pages': total_pages,
    })



def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = createuserform()
        customer_form = createcustomerform()
        if request.method == 'POST':
            form = createuserform(request.POST)
            customer_form = createcustomerform(request.POST)
            if form.is_valid() and customer_form.is_valid():
                user = form.save()
                customer = customer_form.save(commit=False)
                customer.user = user
                customer.save()
                return redirect('login')
        context = {
            'form': form,
            'customer_form': customer_form,
        }
        return render(request, 'customapp/register.html', context)

def about_us(request):
    return render(request, 'cu/about_us.html')

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
        context = {}
        return render(request, 'customapp/login.html', context)

def logoutPage(request):
    logout(request)
    return redirect('/')




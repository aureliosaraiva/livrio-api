import urllib2
import urllib
import json
from settings import DEFAULT
from tasks import schedule

def get_location(latitudade, longitude):

    url = "http://maps.googleapis.com/maps/api/geocode/json?latlng={},{}&sensor=false".format(latitudade, longitude)

    response = urllib2.urlopen(url)
    html = response.read()
    data = json.loads(html)

    if 'status' in data and data['status'] == 'OK':

        location = {}

        for i in data['results'][0]['address_components']:
            if 'administrative_area_level_2' in i['types']:
                location['city'] = i['long_name']
            elif 'administrative_area_level_1' in i['types']:
                location['state'] = i['short_name']
                location['state_name'] = i['long_name']
            elif 'country' in i['types']:
                location['country'] = i['long_name']
            elif 'sublocality_level_1' in i['types']:
                location['district'] = i['long_name']
            elif 'route' in i['types']:
                location['route'] = i['long_name']
            elif 'street_number' in i['types']:
                location['number'] = i['long_name']
            elif 'postal_code' in i['types']:
                location['cep'] = i['long_name']


        if 'formatted_address' in data['results'][0]:
            location['address'] = data['results'][0]['formatted_address']


    return location

def book_data(item):
    book = {}
    volume = item['volumeInfo']

    if not 'industryIdentifiers' in volume:
        return False

    for ind in volume['industryIdentifiers']:
        if ind['type'] == 'ISBN_10':
            book['isbn_10'] = ind['identifier']
        elif ind['type'] == 'ISBN_13':
            book['isbn'] = ind['identifier']
        else:
            book['isbn_other'] = ind['identifier']

    if not 'isbn' in book and 'isbn_10' in book:
        book['isbn'] = '978' + book['isbn_10']

    if not 'isbn' in book and 'isbn_other' in book:
        book['isbn'] = book['isbn_other']

    book['origin'] = {'name':'google','id':item['id']}

    if 'title' in volume:
        book['title'] = volume['title']

    if 'subtitle' in volume:
        book['subtitle'] = volume['subtitle']

    if 'authors' in volume:
        book['authors'] = volume['authors']

    if 'publisher' in volume:
        book['publisher'] = volume['publisher']

    if 'publishedDate' in volume:
        book['publishedDate'] = volume['publishedDate']

    if 'pageCount' in volume:
        book['pageCount'] = volume['pageCount']

    if 'categories' in volume:
        book['categories'] = volume['categories']

    if 'language' in volume:
        book['language'] = volume['language']

    if 'description' in volume:
        book['description'] = volume['description']

    if 'imageLinks' in volume and 'thumbnail' in volume['imageLinks']:
        book['cover'] = volume['imageLinks']['thumbnail'].replace('&zoom=1&edge=curl&source=gbs_api','')

    else:
        book['cover'] = DEFAULT['book']

    return book

def search_books(word, offset=0, limit=20):
    
    params = {
        'startIndex': offset,
        'maxResults': limit,
        'q': word,
        'printType': 'books',
        'orderBy': 'newest'
    }
    url = "https://www.googleapis.com/books/v1/volumes?{}".format(urllib.urlencode(params))

    print url
    response = urllib2.urlopen(url)
    html = response.read()
    data = json.loads(html)

    books = []
    if 'items' in data:
        items = data['items']
        for item in items:
            d = book_data(item)
            if d:
                books.append(d)
                #bugfix esta atrasando um pouco o retorno aqui
                schedule.insert_book(d)


    if len(books)>1:
        return books
    elif len(books) == 1 and limit == 1:
        return books[0]
    
    return None



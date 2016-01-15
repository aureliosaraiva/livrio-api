# -*- coding: utf-8 -*-
from bson.objectid import ObjectId
import json
import urllib2
from settings import AWS
import bottlenose
import untangle


def db():
    return app.data.driver.db['isbn']


def find_isbn_google(isbn):
    url = 'https://www.googleapis.com/books/v1/volumes?q=%s' % isbn
    response = urllib2.urlopen(url)
    html = response.read()
    data = json.loads(html)

    if 'totalItems' in data and data['totalItems'] == 0:
        return None

    book = {}

    for item in data['items']:
        volume = item['volumeInfo']

        for ind in volume['industryIdentifiers']:
            if ind['type'] == 'ISBN_10':
                book['isbn'] = ind['identifier']
            elif ind['type'] == 'ISBN_13':
                book['isbn_13'] = ind['identifier']
            else:
                book['isbn_other'] = ind['identifier']

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
            book['cover'] = volume['imageLinks']['thumbnail']

    return book
       

def find_isbn_amazon(isbn):
    amazon = bottlenose.Amazon(AWS['AWS_ACCESS_KEY_ID'], AWS['AWS_SECRET_ACCESS_KEY'], AWS['AWS_ASSOCIATE_TAG'])
    response = amazon.ItemLookup(ItemId=str(isbn), ResponseGroup="Large",
        SearchIndex="Books", IdType="ISBN")
    try:
        xml =  untangle.parse(response)

        item = xml.ItemLookupResponse.Items.Item
        aa = item.ItemAttributes

        book = {}

        book['origin'] = {'name':'amazon','id':item.ASIN.cdata}

        if hasattr(aa,'EAN'):
            book['isbn'] = aa.EAN.cdata

        if hasattr(aa,'ISBN'):
            book['isbn_10'] = aa.ISBN.cdata

        if hasattr(aa,'Title'):
            book['title'] = aa.Title.cdata

        if hasattr(aa,'Publisher'):
            book['publisher'] = aa.Publisher.cdata

        if hasattr(aa,'publishedDate'):
            book['publishedDate'] = aa.publishedDate.cdata

        if hasattr(aa,'NumberOfPages'):
            book['pageCount'] = aa.NumberOfPages.cdata

        if hasattr(aa,'NumberOfPages'):
            book['Edition'] = aa.NumberOfPages.cdata

        try:
            book['description'] = item.EditorialReviews.EditorialReview.Content.cdata
        except:
            pass

        try:
            book['categories'] = [item.BrowseNodes.BrowseNode.Name.cdata]
        except:
            pass

        try:
            book['cover'] = item.ImageSets.ImageSet.LargeImage.URL.cdata
        except:
            pass

        return book
    except:
        return None
        



    

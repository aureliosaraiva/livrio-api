# -*- coding: utf-8 -*-
from bson.objectid import ObjectId
import json
import urllib2
from settings import AWS
import bottlenose
import untangle


def db():
    return app.data.driver.db['isbn']


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

            if not book['title'].find('36x24inch') == -1:
                return None

            if not book['title'].find('32x24inch') == -1:
                return None

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
            book['cover'] = item.LargeImage.URL.cdata
        except Exception, e:
            pass

        return book
    except:
        return None
        

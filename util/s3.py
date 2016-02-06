#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import urllib2
import boto
import cStringIO
from boto.s3.key import Key

def to_url(bucket, key):
    return 'https://s3-sa-east-1.amazonaws.com/'+ str(bucket) +'/' + str(key)


def download_file_from_url(url):
    opener = urllib2.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36')]
    response = opener.open(url)
    info = response.info()
    return {
        'body': response.read(),
        'type': info.getheader('Content-Type'),
        'length': int(info.getheader('Content-Length'))
    }

def upload_from_file(filename, key, bucket='livrio',callback=None, md5=None, reduced_redundancy=False, content_type=None):
    file =open(filename,'r')
    try:
        size = os.fstat(file.fileno()).st_size
    except:
        file.seek(0, os.SEEK_END)
        size = file.tell()

    conn = boto.connect_s3()
    bucket = conn.get_bucket(bucket, validate=True)
    k = Key(bucket)
    k.key = key

    if content_type:
        k.set_metadata('Content-Type', content_type)
    sent = k.set_contents_from_file(file, cb=callback, md5=md5, reduced_redundancy=reduced_redundancy, rewind=True)
    k.make_public()
    # Rewind for later use
    file.seek(0)

    if sent == size:
        return to_url('livrio', key)
    return False

def upload_from_url(url, key, bucket='livrio',callback=None, md5=None, reduced_redundancy=False, content_type=None):

    file = download_file_from_url(url)

    conn = boto.connect_s3()
    bucket = conn.get_bucket(bucket, validate=True)
    k = Key(bucket)
    k.key = key
    k.set_metadata('Content-Type', file['type'])

    sent = k.set_contents_from_string(file['body'], cb=callback, md5=md5, reduced_redundancy=reduced_redundancy)
    k.make_public()


    if sent == file['length']:
        return to_url('livrio', key)
    return False

def upload_from_string(file, key, bucket='livrio',content_type=None, callback=None, md5=None, reduced_redundancy=False):


    conn = boto.connect_s3()
    bucket = conn.get_bucket(bucket, validate=True)
    k = Key(bucket)
    k.key = key

    if content_type:
        k.set_metadata('Content-Type', content_type)

    sent = k.set_contents_from_string(file, cb=callback, md5=md5, reduced_redundancy=reduced_redundancy)
    k.make_public()


    # if sent == file['length']:
    return to_url('livrio', key)
    # return False
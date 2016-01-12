#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..checkmailing.tasks import check_syntax

line_data = {'import_id':'1234', 'collection_name':'123', 'email':'aurelio@codeway.com.br', 'line':[], 'deliverability':True}
check_syntax.process_check_syntax.apply_async([line_data])

"""
from __future__ import absolute_import
from __future__ import unicode_literals

from tasks import check_file
from settings import db


document_id = db.process.insert_one({
    'filename':'_files/test.csv',
    'delimiter': ",",
    'quotechar': '"',
    'column': 0,
    'deliverability': True
}).inserted_id


check_file.process_check_file.apply_async([str(document_id)])
print str(document_id)

"""
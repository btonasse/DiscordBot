from rest_framework import pagination
from rest_framework.response import Response
from typing import OrderedDict

class MyPageNumberPagination(pagination.PageNumberPagination):
    '''
    Overrides the useless DRF pagination class
    '''
    page_size = 50
    def get_paginated_response(self, data):
        if self.page.has_next():
            next_page = self.page.number + 1
        else:
            next_page = None
        if self.page.has_previous():
            previous_page = self.page.number - 1
        else:
            previous_page = None
        
        return Response(OrderedDict([
            ('current_page', self.page.number),
            ('last_page', self.page.paginator.num_pages),
            ('page_size', self.page_size),
            ('total_items', self.page.paginator.count),
            ('next_page', next_page),
            ('previous_page', previous_page),
            ('results', data)
        ]))

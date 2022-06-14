from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class NotificationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 10000

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'limit': self.page.paginator.per_page,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })
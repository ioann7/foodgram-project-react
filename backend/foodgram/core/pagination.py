from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class LimitPagionation(PageNumberPagination):
    max_page_size = settings.MAX_PAGE_SIZE_PAGINATION
    page_size_query_param = 'limit'
    page_size = settings.DEFAULT_PAGE_SIZE_PAGINATION

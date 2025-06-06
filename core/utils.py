from rest_framework.pagination import PageNumberPagination


class TenPerPagePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"  # optional: allow client to override up to a max
    max_page_size = 100
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ProductPagination(PageNumberPagination):
    page_size = 3
    page_query_param = 'pagina'
    page_size_query_param = 'por_pagina'
    max_page_size = 20
    last_page_strings = ('ultima',)
    invalid_page_message = 'La página que buscas no existe.'

    def get_paginated_response(self, data):
        return Response({
            'total': self.page.paginator.count,
            'pagina_actual': self.page.number,
            'total_paginas': self.page.paginator.num_pages,
            'siguiente': self.get_next_link(),
            'anterior': self.get_previous_link(),
            'resultados': data,
        })


class UserPagination(ProductPagination):
    page_size = 10

from django.shortcuts import render
from rest_framework import views
from rest_framework.response import Response

from rossvyaz.info import get_num_info


def search(request):
    context = dict()
    params = request.POST or request.GET
    try:
        context['result'] = get_num_info(params.get('num'))
    except Exception as e:
        context['error_message'] = str(e)

    return context


class SearchAPI(views.APIView):
    def get(self, request):
        return Response(search(request))


def search_view(request):
    return render(request, 'rossvyaz/search.html', search(request))

from django.http import Http404
from django.shortcuts import render
from rest_framework import permissions
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import BookTitle


# Create your views here.
from .serializers import BookTitleSerializer


class InputView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        book_id = request.query_params.get('id', None)
        if book_id is None:
            return Response("Något vettigt felmeddelande", status=status.HTTP_400_BAD_REQUEST)

        q = BookTitle.objects.filter(pk=book_id).first()

        serializer = BookTitleSerializer(q, many=False)
        return Response(serializer.data)

    def post(self, request, format=None):
        book_title = BookTitleSerializer(data=request.data)
        if not book_title.is_valid():
            return Response(book_title.errors, status=status.HTTP_400_BAD_REQUEST)
        book_title.save()
        return Response(book_title.data)




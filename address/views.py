from functools import partial
from django.shortcuts import render
from rest_framework import exceptions, generics, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from address.serializers import AddressSerializer
from authorization.authentication import JWTAuthentication
from core.models import Address

class AddressAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, _):
        address = Address.objects.all()
        return Response(AddressSerializer(address, many=True).data)

class AddressDetailAPIView(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    """
    POST   /api/address/      → create (409 if already exists)
    GET    /api/address/      → retrieve (404 if none)
    PUT    /api/address/      → update existing (404 if none)
    DELETE /api/address/      → delete   (404 if none)
    """
    serializer_class = AddressSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # only one address per user
        try:
            return Address.objects.get(user=self.request.user)
        except Address.DoesNotExist:
            raise exceptions.NotFound({"message": "Address not found"})

    def perform_create(self, serializer):
        # attach the logged‑in user
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        # conflict if already have one
        if Address.objects.filter(user=request.user).exists():
            return Response(
                {"message": "Address already exists"},
                status=status.HTTP_409_CONFLICT
            )
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        response.status_code = status.HTTP_202_ACCEPTED
        return response

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

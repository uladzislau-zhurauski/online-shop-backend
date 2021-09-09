from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.controllers.image import ImageController
from shop.serializers.image import ImageInputSerializer, ImageOutputSerializer


class ImageView(APIView):
    permission_classes = [IsAdminUser]

    @classmethod
    def get(cls, request, pk=None):
        if pk is None:
            images = ImageController.get_image_list()
            data = ImageOutputSerializer(instance=images, many=True).data
        else:
            image = ImageController.get_image(pk)
            data = ImageOutputSerializer(instance=image).data

        return Response(data, status.HTTP_200_OK)

    @classmethod
    def post(cls, request):
        serializer = ImageInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ImageController.create_image(**serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)

    @classmethod
    def put(cls, request, pk):
        serializer = ImageInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ImageController.update_image(pk, **serializer.validated_data)

        return Response(status=status.HTTP_200_OK)

    @classmethod
    def delete(cls, request, pk):
        ImageController.delete_image(pk)

        return Response(status=status.HTTP_204_NO_CONTENT)

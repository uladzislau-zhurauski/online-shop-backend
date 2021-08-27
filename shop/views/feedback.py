from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.controllers.feedback import FeedbackController
from shop.permissions import is_owner_or_admin_factory, check_permissions
from shop.serializers.feedback import FeedbackDetailSerializer, FeedbackInputSerializer, FeedbackListSerializer


class FeedbackList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @classmethod
    def get(cls, request):
        feedback = FeedbackController.get_feedback_list()
        data = FeedbackListSerializer(instance=feedback, many=True).data

        return Response(data, status.HTTP_200_OK)

    @classmethod
    def post(cls, request):
        serializer = FeedbackInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data.pop('images_to_delete', None)
        FeedbackController.create_feedback(request.user, **serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)


class FeedbackDetail(APIView):
    permission_classes = [is_owner_or_admin_factory('author')]

    @classmethod
    def get(cls, request, pk):
        feedback = FeedbackController.get_feedback(pk)
        data = FeedbackDetailSerializer(instance=feedback).data

        return Response(data, status.HTTP_200_OK)

    @check_permissions(FeedbackController.get_feedback)
    def put(self, request, pk):
        serializer = FeedbackInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        FeedbackController.update_feedback(pk, **serializer.validated_data)

        return Response(status=status.HTTP_200_OK)

    @check_permissions(FeedbackController.get_feedback)
    def delete(self, request, pk):
        FeedbackController.delete_feedback(pk)

        return Response(status=status.HTTP_204_NO_CONTENT)


class FeedbackImagesRemover(APIView):
    permission_classes = [is_owner_or_admin_factory('author')]

    @check_permissions(FeedbackController.get_feedback)
    def get(self, request, pk):
        FeedbackController.delete_feedback_images(pk)

        return Response(status=status.HTTP_204_NO_CONTENT)

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.controllers.feedback import FeedbackController
from shop.permissions import IsOwnerOrSuperuserOrReadOnly
from shop.serializers.feedback import FeedbackListSerializer, FeedbackDetailSerializer, FeedbackInputSerializer


class FeedbackList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @classmethod
    def get(cls, request):
        feedback = FeedbackController.get_feedback_list()

        data = FeedbackListSerializer(instance=feedback, many=True, context={'request': request}).data

        return Response(data)

    @classmethod
    def post(cls, request):
        serializer = FeedbackInputSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        FeedbackController.create_feedback(request.user, **serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)


class FeedbackDetail(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrSuperuserOrReadOnly]

    @classmethod
    def get(cls, request, pk):
        feedback = FeedbackController.get_feedback(pk)

        data = FeedbackDetailSerializer(instance=feedback, context={'request': request}).data

        return Response(data)

    @classmethod
    def put(cls, request, pk):
        serializer = FeedbackInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        FeedbackController.update_feedback(pk, **serializer.validated_data)

        data = FeedbackDetailSerializer(instance=FeedbackController.get_feedback(pk)).data
        return Response(data)

    @classmethod
    def delete(cls, request, pk):
        FeedbackController.delete_feedback(pk)

        return Response(status=status.HTTP_204_NO_CONTENT)

from functools import wraps

from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.controllers.feedback import FeedbackController
from shop.permissions import IsOwnerOrAdmin
from shop.serializers.feedback import FeedbackListSerializer, FeedbackDetailSerializer, FeedbackInputSerializer


class FeedbackList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

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


def check_permissions(get_object_func):
    def check_permissions_decorator(http_method):
        @wraps(http_method)
        def wrapper(self, *method_args, **method_kwargs):
            request, pk = method_args[0], method_kwargs['pk']
            self.check_object_permissions(request, get_object_func(pk))
            return http_method(self, *method_args, **method_kwargs)
        return wrapper
    return check_permissions_decorator


class FeedbackDetail(APIView):
    permission_classes = [IsOwnerOrAdmin]

    @classmethod
    def get(cls, request, pk):
        feedback = FeedbackController.get_feedback(pk)
        data = FeedbackDetailSerializer(instance=feedback, context={'request': request}).data

        return Response(data)

    @check_permissions(FeedbackController.get_feedback)
    def put(self, request, pk):
        serializer = FeedbackInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        FeedbackController.update_feedback(pk, **serializer.validated_data)
        data = FeedbackDetailSerializer(instance=FeedbackController.get_feedback(pk)).data

        return Response(data)

    @check_permissions(FeedbackController.get_feedback)
    def delete(self, request, pk):
        FeedbackController.delete_feedback(pk)

        return Response(status=status.HTTP_204_NO_CONTENT)

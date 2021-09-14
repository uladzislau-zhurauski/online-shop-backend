from django.contrib.auth import get_user_model
from rest_framework import serializers

from shop.serializers import DynamicFieldsModelSerializer
from shop.serializers.address import AddressOutputSerializer
from shop.serializers.feedback import FeedbackOutputSerializer
from shop.serializers.order import OrderOutputSerializer


class UserOutputSerializer(DynamicFieldsModelSerializer):
    addresses = AddressOutputSerializer(many=True, fields_to_remove=['user'])
    feedback = FeedbackOutputSerializer(many=True, fields_to_remove=['author'])
    orders = OrderOutputSerializer(many=True, fields_to_remove=['user'])

    class Meta:
        model = get_user_model()
        fields = ('addresses', 'feedback', 'orders', 'phone_number', 'username', 'first_name', 'last_name', 'email',
                  'is_staff', 'is_superuser', 'is_active', 'password')


class UserInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('phone_number', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser',
                  'is_active', 'password')
        extra_kwargs = {'phone_number': {'required': False}}

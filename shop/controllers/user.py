from django.contrib.auth import get_user_model
from django.http import Http404
from rest_framework import serializers
from rest_framework.settings import api_settings
from rest_framework.validators import UniqueValidator

from shop.dal.user import UserDAL


class UserController:
    @classmethod
    def get_user_list(cls):
        return UserDAL.get_all_users()

    @classmethod
    def create_user(cls, user, username, is_staff, is_superuser, is_active, password, phone_number='', first_name='',
                    last_name='', email=''):
        is_staff, is_superuser, is_active = cls.compute_superuser_settings(user, is_staff, is_superuser, is_active)
        UserDAL.insert_user(username, is_staff, is_superuser, is_active, password, phone_number, first_name, last_name,
                            email)

    @classmethod
    def get_user(cls, user_pk):
        try:
            return UserDAL.get_user_by_pk(user_pk)
        except get_user_model().DoesNotExist:
            raise Http404

    @classmethod
    def update_user(cls, user_pk, user, username, is_staff, is_superuser, is_active, password, phone_number='',
                    first_name='', last_name='', email=''):
        is_staff, is_superuser, is_active = cls.compute_superuser_settings(user, is_staff, is_superuser, is_active)
        UserDAL.update_user(cls.get_user(user_pk), username, is_staff, is_superuser, is_active, password, phone_number,
                            first_name, last_name, email)

    @classmethod
    def delete_user(cls, user_pk):
        UserDAL.delete_user(cls.get_user(user_pk))

    @classmethod
    def check_username_field(cls, user_pk, serializer):
        username = serializer.initial_data.get('username', None)
        if cls.get_user(user_pk).username == username:
            cls.remove_username_unique_validator(serializer.fields)

    @classmethod
    def remove_username_unique_validator(cls, fields):
        username_validators = fields.get('username').validators
        for validator in username_validators:
            if isinstance(validator, UniqueValidator):
                username_validators.remove(validator)
                break

    @classmethod
    def compute_superuser_settings(cls, user, is_staff, is_superuser, is_active):
        if user.is_staff:
            cls.validate_superuser_settings(is_staff, is_superuser)
        else:
            is_staff = is_superuser = False
            is_active = True
        return is_staff, is_superuser, is_active

    @classmethod
    def validate_superuser_settings(cls, is_staff, is_superuser):
        if is_superuser is True and is_staff is not True:
            raise serializers.ValidationError({api_settings.NON_FIELD_ERRORS_KEY: 'Superuser must have is_staff=True.'})

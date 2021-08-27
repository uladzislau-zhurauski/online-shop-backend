from django.http import Http404
from rest_framework import serializers

from shop.dal.address import AddressDAL
from shop.models import Address


class AddressController:
    @classmethod
    def get_address_list(cls, user):
        if user.is_staff:
            return AddressDAL.get_all_addresses()
        else:
            return AddressDAL.get_user_addresses(user.pk)

    @classmethod
    def create_address(cls, user, country, region, city, street, house_number, flat_number, postal_code):
        AddressDAL.insert_address(user, country, region, city, street, house_number, flat_number, postal_code)

    @classmethod
    def get_address(cls, address_pk):
        try:
            return AddressDAL.get_address_by_pk(address_pk)
        except Address.DoesNotExist:
            raise Http404

    @classmethod
    def update_address(cls, address_pk, country, region, city, street, house_number, flat_number, postal_code):
        address_obj = cls.get_address(address_pk)
        AddressDAL.update_address(address_obj, country, region, city, street, house_number, flat_number, postal_code)

    @classmethod
    def delete_address(cls, address_pk):
        AddressDAL.delete_address(cls.get_address(address_pk))

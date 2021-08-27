from shop.models import Address


class AddressDAL:
    @classmethod
    def insert_address(cls, user, country, region, city, street, house_number, flat_number, postal_code):
        return Address.objects.create(user=user, country=country, region=region, city=city, street=street,
                                      house_number=house_number, flat_number=flat_number, postal_code=postal_code)

    @classmethod
    def get_all_addresses(cls):
        return Address.objects.all()

    @classmethod
    def get_user_addresses(cls, user_pk):
        return Address.objects.filter(user_id=user_pk)

    @classmethod
    def get_address_by_pk(cls, address_pk):
        return Address.objects.get(pk=address_pk)

    @classmethod
    def update_address(cls, address_obj: Address, country, region, city, street, house_number, flat_number,
                       postal_code):
        address_obj.country = country
        address_obj.region = region
        address_obj.city = city
        address_obj.street = street
        address_obj.house_number = house_number
        address_obj.flat_number = flat_number
        address_obj.postal_code = postal_code
        return address_obj.save()

    @classmethod
    def delete_address(cls, address):
        return address.delete()

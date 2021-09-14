from django.contrib.auth import get_user_model


class UserDAL:
    @classmethod
    def insert_user(cls, username, is_staff, is_superuser, is_active, password, phone_number, first_name,
                    last_name, email):
        return get_user_model().objects.create(username=username, phone_number=phone_number, first_name=first_name,
                                               last_name=last_name, email=email, is_staff=is_staff,
                                               is_superuser=is_superuser, is_active=is_active, password=password)

    @classmethod
    def get_all_users(cls):
        return get_user_model().objects.all()

    @classmethod
    def get_user_by_pk(cls, user_pk):
        return get_user_model().objects.get(pk=user_pk)

    @classmethod
    def update_user(cls, user_obj, username, is_staff, is_superuser, is_active, password, phone_number,
                    first_name, last_name, email):
        user_obj.phone_number = phone_number
        user_obj.username = username
        user_obj.first_name = first_name
        user_obj.last_name = last_name
        user_obj.email = email
        user_obj.is_staff = is_staff
        user_obj.is_superuser = is_superuser
        user_obj.is_active = is_active
        user_obj.password = password
        return user_obj.save()

    @classmethod
    def delete_user(cls, user):
        return user.delete()

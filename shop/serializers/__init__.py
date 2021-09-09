from rest_framework import serializers


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields_to_remove = kwargs.pop('fields_to_remove', None)
        super().__init__(*args, **kwargs)

        if fields_to_remove is not None:
            for field_name in fields_to_remove:
                self.fields.pop(field_name)

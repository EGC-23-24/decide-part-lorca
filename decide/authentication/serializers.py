from rest_framework import serializers

from django.contrib.auth.models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer class for User model.

    Serializes User instances to JSON data and vice versa.

    Attributes:
        model: The User model to be serialized.
        fields: The fields to include in the serialized data.
    """
    class Meta:
        """
        Meta class for UserSerializer.

        Defines metadata options for the serializer.

        Attributes:
            model: The User model to be serialized.
            fields: The fields to include in the serialized data.
        """
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff')

from attendance.models import Parent, LostKid, VerifyRequest, Kid
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'password')
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username', 'email']
            )
        ]


class ParentSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Parent
        fields = ('user', 'phone_number')

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        parent, created = Parent.objects.update_or_create(user=user,
                                                          phone_number=validated_data.pop('phone_number'))
        return parent


class LostKidSerializer(serializers.ModelSerializer):

    class Meta:
        model = LostKid
        fields = ('name', 'photo', 'state', 'description', 'email', 'phone_number')


class VerifyKidSerializer(serializers.ModelSerializer):

    class Meta:
        model = VerifyRequest
        fields = ('photo', 'location')


class KidSerializer(serializers.ModelSerializer):

    flag = serializers.BooleanField(default=False)

    class Meta:
        model = Kid
        fields = ('name', 'photo_id', 'description', 'state', 'flag')

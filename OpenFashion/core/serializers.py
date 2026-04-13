from django.shortcuts import render
from rest_framework.serializers import LoginSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

class CutsomLoginSerializer(LoginSerializer):
    username = None
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        user = authenticate(
            request=self.context.get("request"),
            username=email,   # trick: backend will map email
            password=password
        )
        
        if not user:
            raise serializers.ValidationError("Invalid email or password")

        attrs['user'] = user
        return attrs

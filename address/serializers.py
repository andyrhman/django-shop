from rest_framework import serializers

from core.models import Address, User

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'fullName', 'email', 'username', 'password', 'is_user', 'is_verified', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }    
          
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        
        # Convert email and username to lowercase
        email = validated_data.get('email', '').lower()
        username = validated_data.get('username', '').lower()
        
        # Update the dictionary with lowercase values
        validated_data['email'] = email
        validated_data['username'] = username

        instance = self.Meta.model(**validated_data)
        
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class AddressSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Address
        fields = "__all__"
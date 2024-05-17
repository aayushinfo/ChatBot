from rest_framework import serializers
from chatapp.models import CustomUser, Messages
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'name', 'phone_number', 'user_status', 'updated_at', 'deleted_at', 'password', 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password and Confirm Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = CustomUser(
            name=validated_data['name'],
            email=validated_data['email'],
            first_name='',
            last_name='',
            username=validated_data['email'],
            date_joined=timezone.now()
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = ['id', 'sender_user', 'receiver_user', 'message', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, attrs):
        sender_user = attrs.get('sender_user').id
        receiver_user = attrs.get('receiver_user').id

        if sender_user == receiver_user:
            raise serializers.ValidationError("sender and receiver cannot be the same user please check.")

        if not isinstance(sender_user, int):
            raise serializers.ValidationError("Sender user id must be an integer.")
        if not isinstance(receiver_user, int):
            raise serializers.ValidationError("Receiver user id must be an integer.")

        try:
            CustomUser.objects.get(pk=sender_user)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Sender user not exist.")

        try:
            CustomUser.objects.get(pk=receiver_user)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Receiver user not exist.")

        replies_message = attrs.get('replies_message')
        if replies_message is not None:
            if not Messages.objects.filter(id=replies_message.id).exists():
                raise serializers.ValidationError("Replies message not exist.")

        return attrs


class AutoMessageSerializer(serializers.ModelSerializer):
    send_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Messages
        fields = ['id', 'sender_user', 'receiver_user', 'message', 'created_at', 'updated_at', 'send_time']
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, attrs):
        sender_user = attrs.get('sender_user').id
        receiver_user = attrs.get('receiver_user').id

        if sender_user == receiver_user:
            raise serializers.ValidationError("Sender and receiver cannot be the same user.")

        if not isinstance(sender_user, int):
            raise serializers.ValidationError("Sender user id must be an integer.")
        if not isinstance(receiver_user, int):
            raise serializers.ValidationError("Receiver user id must be an integer.")

        try:
            CustomUser.objects.get(pk=sender_user)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Sender user does not exist.")

        try:
            CustomUser.objects.get(pk=receiver_user)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Receiver user does not exist.")

        replies_message = attrs.get('replies_message')
        if replies_message is not None:
            if not Messages.objects.filter(id=replies_message.id).exists():
                raise serializers.ValidationError("Replies message does not exist.")

        return attrs
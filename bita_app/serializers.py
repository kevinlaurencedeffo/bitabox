from rest_framework import serializers
from django.contrib.auth.hashers import check_password
from .models import *


# Sérialiseur d'inscription
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = BitaBoxUtilisateur
        fields = ["id", "username", "email", "password", "is_commercial","is_admin","enterprise"]

    def create(self, validated_data):
        user = BitaBoxUtilisateur.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            is_commercial=validated_data.get("is_commercial", False),
            is_admin=validated_data.get("is_admin", False),
        )
        return user

# Sérialiseur de connexion
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        try:
            user = BitaBoxUtilisateur.objects.get(username=username)
        except BitaBoxUtilisateur.DoesNotExist:
            raise serializers.ValidationError("Identifiants invalides.")

        if not user.check_password(password):
            raise serializers.ValidationError("Mot de passe incorrect.")

        return user  # ✅ Retourner l'utilisateur validé



class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = BitaBoxUtilisateur
        fields = "__all__"


class EntrepriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BitaBoxEntreprise
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BitaboxComment
        fields = "__all__"


class LeadSerializer(serializers.ModelSerializer):
    date = serializers.DateField(read_only=True)
    time = serializers.TimeField(read_only=True)
    comments = serializers.PrimaryKeyRelatedField(
        queryset=BitaboxComment.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = BitaBoxLead
        fields = "__all__"
        read_only_fields = ['enterprise', 'commercial', 'author', 'date', 'time', 'id_lead']



class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BitaBoxNotification
        fields = ['id', 'user', 'event_type', 'message', 'status', 'created_at']


from .models import *
from .serializers import *
from rest_framework import status, generics, permissions,viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password


# Inscription
class RegisterView(generics.CreateAPIView):
    queryset = BitaBoxUtilisateur.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

# Connexion (Renvoie un token JWT)
class LoginView(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data  # ✅ On récupère l'utilisateur
            refresh = RefreshToken.for_user(user)
            return Response({
                "user_id": user.id,  # ✅ On envoie bien un entier
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Infos utilisateur connecté
class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        serializer = UtilisateurSerializer(request.user)
        return Response(serializer.data)

class UtilisateursParEntrepriseView(generics.ListAPIView):
    serializer_class = UtilisateurSerializer
    permission_classes = [permissions.IsAuthenticated]  # Seuls les utilisateurs connectés peuvent accéder

    def get_queryset(self):
        entreprise_id = self.kwargs.get("entreprise_id")
        return BitaBoxUtilisateur.objects.filter(entreprise=entreprise_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        entreprise = BitaBoxEntreprise.objects.get(id=self.kwargs["entreprise_id"])
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "entreprise": entreprise.nom,
            "utilisateurs": serializer.data
        })

class ListeUtilisateursView(generics.ListAPIView):
    """Liste tous les utilisateurs"""
    queryset = BitaBoxUtilisateur.objects.all()
    serializer_class = UtilisateurSerializer
    permission_classes = [permissions.IsAuthenticated]

class CreerUtilisateurView(generics.CreateAPIView):
    """Créer un nouvel utilisateur"""
    serializer_class = UtilisateurSerializer
    permission_classes = [permissions.IsAdminUser]  # Seuls les admins peuvent créer des utilisateurs

    def perform_create(self, serializer):
        password = serializer.validated_data.get("password")
        serializer.save(password=make_password(password))  # Hash du mot de passe

class DetailUtilisateurView(generics.RetrieveUpdateDestroyAPIView):
    """Voir, mettre à jour ou supprimer un utilisateur"""
    queryset = BitaBoxUtilisateur.objects.all()
    serializer_class = UtilisateurSerializer
    permission_classes = [permissions.IsAdminUser]  # Seuls les admins peuvent modifier/supprimer

class ChangePasswordView(APIView):
    """Changer le mot de passe d'un utilisateur"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        new_password = request.data.get("new_password")

        if not new_password:
            return Response({"error": "Le mot de passe est requis"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Mot de passe mis à jour avec succès"}, status=status.HTTP_200_OK)

# 🏢 Gestion des entreprises
class EntrepriseListCreateView(generics.ListCreateAPIView):
    queryset = BitaBoxEntreprise.objects.all()
    serializer_class = EntrepriseSerializer
    permission_classes = [permissions.IsAuthenticated]  # 🔒 Auth obligatoire

class EntrepriseRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BitaBoxEntreprise.objects.all()
    serializer_class = EntrepriseSerializer
    permission_classes = [permissions.IsAuthenticated]  # 🔒 Auth obligatoire

# 🎯 Gestion des leads
class LeadListCreateView(generics.ListCreateAPIView):
    queryset = BitaBoxLead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated]  # 🔒 Auth obligatoire

class LeadRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BitaBoxLead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated]  # 🔒 Auth obligatoire

class LeadByCommercialView(generics.ListAPIView):
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated]  # Seuls les utilisateurs connectés peuvent voir les leads

    def get_queryset(self):
        # Récupérer l'utilisateur connecté (commercial)
        return BitaBoxLead.objects.filter(commercial=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"commercial": request.user.username, "leads": serializer.data})

class LeadByEntrepriseView(generics.ListAPIView):
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated]  # Seuls les utilisateurs connectés peuvent voir les leads

    def get_queryset(self):
        entreprise_id = self.kwargs.get("entreprise_id")  # Récupérer l'ID de l'entreprise depuis l'URL
        return BitaBoxLead.objects.filter(entreprise_id=entreprise_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        entreprise = BitaBoxEntreprise.objects.get(id=self.kwargs["entreprise_id"])
        serializer = self.get_serializer(queryset, many=True)
        return Response({"entreprise": entreprise.nom, "leads": serializer.data})

# 📩 Liste des notifications de l'utilisateur connecté
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BitaBoxNotification.objects.filter(user=self.request.user).order_by('-created_at')

# ✅ Marquer une notification comme lue
class MarkNotificationAsReadView(generics.UpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BitaBoxNotification.objects.filter(user=self.request.user, status='unread')

    def perform_update(self, serializer):
        serializer.save(status='read')

# ❌ Supprimer une notification
class NotificationDeleteView(generics.DestroyAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BitaBoxNotification.objects.filter(user=self.request.user)
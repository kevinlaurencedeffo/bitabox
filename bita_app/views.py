from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
from rest_framework import status, generics, permissions,viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from deep_translator import GoogleTranslator
from django.db.models import Count,Q
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model


User = get_user_model()


class TraductionAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request, langue_source, langue_cible):
        mot = request.data.get('mot')

        if not mot:
            return Response({"error": "Le champ 'mot' est requis."}, status=status.HTTP_400_BAD_REQUEST)

        if langue_source == langue_cible:
            return Response({"error": "Les langues source et cible doivent être différentes."}, status=400)

        try:
            traduction = GoogleTranslator(source=langue_source, target=langue_cible).translate(mot)

            return Response({
                "original": mot,
                "langue_source": langue_source,
                "langue_cible": langue_cible,
                "traduction": traduction
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class IsAdminOrSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_admin or request.user.is_superuser)


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
        entreprise_id = self.kwargs.get("enterprise")
        return BitaBoxUtilisateur.objects.filter(enterprise=entreprise_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        entreprise = BitaBoxEntreprise.objects.get(id=self.kwargs["enterprise"])
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "enterprise": entreprise.name,
            "utilisateurs": serializer.data
        })

class ListeUtilisateursView(generics.ListAPIView):
    """Liste tous les utilisateurs"""
    queryset = BitaBoxUtilisateur.objects.all()
    serializer_class = UtilisateurSerializer
    permission_classes = [IsAdminOrSuperuser]

class CreerUtilisateurView(generics.CreateAPIView):
    """Créer un nouvel utilisateur"""
    serializer_class = UtilisateurSerializer
    permission_classes = [IsAdminOrSuperuser]  # Seuls les admins peuvent créer des utilisateurs

    def perform_create(self, serializer):
        password = serializer.validated_data.get("password")
        serializer.save(password=make_password(password))  # Hash du mot de passe

class DetailUtilisateurView(generics.RetrieveUpdateDestroyAPIView):
    """
    Voir, mettre à jour ou supprimer un utilisateur.
    Si un champ 'password' est envoyé, le mot de passe est mis à jour.
    """
    queryset = BitaBoxUtilisateur.objects.all()
    serializer_class = UtilisateurSerializer
    permission_classes = [IsAdminOrSuperuser]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Vérifie s'il y a un mot de passe à mettre à jour
        password = request.data.get("password", None)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # Mise à jour du mot de passe si présent
        if password:
            instance.set_password(password)
            instance.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

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
    permission_classes = [IsAdminOrSuperuser]  # 🔒 Auth obligatoire

class EntrepriseRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BitaBoxEntreprise.objects.all()
    serializer_class = EntrepriseSerializer
    permission_classes = [IsAdminOrSuperuser]  # 🔒 Auth obligatoire

# 🎯 Gestion des leads
class LeadListCreateView(generics.ListCreateAPIView):
    queryset = BitaBoxLead.objects.all().order_by('-date')
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated]  # 🔒 Auth obligatoire

class LeadRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BitaBoxLead.objects.all().order_by('-date')
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
        entreprise_id = self.kwargs.get("enterprise")  # Récupérer l'ID de l'entreprise depuis l'URL
        return BitaBoxLead.objects.filter(enterprise=entreprise_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        entreprise = BitaBoxEntreprise.objects.get(id=self.kwargs["enterprise"])
        serializer = self.get_serializer(queryset, many=True)
        return Response({"enterprise": entreprise.name, "leads": serializer.data})

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
    


class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        stats = {}

        # Superadmin : accès global
        if user.is_superuser:
            entreprises_count = BitaBoxEntreprise.objects.count()
            utilisateurs_count = BitaBoxUtilisateur.objects.count()
            leads_count = BitaBoxLead.objects.count()
            leads_by_status = BitaBoxLead.objects.values('status').annotate(count=Count('id'))
            top_entreprises = BitaBoxEntreprise.objects.annotate(lead_count=Count('leads')).order_by('-lead_count')[:5]
            notifications_count = BitaBoxNotification.objects.count()

            stats = {
                'entreprises_count': entreprises_count,
                'utilisateurs_count': utilisateurs_count,
                'leads_count': leads_count,
                'leads_by_status': list(leads_by_status),
                'top_entreprises': list(top_entreprises.values('name', 'lead_count')),
                'notifications_count': notifications_count
            }

        # Admin entreprise : stats liées à son entreprise
        elif user.is_admin:
            entreprise = user.enterprise
            leads = BitaBoxLead.objects.filter(enterprise=entreprise)
            leads_by_status = leads.values('status').annotate(count=Count('id'))
            leads_by_commercial = leads.values('commercial').annotate(count=Count('id'))
            recent_leads = leads.order_by('-date')[:5]

            total_leads = leads.count()
            total_commercials = BitaBoxUtilisateur.objects.filter(enterprise=entreprise, is_commercial=True).count()
            total_leads_converted = leads.filter(status="converted").count()
            total_leads_lost = leads.filter(status="lost_lead").count()

            top_commercials = leads.values('commercial').annotate(count=Count('id')).order_by('-count')[:5]

            stats = {
                'total_leads': total_leads,
                'total_commercials': total_commercials,
                'total_leads_converted': total_leads_converted,
                'total_leads_lost': total_leads_lost,
                'leads_by_status': list(leads_by_status),
                'leads_by_commercial': list(leads_by_commercial),
                'top_commercials': list(top_commercials),
                'recent_leads': [{'name': lead.name, 'surname': lead.surname, 'status': lead.status} for lead in recent_leads]
            }

        # Commercial : accès à ses propres leads
        elif user.is_commercial:
            leads = BitaBoxLead.objects.filter(commercial=user)
            leads_by_status = leads.values('status').annotate(count=Count('id'))
            converted = leads.filter(status="converted").count()
            lost = leads.filter(status="lost_lead").count()
            total_leads = leads.count()
            conversion_rate = self.get_conversion_rate(user)
            leads_to_follow_up = leads.filter(status="call_back").order_by('-date')[:5]

            stats = {
                'total_leads': total_leads,
                'total_leads_converted': converted,
                'total_leads_lost': lost,
                'conversion_rate': conversion_rate,
                'leads_by_status': list(leads_by_status),
                'leads_to_follow_up': [{'name': lead.name, 'surname': lead.surname, 'contact': lead.contact} for lead in leads_to_follow_up]
            }

        return Response(stats)

    def get_conversion_rate(self, commercial):
        total_leads = BitaBoxLead.objects.filter(commercial=commercial).count()
        converted_leads = BitaBoxLead.objects.filter(commercial=commercial, status="converted").count()

        if total_leads > 0:
            return (converted_leads / total_leads) * 100
        return 0
    


class AddLeadView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, enterprise_id, commercial_id):
        try:
            entreprise = BitaBoxEntreprise.objects.get(id=enterprise_id)
            commercial = BitaBoxUtilisateur.objects.get(id=commercial_id)
        except BitaBoxEntreprise.DoesNotExist:
            return Response({"error": "Enterprise not found"}, status=status.HTTP_404_NOT_FOUND)
        except BitaBoxUtilisateur.DoesNotExist:
            return Response({"error": "Commercial user not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = LeadSerializer(data=request.data)
        if serializer.is_valid():
            lead = serializer.save(enterprise=entreprise, commercial=commercial)
            return Response({
                "message": "Lead added successfully",
                "lead": LeadSerializer(lead).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LeadByAuthorView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, author_id):
        leads = BitaBoxLead.objects.filter(author__id=author_id)
        serializer = LeadSerializer(leads, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CommentListCreateView(generics.ListCreateAPIView):
    queryset = BitaboxComment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BitaboxComment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]


class CommentairesParLeadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, lead_id):
        lead = get_object_or_404(BitaBoxLead, id=lead_id)
        commentaires = BitaboxComment.objects.filter(lead_id=lead).order_by('-date', '-time')
        serializer = CommentSerializer(commentaires, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CommentairesParUtilisateurView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        commentaires = BitaboxComment.objects.filter(user=user).order_by('-date', '-time')
        serializer = CommentSerializer(commentaires, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CommentaireFiltreView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        lead_id = request.GET.get('lead_id')
        user_id = request.GET.get('user_id')

        commentaires = BitaboxComment.objects.all()

        if lead_id:
            commentaires = commentaires.filter(lead_id=lead_id)
        if user_id:
            commentaires = commentaires.filter(user_id=user_id)

        commentaires = commentaires.order_by('-date', '-time')
        serializer = CommentSerializer(commentaires, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AjouterCommentaireView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        lead_id = request.data.get('lead_id')
        message = request.data.get('message')

        if not all([lead_id, message]):
            return Response(
                {"error": "Les champs 'lead_id' et 'message' sont requis."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lead = BitaBoxLead.objects.get(id=lead_id)
        except BitaBoxLead.DoesNotExist:
            return Response({"error": "Lead introuvable."}, status=status.HTTP_404_NOT_FOUND)

        commentaire = BitaboxComment.objects.create(
            lead_id=lead,
            user=request.user,
            message=message
        )

        serializer = CommentSerializer(commentaire)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
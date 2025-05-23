from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('loged/user/', UserView.as_view(), name='user'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path("utilisateurs/entreprise/<int:entreprise_id>/", UtilisateursParEntrepriseView.as_view(), name="utilisateurs_par_entreprise"),
    path("utilisateurs/", ListeUtilisateursView.as_view(), name="liste_utilisateurs"),
    path("utilisateurs/creer/", CreerUtilisateurView.as_view(), name="creer_utilisateur"),
    path("utilisateurs/<int:pk>/", DetailUtilisateurView.as_view(), name="detail_utilisateur"),
    path("utilisateurs/changer-mdp/", ChangePasswordView.as_view(), name="changer_mot_de_passe"),
    
    path('entreprises/', EntrepriseListCreateView.as_view(), name='entreprise-list-create'),
    path('entreprises/<int:pk>/', EntrepriseRetrieveUpdateDeleteView.as_view(), name='entreprise-detail'),
    # Routes pour les leads
    path('leads/', LeadListCreateView.as_view(), name='lead-list-create'),
    path('leads/<int:pk>/', LeadRetrieveUpdateDeleteView.as_view(), name='lead-detail'),
    path("leads/commercial/", LeadByCommercialView.as_view(), name="leads_by_commercial"),
    path("leads/entreprise/<int:entreprise_id>/", LeadByEntrepriseView.as_view(), name="leads_by_entreprise"),
    path('addlead/<int:enterprise_id>/<int:commercial_id>/', AddLeadView.as_view(), name='add-lead'),
    path('leads/author/<int:author_id>/', LeadByAuthorView.as_view(), name='leads-by-author'),

    path('comments/', CommentaireFiltreView.as_view(), name='commentaires_filtrés'),


    path('leads/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('leads/comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),

    path('leads/comments/lead/<int:lead_id>/', CommentairesParLeadView.as_view(), name='commentaires_par_lead'),
    path('utilisateurs/comments/user/<int:user_id>/', CommentairesParUtilisateurView.as_view(), name='commentaires_par_utilisateur'),
    path('comments/add/', AjouterCommentaireView.as_view(), name='ajouter_commentaire'),


    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/read/', MarkNotificationAsReadView.as_view(), name='mark-notification-read'),
    path('notifications/<int:pk>/delete/', NotificationDeleteView.as_view(), name='notification-delete'),

    path('traduction/<str:langue_source>/<str:langue_cible>/', TraductionAPIView.as_view(), name='traduction'),

    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),



]

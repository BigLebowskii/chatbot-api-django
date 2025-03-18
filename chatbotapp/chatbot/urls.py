from django.urls import path, include
from rest_framework.routers import DefaultRouter
import chatbot.views
from .views import DocumentViewSet, ConversationViewSet, MessageViewSet, index

router = DefaultRouter()
router.register(r'documents', DocumentViewSet)
router.register(r'conversations', ConversationViewSet)
router.register(r'messages', MessageViewSet)

urlpatterns = [
    path('', index, name='index'),
    path('api/', include(router.urls)),
]


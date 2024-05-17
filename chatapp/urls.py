from django.urls import path
from .views import UserSignUp, MessageViewSet, AutoMessageView
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView




urlpatterns = [
    path("sign-up", UserSignUp.as_view(actions={"post": "user_sign_up"}), name="user_login"),
    path("message/get", MessageViewSet.as_view(actions={"get": "get_messages"}), name="get_messages"),
    path("message/send", MessageViewSet.as_view(actions={"post": "send_message"}), name="send_message"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('message/auto/', AutoMessageView.as_view(actions = {"post":"send_message"}), name="message_auto")
]

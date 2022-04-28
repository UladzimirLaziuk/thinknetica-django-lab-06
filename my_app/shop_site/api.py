import rest_framework
from django.contrib.auth.models import User
from django_filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.renderers import TemplateHTMLRenderer
from shop_site.models import Ad, Seller
from shop_site.serializers import UserSerializer, AdSerializer, SellerSerializer
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny


class AdsViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer


class OwnProfilePermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user


class ActionBasedPermission(AllowAny):

    def has_permission(self, request, view):
        for klass, actions in getattr(view, 'action_permissions', {}).items():
            if view.action in actions:
                return klass().has_permission(request, view)
        return False


class MyTemplateHTMLRenderer(TemplateHTMLRenderer):
    def get_template_context(self, object_list, renderer_context):
        response = renderer_context['response']
        if response.exception:
            object_list['status_code'] = response.status_code
        return {'object_list': object_list}


class MyModelViewSet(viewsets.ModelViewSet):
    # renderer_classes = [MyTemplateHTMLRenderer]
    # pagination_class = PageNumberPagination
    # template_name = 'ad_list.html'
    serializer_class = AdSerializer
    queryset = Ad.objects.all()

    permission_classes = (ActionBasedPermission,)
    action_permissions = {
        IsAuthenticated: ['create'],
        AllowAny: ['retrieve', 'list'],
        OwnProfilePermission: ['update', 'partial_update', 'destroy'],
    }

    authentication_classes = (TokenAuthentication, SessionAuthentication)  # TODO ??


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class SellerUpdateViews(RetrieveUpdateDestroyAPIView):
    # renderer_classes = [TemplateHTMLRenderer]
    # template_name = 'seller_update.html'
    model = Seller
    serializer_class = SellerSerializer

    def get_queryset(self):
        return self.model.objects.filter(pk=self.kwargs['pk'])



class AdBasketList(ListAPIView):
    serializer_class = AdSerializer

    def get_queryset(self):
        username = self.kwargs['username']
        return Ad.objects.filter(seller__user__username=username)


class AdListFilter(ListAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['category', 'data_create']
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from GraphQL.views import PrivateGraphQLView

urlpatterns = [
    path('', csrf_exempt(PrivateGraphQLView.as_view(graphiql=True)), name='graphql_ui'),
]

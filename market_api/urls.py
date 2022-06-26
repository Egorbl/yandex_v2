from django.urls import path
from .views import import_units, ShopUnitStatisticsAPIView, ShopUnitDeleteAPIView, ShopUnitRetrieveAPIView, SalesAPIView
from .views import NodeStatisticAPIView

app_name = 'market_api'

urlpatterns = [
    path('imports', import_units),  # Post new offers and categories
    # Post changes of offers and categories
    path('statistics', ShopUnitStatisticsAPIView.as_view()),
    path('delete/<str:pk>', ShopUnitDeleteAPIView.as_view()),  # Delete a unit
    # Get all information about a unit
    path('nodes/<str:pk>', ShopUnitRetrieveAPIView.as_view()),
    # Get all changes of units in interval [givenDate - 24h; givenDate]
    path('sales', SalesAPIView.as_view()),
    # Get all statistics for 1 unit in interval [startDate; endDate]
    path('node/<str:pk>/statistic', NodeStatisticAPIView.as_view())
]

from django.urls import path

from agents.views import Agents

urlpatterns = [
    path("health_plan/", Agents.as_view({"post": "health_plan"})),
    path("health_plan2/", Agents.as_view({"post": "health_plan2"})),
    path(
        "modified_health_plan/",
        Agents.as_view({"post": "modified_health_plan"}),
    ),
    path("guided_health_plan/", Agents.as_view({"post": "guided_health_plan"})),
]


# urlpatterns = [
#     path("price_range", Vaults.as_view({"get": "price_range"})),
#     path("expiration", Vaults.as_view({"get": "expiration"})),
#     path("asset_tvl", Vaults.as_view({"get": "asset_tvl"})),
#     path("total_tvl", Vaults.as_view({"get": "total_tvl"})),
#     path("strategy_plot_data", Vaults.as_view({"get": "strategy_plot_data"})),
#     path("asset_apy", Vaults.as_view({"get": "asset_apy"})),
# ]

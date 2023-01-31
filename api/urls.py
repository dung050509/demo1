from django.urls import path
from rest_framework.urlpatterns  import format_suffix_patterns
from teacrawler import views
from teatwitter.teacrawler.api.views import (
    search_user_view,
    search_user_tweet,
    get_task_process,
    search_cmc_token,
    search_token_detail,
    get_detail_tweet,
    live_search_user_view,
    get_detail_tweet1

)

app_name = "teacrawler_api"
urlpatterns = [
    path('search/user', search_user_view, name='search_user'),
    path('search/tweet', search_user_tweet, name='search_tweet'),
    path('search/tweet-by-id', get_detail_tweet, name='get_detail_tweet'),
    path('search/tasks', get_task_process, name='get_task_process'),
    path('search/cmc-token', search_cmc_token, name='search_cmc_token'),
    path('search/token-detail', search_token_detail, name='search_token_detail'),
    path('susgest/users', live_search_user_view, name='live_search_user_view'),
    path("search/tweet-by-hashtags", get_detail_tweet1, name='get_detail_tweet1')
]

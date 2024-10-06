from django.urls import path

from article.views import (
    ArticleEditHistoryView,
    ListArticleApprovalView,
    ArticleApprovalView,
    CreateArticleView,
    Dashboard,
    UpdateArticleView
)

urlpatterns = [
    path("", Dashboard.as_view(), name="dashboard"),
    path("articles-edited",
         ArticleEditHistoryView.as_view(),
         name="article-edit-history"),
    path("article", CreateArticleView.as_view(), name="new-article"),
    path("article/<article_id>",
         UpdateArticleView.as_view(),
         name="article-detail"),
    path("article-approval",
         ListArticleApprovalView.as_view(),
         name="article-approval-list"),
    path("article-approval/<article_id>",
         ArticleApprovalView.as_view(),
         name="article-approval")
]

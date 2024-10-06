from typing import Any
from datetime import timedelta
from django.forms import BaseModelForm
from django.http import HttpResponse
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, ListView
from django.db.models import Count, Q

from article.forms import (
    ArticleApprovalForm,
    CreateArticleForm,
    UpdateArticleForm
)
from article.models import Article, ArticleStatus
from article.permission import EditorRequiredMixin
from user.models import Writer


class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = "article/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # Query to get each writer article count
        thirty_days_ago = timezone.now() - timedelta(days=30)
        thirty_day_filter = Q(article_writer__created_at__gte=thirty_days_ago)
        context["writer"] = Writer.objects.values("name").annotate(
            total_article=Count("article_writer"),
            articles_last_30_days=Count("article_writer",
                                        filter=thirty_day_filter)
        )

        return context


class CreateArticleView(LoginRequiredMixin, CreateView):
    template_name = "article/create_article.html"
    model = Article
    form_class = CreateArticleForm

    def get_success_url(self):
        return reverse('article-detail', kwargs={'article_id': self.object.id})

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.written_by = self.request.user
        return super().form_valid(form)


class UpdateArticleView(LoginRequiredMixin, UpdateView):
    template_name = "article/update_article.html"
    model = Article
    form_class = UpdateArticleForm
    pk_url_kwarg = "article_id"
    success_url = reverse_lazy("dashboard")


class ListArticleApprovalView(EditorRequiredMixin, ListView):
    template_name = "article/approve_article.html"
    model = Article
    context_object_name = "articles"

    def get_queryset(self):
        return self.model.objects.filter(status=ArticleStatus.pending_review)


class ArticleApprovalView(EditorRequiredMixin, UpdateView):
    template_name = "article/approve_article.html"
    model = Article
    form_class = ArticleApprovalForm
    pk_url_kwarg = "article_id"
    success_url = reverse_lazy("article-approval-list")

    def get_queryset(self):
        return self.model.objects.filter(status=ArticleStatus.pending_review)

    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        return super().form_valid(form)


class ArticleEditHistoryView(EditorRequiredMixin, ListView):
    template_name = "article/article_approval_history.html"
    model = Article
    context_object_name = "articles"

    def get_queryset(self):
        return self.model.objects.filter(edited_by=self.request.user)

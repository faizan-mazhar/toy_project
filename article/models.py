from django.db import models
from user.models import Writer


class ArticleStatus(models.TextChoices):
    approved = "Approved"
    rejected = "Rejected"
    pending_review = "Pending review"


class Article(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(Writer,
                                  on_delete=models.SET_NULL,
                                  null=True,
                                  related_name="article_editor")
    written_by = models.ForeignKey(Writer,
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   related_name="article_writer")

    title = models.CharField(max_length=255)
    content = models.TextField()
    status = models.CharField(choices=ArticleStatus,
                              default=ArticleStatus.pending_review,
                              max_length=15)

from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
from project.test_base import TestBase, ArticleFactory
from article.models import Article, ArticleStatus


class DashboardTest(TestBase):

    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("dashboard")

    def test_verify_count_for_writer(self):
        writer = self.get_writer(authenticate=True)
        writer_2 = self.get_writer()

        # First writer articles
        ArticleFactory.create_batch(4, written_by=writer)

        # Create article for writer one to be older then 10 days.
        older_articles = ArticleFactory.create_batch(2, written_by=writer)
        forty_days_ago = timezone.now() - timedelta(days=40)
        for old_article in older_articles:
            old_article.created_at = forty_days_ago
            old_article.save()

        # Second writer articles
        ArticleFactory.create_batch(2, written_by=writer_2)

        # writer article map
        writer_article_map = {
            writer.name: {"total_article": 6, "articles_last_30_days": 4},
            writer_2.name: {"total_article": 2, "articles_last_30_days": 2},
        }
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        writers_data = response.context["writer"]
        self.assertEqual(len(writers_data), 2)
        for writer in writers_data:
            expected_article = writer_article_map[writer["name"]]
            self.assertEqual(expected_article["total_article"],
                             writer["total_article"])
            self.assertEqual(
                expected_article["articles_last_30_days"],
                writer["articles_last_30_days"],
            )


class CreateArticleTest(TestBase):

    def setUp(self):
        super().setUp()
        self.url = reverse("new-article")
        self.writer = self.get_writer(authenticate=True)

    def test_article_creation(self):
        title = "Testing article creation"
        data = {"title": title, "content": "testing content"}

        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Article.objects.filter(title=title).count(), 1)
        self.assertEqual(
            Article.objects.filter(written_by=self.writer).count(), 1
            )

    def test_article_creation_with_missing_title(self):
        data = {}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(
            form.errors,
            {
                "title": ["This field is required."],
                "content": ["This field is required."],
            },
        )


class UpdateArticleTest(TestBase):

    def setUp(self) -> None:
        super().setUp()
        self.writer = self.get_writer(authenticate=True)
        self.article = ArticleFactory(
            written_by=self.writer, title="Old title", content="old content"
        )
        self.url = reverse("article-detail",
                           kwargs={"article_id": self.article.id})

    def test_updating_article_content(self):
        title = "Updated title"
        content = "Updated content"
        data = {
            "title": title,
            "content": content,
        }

        # Assert article with following content does not exist
        self.assertFalse(Article.objects.filter(title=title).exists())
        self.assertFalse(Article.objects.filter(content=content).exists())
        self.assertTrue(Article.objects.filter(written_by=self.writer))

        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Article.objects.filter(title=title).count(), 1)
        self.assertEqual(Article.objects.filter(content=content).count(), 1)

    def test_update_status_field_of_article(self):
        data = {
            "title": self.article.title,
            "content": self.article.content,
            "status": ArticleStatus.approved,
        }

        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 302)
        self.article.refresh_from_db()
        self.assertEqual(self.article.status, ArticleStatus.pending_review)
        self.assertNotEqual(self.article.status, ArticleStatus.approved)


class ArticleApprovalTest(TestBase):
    def setUp(self):
        super().setUp()
        self.url = reverse("article-approval-list")
        self.editor = self.get_editor(authenticate=True)
        self.writer = self.get_writer()

    def test_get_article_view(self):
        ArticleFactory.create_batch(
            3, written_by=self.writer, status=ArticleStatus.approved
        )
        ArticleFactory.create_batch(
            2, written_by=self.writer, status=ArticleStatus.rejected
        )
        pending_articles = ArticleFactory.create_batch(
            4, written_by=self.writer, status=ArticleStatus.pending_review
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        articles = response.context["articles"]
        self.assertEqual(len(articles), 4)
        self.assertListEqual(
            [article.id for article in articles],
            [article.id for article in pending_articles],
        )

    def test_update_article_view(self):
        article = ArticleFactory.create(written_by=self.writer)
        url = reverse("article-approval", kwargs={"article_id": article.id})
        data = {"status": ArticleStatus.approved}

        # verify there is no approved article
        self.assertEqual(
            Article.objects.filter(status=ArticleStatus.approved).count(), 0
        )
        self.assertEqual(
            Article.objects.filter(edited_by=self.editor).count(), 0
            )

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        article.refresh_from_db()
        self.assertEqual(article.status, ArticleStatus.approved)
        self.assertEqual(article.edited_by, self.editor)

    def test_editor_can_only_access_page(self):
        self.client.force_login(self.writer)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)


class ArticleEditHistoryTest(TestBase):

    def setUp(self):
        super().setUp()
        self.url = reverse("article-edit-history")
        self.writer = self.get_writer()
        self.editor = self.get_editor(authenticate=True)

    def test_only_current_user_article_are_listed(self):
        editor_2 = self.get_editor()

        # First editor articles
        first_editor_articles = ArticleFactory.create_batch(
            2, written_by=self.writer, edited_by=self.editor
        )

        # Second editor article
        second_editor_articles = ArticleFactory.create_batch(
            3, written_by=self.writer, edited_by=editor_2
        )

        # Response should only contain articles for the first editor
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        editor_articles = response.context["articles"]

        self.assertEqual(len(editor_articles), 2)
        expected_article_ids = [
            article.id for article in first_editor_articles
            ]
        not_expected_article_ids = [
            article.id for article in second_editor_articles
            ]
        response_article_ids = [article.id for article in editor_articles]
        self.assertListEqual(expected_article_ids, response_article_ids)
        self.assertNotEqual(not_expected_article_ids, response_article_ids)

    def test_only_editor_can_access_page(self):
        self.client.force_login(self.writer)

        # Writer should not be able to access the page
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

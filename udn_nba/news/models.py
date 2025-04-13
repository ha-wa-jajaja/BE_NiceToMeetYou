from django.db import models


class Author(models.Model):
    # Indexing on name field is for faster search to check if author exists
    name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.name


class NewsSession(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        formatted_date = self.created_at.strftime("%Y-%m-%d %H:%M")
        news_count = self.news.count()
        return f"Session {self.id} ({formatted_date}) - {news_count} articles"


class News(models.Model):
    # Indexing on title field is for faster search implementation in the future
    title = models.CharField(max_length=200, db_index=True)
    content = models.TextField()
    # Indexing on original_url field is for faster identification of existing news
    original_url = models.URLField(db_index=True)
    thumbnail_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, related_name="news", null=True, blank=True
    )
    session = models.ForeignKey(
        NewsSession, on_delete=models.CASCADE, related_name="news"
    )
    tags = models.ManyToManyField("tags.Tag", related_name="news", blank=True)

    def __str__(self):
        return self.title

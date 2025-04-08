from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class NewsSession(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        formatted_date = self.created_at.strftime("%Y-%m-%d %H:%M")
        news_count = self.news.count()
        return f"Session {self.id} ({formatted_date}) - {news_count} articles"


class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    thumbnail_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="news")
    session = models.ForeignKey(
        NewsSession, on_delete=models.CASCADE, related_name="news"
    )
    tags = models.ManyToManyField("tags.Tag", related_name="news")

    def __str__(self):
        return self.title

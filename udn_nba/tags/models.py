from django.db import models


class Tag(models.Model):
    class TypeChoices(models.TextChoices):
        TEAMS = "Teams"
        PLAYERS = "Players"

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=TypeChoices.choices)

    class Meta:
        unique_together = ["name", "type"]

    def __str__(self):
        return self.name

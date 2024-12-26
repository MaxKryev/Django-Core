from django.contrib.auth.models import User
from django.db import models


class Docs(models.Model):

    file_path = models.CharField(max_length=1000)
    size = models.PositiveIntegerField(db_index=True)
    external_id = models.IntegerField(null=True, blank=True, default=None)
    file_type = models.CharField(max_length=30, default="png")

    class Meta:
        db_table = "docs"

    def __str__(self):
        return self.file_path


class UsersToDocs(models.Model):

    username = models.ForeignKey(User, on_delete=models.CASCADE, max_length=50)
    docs_id = models.ForeignKey(Docs, on_delete=models.CASCADE)

    class Meta:
        db_table = "users_to_docs"

    def __str__(self):
        return self.username


class Price(models.Model):

    file_type = models.CharField(max_length=30)
    price = models.FloatField()

    class Meta:
        db_table = "price"

    def __str__(self):
        return f"{self.file_type}: {self.price}"


class Cart(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    docs = models.ForeignKey(Docs, on_delete=models.CASCADE)
    order_price = models.FloatField()
    payment = models.BooleanField(default=False)

    class Meta:
        db_table = "cart"

    def __str__(self):
        return f"cart of {self.user.name} - {self.docs}"
    
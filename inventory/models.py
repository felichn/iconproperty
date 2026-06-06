from django.db import models


class Property(models.Model):
    class PropertyType(models.TextChoices):
        RUMAH = "rumah", "Rumah"
        RUKO = "ruko", "Ruko"
        GUDANG = "gudang", "Gudang"

    class ListingMode(models.TextChoices):
        RENT = "rent", "Rent"
        SELL = "sell", "Sell"

    title = models.CharField(max_length=200)
    property_type = models.CharField(max_length=20, choices=PropertyType.choices)
    listing_mode = models.CharField(max_length=20, choices=ListingMode.choices)
    price = models.DecimalField(max_digits=14, decimal_places=2)
    width = models.DecimalField(max_digits=8, decimal_places=2)
    length = models.DecimalField(max_digits=8, decimal_places=2)
    floors = models.PositiveIntegerField(default=1)
    area = models.CharField(max_length=100)
    owner_whatsapp_number = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_property_type_display()})"


class PropertyPhoto(models.Model):
    property = models.ForeignKey(
        Property, related_name="photos", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="property_photos/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["uploaded_at"]

    def __str__(self):
        return f"Photo {self.pk} for property {self.property_id}"

# Create your models here.

from django.core.exceptions import ValidationError
from django.db import models


class Property(models.Model):
    class PropertyType(models.TextChoices):
        RUMAH = "rumah", "Rumah"
        RUKO = "ruko", "Ruko"
        GUDANG = "gudang", "Gudang"

    class ListingMode(models.TextChoices):
        RENT = "rent", "Rent"
        SELL = "sell", "Sell"

    AREA_OPTIONS_BY_PROPERTY_TYPE = {
        PropertyType.RUMAH: ["Villa Pasir Putih"],
        PropertyType.RUKO: ["Hollywood", "Manhattan", "Broadway"],
        PropertyType.GUDANG: ["Bizpark"],
    }

    title = models.CharField(max_length=200)
    property_type = models.CharField(max_length=20, choices=PropertyType.choices)
    listing_mode = models.CharField(max_length=20, choices=ListingMode.choices)
    block = models.CharField(max_length=20, default="1")
    unit_no = models.PositiveIntegerField(default=1)
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
        constraints = [
            models.UniqueConstraint(
                fields=["property_type", "area", "block", "unit_no"],
                name="unique_property_unit_identifier",
            ),
        ]

    def __str__(self):
        return f"{self.unit} ({self.get_property_type_display()})"

    @property
    def normalized_block(self):
        return "".join(str(self.block).upper().split())

    @property
    def unit(self):
        area_prefix_map = {
            (self.PropertyType.RUMAH, "Villa Pasir Putih"): "V5S",
            (self.PropertyType.RUKO, "Hollywood"): "MBHW",
            (self.PropertyType.RUKO, "Manhattan"): "MBMN",
            (self.PropertyType.RUKO, "Broadway"): "MBBW",
            (self.PropertyType.GUDANG, "Bizpark"): "BP",
        }
        prefix = area_prefix_map.get((self.property_type, self.area), "UNIT")
        block = self.normalized_block or "X"
        number = int(self.unit_no or 0)

        if self.property_type == self.PropertyType.RUKO:
            return f"{prefix}-{block}{number:02d}"
        return f"{prefix}{block}-{number:03d}"

    def clean(self):
        super().clean()
        valid_areas = self.AREA_OPTIONS_BY_PROPERTY_TYPE.get(self.property_type, [])
        if self.area and valid_areas and self.area not in valid_areas:
            raise ValidationError(
                {"area": f"Area must be one of: {', '.join(valid_areas)}."}
            )
        if self.unit_no < 1:
            raise ValidationError({"unit_no": "No. must be at least 1."})
        if not self.normalized_block:
            raise ValidationError({"block": "Blok is required."})


class PropertyPhoto(models.Model):
    property = models.ForeignKey(
        Property, related_name="photos", on_delete=models.CASCADE
    )
    image = models.FileField(upload_to="property_photos/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["uploaded_at"]

    def __str__(self):
        return f"Photo {self.pk} for property {self.property_id}"

# Create your models here.

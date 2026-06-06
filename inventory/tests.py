import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from .models import Property, PropertyPhoto


TEST_MEDIA_ROOT = tempfile.mkdtemp(prefix="inventory_test_media_")


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT, MEDIA_URL="/media/")
class PropertyApiTests(TestCase):
    def _build_test_image(self, color=(255, 100, 100)):
        image_bytes = BytesIO()
        image = Image.new("RGB", (120, 80), color=color)
        image.save(image_bytes, format="JPEG")
        return SimpleUploadedFile(
            "sample.jpg", image_bytes.getvalue(), content_type="image/jpeg"
        )

    def setUp(self):
        for index in range(11):
            Property.objects.create(
                title=f"Property {index}",
                property_type=Property.PropertyType.RUMAH,
                listing_mode=Property.ListingMode.SELL,
                price=1_000_000 + index,
                width=10,
                length=20,
                floors=2,
                area="Jakarta",
                owner_whatsapp_number="6281234567890",
                description="Sample listing",
            )

    def test_property_list_pagination_returns_10_items(self):
        response = self.client.get("/api/properties/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload["results"]), 10)
        self.assertEqual(payload["pagination"]["total_items"], 11)
        self.assertEqual(payload["pagination"]["num_pages"], 2)

    def test_property_list_filtering_by_listing_mode(self):
        Property.objects.create(
            title="Rental Listing",
            property_type=Property.PropertyType.RUKO,
            listing_mode=Property.ListingMode.RENT,
            price=2_000_000,
            width=8,
            length=15,
            floors=1,
            area="Bandung",
            owner_whatsapp_number="6281111111111",
            description="Rental unit",
        )
        response = self.client.get("/api/properties/?listing_mode=rent")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["pagination"]["total_items"], 1)
        self.assertEqual(payload["results"][0]["listing_mode"], "rent")

    def test_collage_creation_returns_whatsapp_url(self):
        listing = Property.objects.first()
        PropertyPhoto.objects.create(property=listing, image=self._build_test_image())
        PropertyPhoto.objects.create(
            property=listing, image=self._build_test_image(color=(50, 150, 220))
        )

        response = self.client.post(
            f"/api/properties/{listing.id}/collage/",
            data='{"photo_ids": []}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("collage_url", payload)
        self.assertIn("whatsapp_share_url", payload)
        self.assertIn("https://wa.me/?text=", payload["whatsapp_share_url"])

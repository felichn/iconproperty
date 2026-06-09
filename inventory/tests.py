import json
import tempfile
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from .models import Property, PropertyPhoto


TEST_MEDIA_ROOT = tempfile.mkdtemp(prefix="inventory_test_media_")


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT, MEDIA_URL="/media/")
class PropertyApiTests(TestCase):
    def _build_test_image(self, name="sample.jpg"):
        return SimpleUploadedFile(
            name,
            b"test image bytes",
            content_type="image/jpeg",
        )

    def setUp(self):
        for index in range(11):
            Property.objects.create(
                title=f"Property {index}",
                property_type=Property.PropertyType.RUMAH,
                listing_mode=Property.ListingMode.SELL,
                block=f"{(index % 3) + 1}",
                unit_no=index + 1,
                price=1_000_000 + index,
                width=10,
                length=20,
                floors=2,
                area="Villa Pasir Putih",
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
            block="F",
            unit_no=1,
            price=2_000_000,
            width=8,
            length=15,
            floors=1,
            area="Hollywood",
            owner_whatsapp_number="6281111111111",
            description="Rental unit",
        )
        response = self.client.get("/api/properties/?listing_mode=rent")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["pagination"]["total_items"], 1)
        self.assertEqual(payload["results"][0]["listing_mode"], "rent")

    def test_create_property_defaults_title_when_not_provided(self):
        response = self.client.post(
            "/api/properties/",
            data=json.dumps(
                {
                    "property_type": "gudang",
                    "listing_mode": "sell",
                    "block": "C2",
                    "unit_no": 55,
                    "price": "3500000000",
                    "width": "15",
                    "length": "25",
                    "floors": 2,
                    "area": "Bizpark",
                    "owner_whatsapp_number": "6281230000000",
                    "description": "Auto-title listing",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertEqual(payload["title"], "Bizpark")
        self.assertEqual(payload["unit"], "BPC2-055")

    def test_unit_format_examples(self):
        Property.objects.all().delete()

        rumah = Property.objects.create(
            title="Villa Pasir Putih",
            property_type=Property.PropertyType.RUMAH,
            listing_mode=Property.ListingMode.SELL,
            block="1",
            unit_no=38,
            price=100,
            width=10,
            length=10,
            floors=1,
            area="Villa Pasir Putih",
            owner_whatsapp_number="6281000000001",
            description="",
        )
        rumah_2 = Property.objects.create(
            title="Villa Pasir Putih",
            property_type=Property.PropertyType.RUMAH,
            listing_mode=Property.ListingMode.SELL,
            block="3",
            unit_no=3,
            price=100,
            width=10,
            length=10,
            floors=1,
            area="Villa Pasir Putih",
            owner_whatsapp_number="6281000000002",
            description="",
        )
        ruko = Property.objects.create(
            title="Hollywood",
            property_type=Property.PropertyType.RUKO,
            listing_mode=Property.ListingMode.SELL,
            block="F",
            unit_no=1,
            price=100,
            width=10,
            length=10,
            floors=1,
            area="Hollywood",
            owner_whatsapp_number="6281000000003",
            description="",
        )
        gudang = Property.objects.create(
            title="Bizpark",
            property_type=Property.PropertyType.GUDANG,
            listing_mode=Property.ListingMode.SELL,
            block="C2",
            unit_no=55,
            price=100,
            width=10,
            length=10,
            floors=1,
            area="Bizpark",
            owner_whatsapp_number="6281000000004",
            description="",
        )

        self.assertEqual(rumah.unit, "V5S1-038")
        self.assertEqual(rumah_2.unit, "V5S3-003")
        self.assertEqual(ruko.unit, "MBHW-F01")
        self.assertEqual(gudang.unit, "BPC2-055")

    def test_property_share_links_returns_page_and_download_urls(self):
        listing = Property.objects.first()
        PropertyPhoto.objects.create(property=listing, image=self._build_test_image())

        response = self.client.get(
            f"/api/properties/{listing.id}/share-links/",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("property_page_url", payload)
        self.assertIn("download_photos_url", payload)
        self.assertIn("whatsapp_share_url", payload)
        self.assertIn("https://wa.me/?text=", payload["whatsapp_share_url"])

    def test_photo_download_returns_zip_attachment(self):
        listing = Property.objects.first()
        PropertyPhoto.objects.create(property=listing, image=self._build_test_image())
        PropertyPhoto.objects.create(
            property=listing, image=self._build_test_image(name="sample-2.jpg")
        )

        response = self.client.get(f"/api/properties/{listing.id}/download-photos/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        self.assertIn("attachment;", response["Content-Disposition"])

    def test_photo_upload_attaches_files_to_property(self):
        listing = Property.objects.first()

        response = self.client.post(
            f"/api/properties/{listing.id}/photos/",
            data={
                "photos": [
                    self._build_test_image(name="front.jpg"),
                    self._build_test_image(name="kitchen.jpg"),
                ]
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(listing.photos.count(), 2)
        self.assertEqual(len(response.json()["photos"]), 2)

    def test_property_public_page_shows_photo_gallery(self):
        listing = Property.objects.first()
        PropertyPhoto.objects.create(property=listing, image=self._build_test_image())

        response = self.client.get(f"/properties/{listing.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, listing.unit)
        self.assertContains(response, "Download All Photos")

    def test_add_property_page_route_is_available(self):
        response = self.client.get("/properties/add/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add Property")
        self.assertContains(response, "add-property-page")

    def test_add_property_form_script_has_requested_labels(self):
        script_path = Path(__file__).resolve().parent / "static/inventory/add_property.jsx"
        script = script_path.read_text()

        for label in (
            "Rent or Sell",
            "Harga",
            "Juta",
            "Milyar",
            "Width",
            "Length",
            "Lantai",
            "Contact",
            "Attach Photos",
        ):
            self.assertIn(label, script)
        self.assertIn('owner_whatsapp_number: "+62"', script)
        self.assertIn("expandPriceValue(formData.price, price_unit)", script)
        self.assertIn('unit === "milyar" ? "1000000000" : "1000000"', script)
        self.assertNotIn("Description", script)

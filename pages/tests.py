from django.test import SimpleTestCase
from django.urls import reverse


class HomePageTests(SimpleTestCase):
    def test_homepage_uses_home_template(self):
        response = self.client.get(reverse("pages:home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/home.html")

    def test_homepage_renders_property_sections(self):
        response = self.client.get("/")

        self.assertContains(response, "Find the space that moves you forward.")
        self.assertContains(response, "Property paths")
        self.assertContains(response, "Sharper property discovery")
        self.assertContains(response, "Market notes")
        self.assertContains(response, 'href="/static/pages/styles.css"')

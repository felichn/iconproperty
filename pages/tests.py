from django.test import SimpleTestCase
from django.urls import reverse


class HomePageTests(SimpleTestCase):
    def test_homepage_uses_support_template(self):
        response = self.client.get(reverse("pages:home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/home.html")

    def test_homepage_renders_lululemon_inspired_support_sections(self):
        response = self.client.get("/")

        self.assertContains(response, "Welcome. We're here to help.")
        self.assertContains(response, "Quick Actions")
        self.assertContains(response, "Chat with us")
        self.assertContains(response, "Let's stay in touch.")
        self.assertContains(response, 'href="/static/pages/styles.css"')

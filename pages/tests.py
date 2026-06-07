from django.test import SimpleTestCase
from django.urls import reverse


class HomePageTests(SimpleTestCase):
    def test_homepage_uses_home_template(self):
        response = self.client.get(reverse("pages:home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/home.html")

    def test_homepage_renders_simple_hello_page(self):
        response = self.client.get("/")

        self.assertContains(response, "Hello.")
        self.assertContains(response, "Welcome to a cleaner property workspace.")
        self.assertContains(response, "/properties/add/")
        self.assertContains(response, 'href="/static/pages/styles.css"')

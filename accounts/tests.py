from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='profile-user',
            password='secure-pass-123',
        )

    def test_profile_page_loads_for_logged_in_user(self):
        self.client.login(username='profile-user', password='secure-pass-123')

        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Profile')

from django.test import TestCase
from .models import User, File, Share


class UserModelTest(TestCase):
    def test_user_creation(self):
        """
        Test user creation and password hashing.
        """
        user = User.objects.create_user(username="testuser", password="testpassword")
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.check_password("testpassword"))


class FileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

    def test_file_creation(self):
        """
        Test file creation and formatting of file size.
        """
        file = File.objects.create(
            user=self.user,
            name="testfile.txt",
            size=1024,
            type="text/plain",
            path="/test/testfile.txt",
            access_permissions="Private",
            sharing_status=False,
        )
        self.assertIsInstance(file, File)
        self.assertEqual(file.user, self.user)
        self.assertEqual(file.name, "testfile.txt")
        self.assertEqual(file.formatted_size, "1.00KB")
        self.assertFalse(file.sharing_status)


class ShareModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="password1")
        self.user2 = User.objects.create_user(username="user2", password="password2")
        self.file = File.objects.create(
            user=self.user1,
            name="testfile.txt",
            size=1024,
            type="text/plain",
            path="/test/testfile.txt",
            access_permissions="Private",
            sharing_status=False,
        )

    def test_share_creation(self):
        """
        Test share creation and sharing functionality.
        """
        share = Share.objects.create(file=self.file, sender=self.user1)
        share.receiver.add(self.user2)
        self.assertIsInstance(share, Share)
        self.assertEqual(share.sender, self.user1)
        self.assertEqual(share.receiver.count(), 1)
        self.assertEqual(list(share.receiver.all())[0], self.user2)

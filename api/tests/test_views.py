from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Category, Company
import uuid


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        self.category = Category.objects.create(
            company=self.company,
            name="Existing Category",
            parent_category=None,
        )

    def test_list(self):
        response = self.client.get("/api/categories/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.category.id))

    def test_retrieve(self):
        response = self.client.get(f"/api/categories/{self.category.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.category.id))
        self.assertEqual(response.data["name"], self.category.name)

    def test_retrieve_returns_404_when_category_does_not_exist(self):
        response = self.client.get(f"/api/categories/{uuid.uuid4()}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        response = self.client.post(
            "/api/categories/",
            {
                "company": str(self.company.id),
                "name": "Created Category",
                "parent_category": None,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
        self.assertTrue(Category.objects.filter(name="Created Category", company=self.company).exists())

    def test_create_returns_400_when_name_exceeds_max_length(self):
        response = self.client.post(
            "/api/categories/",
            {
                "company": str(self.company.id),
                "name": "a" * 256,
                "parent_category": None,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(Category.objects.count(), 1)

    def test_create_returns_400_when_name_is_blank_only(self):
        response = self.client.post(
            "/api/categories/",
            {
                "company": str(self.company.id),
                "name": "   ",
                "parent_category": None,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(Category.objects.count(), 1)

    def test_create_returns_400_when_name_already_exists_in_same_company(self):
        response = self.client.post(
            "/api/categories/",
            {
                "company": str(self.company.id),
                "name": self.category.name,
                "parent_category": None,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertEqual(Category.objects.count(), 1)

    def test_create_allows_same_name_in_different_company(self):
        other_company = Company.objects.create(name="Other Company")

        response = self.client.post(
            "/api/categories/",
            {
                "company": str(other_company.id),
                "name": self.category.name,
                "parent_category": None,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(company=other_company, name=self.category.name).exists())

    def test_update(self):
        response = self.client.patch(
            f"/api/categories/{self.category.id}/",
            {"name": "Updated Category"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Updated Category")

    def test_update_returns_400_when_name_exceeds_max_length(self):
        response = self.client.patch(
            f"/api/categories/{self.category.id}/",
            {"name": "a" * 256},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Existing Category")

    def test_update_returns_400_when_name_is_blank_only(self):
        response = self.client.patch(
            f"/api/categories/{self.category.id}/",
            {"name": "   "},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Existing Category")

    def test_update_returns_400_when_name_already_exists_in_same_company(self):
        sibling_category = Category.objects.create(
            company=self.company,
            name="Sibling Category",
            parent_category=None,
        )

        response = self.client.patch(
            f"/api/categories/{sibling_category.id}/",
            {"name": self.category.name},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        sibling_category.refresh_from_db()
        self.assertEqual(sibling_category.name, "Sibling Category")

    def test_create_returns_400_when_parent_category_does_not_exist(self):
        response = self.client.post(
            "/api/categories/",
            {
                "company": str(self.company.id),
                "name": "Created Category",
                "parent_category": str(uuid.uuid4()),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)
        self.assertEqual(Category.objects.count(), 1)

    def test_create_returns_400_when_parent_category_belongs_to_different_company(self):
        other_company = Company.objects.create(name="Other Company")
        other_parent_category = Category.objects.create(
            company=other_company,
            name="Other Parent Category",
            parent_category=None,
        )

        response = self.client.post(
            "/api/categories/",
            {
                "company": str(self.company.id),
                "name": "Created Category",
                "parent_category": str(other_parent_category.id),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)
        self.assertEqual(Category.objects.count(), 2)

    def test_update_returns_400_when_parent_category_belongs_to_different_company(self):
        other_company = Company.objects.create(name="Other Company")
        other_parent_category = Category.objects.create(
            company=other_company,
            name="Other Parent Category",
            parent_category=None,
        )

        response = self.client.patch(
            f"/api/categories/{self.category.id}/",
            {"parent_category": str(other_parent_category.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)
        self.category.refresh_from_db()
        self.assertIsNone(self.category.parent_category)

    def test_update_allows_parent_category_in_same_company_without_company_in_payload(self):
        parent_category = Category.objects.create(
            company=self.company,
            name="Parent Category",
            parent_category=None,
        )

        response = self.client.patch(
            f"/api/categories/{self.category.id}/",
            {"parent_category": str(parent_category.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.parent_category_id, parent_category.id)

    def test_update_allows_clearing_parent_category_with_null(self):
        parent_category = Category.objects.create(
            company=self.company,
            name="Parent Category",
            parent_category=None,
        )
        self.category.parent_category = parent_category
        self.category.save(update_fields=["parent_category"])

        response = self.client.patch(
            f"/api/categories/{self.category.id}/",
            {"parent_category": None},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertIsNone(self.category.parent_category)

    def test_update_returns_400_when_parent_category_is_self(self):
        response = self.client.patch(
            f"/api/categories/{self.category.id}/",
            {"parent_category": str(self.category.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)
        self.category.refresh_from_db()
        self.assertIsNone(self.category.parent_category)

    def test_update_returns_400_when_parent_category_creates_cycle(self):
        child_category = Category.objects.create(
            company=self.company,
            name="Child Category",
            parent_category=self.category,
        )

        response = self.client.patch(
            f"/api/categories/{self.category.id}/",
            {"parent_category": str(child_category.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)
        self.category.refresh_from_db()
        self.assertIsNone(self.category.parent_category)

    def test_update_returns_400_when_parent_category_creates_longer_cycle(self):
        child_category = Category.objects.create(
            company=self.company,
            name="Child Category",
            parent_category=self.category,
        )
        grandchild_category = Category.objects.create(
            company=self.company,
            name="Grandchild Category",
            parent_category=child_category,
        )

        response = self.client.patch(
            f"/api/categories/{self.category.id}/",
            {"parent_category": str(grandchild_category.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)
        self.category.refresh_from_db()
        self.assertIsNone(self.category.parent_category)

    def test_update_returns_400_when_company_is_changed(self):
        other_company = Company.objects.create(name="Other Company")

        response = self.client.patch(
            f"/api/categories/{self.category.id}/",
            {"company": str(other_company.id)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("company", response.data)
        self.category.refresh_from_db()
        self.assertEqual(self.category.company_id, self.company.id)

    def test_destroy(self):
        response = self.client.delete(f"/api/categories/{self.category.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())

    def test_destroy_returns_404_when_category_does_not_exist(self):
        response = self.client.delete(f"/api/categories/{uuid.uuid4()}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_destroy_clears_parent_category_of_children(self):
        parent_category = Category.objects.create(
            company=self.company,
            name="Parent Category",
            parent_category=None,
        )
        child_category = Category.objects.create(
            company=self.company,
            name="Child Category",
            parent_category=parent_category,
        )

        response = self.client.delete(f"/api/categories/{parent_category.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        child_category.refresh_from_db()
        self.assertIsNone(child_category.parent_category)

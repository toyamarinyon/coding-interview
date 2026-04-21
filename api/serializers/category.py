from rest_framework import serializers

from api.models import Category


class CategorySerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        self._validate_company_is_not_updated(attrs)

        parent_category = self._resolve_parent_category(attrs)

        if parent_category is None:
            return attrs

        company = self._resolve_company(attrs)
        self._validate_parent_is_not_self(parent_category)
        if company is not None:
            self._validate_parent_has_same_company(parent_category, company)
        self._validate_parent_has_no_cycle(parent_category)

        return attrs

    def _resolve_parent_category(self, attrs):
        if "parent_category" in attrs:
            return attrs["parent_category"]
        if self.instance is not None:
            return self.instance.parent_category
        return None

    def _resolve_company(self, attrs):
        company = attrs.get("company")
        if company is not None:
            return company
        if self.instance is not None:
            return self.instance.company
        return None

    def _validate_company_is_not_updated(self, attrs):
        if self.instance is None:
            return
        if "company" in attrs and attrs["company"].id != self.instance.company_id:
            raise serializers.ValidationError(
                {"company": "Company cannot be updated."}
            )

    def _validate_parent_is_not_self(self, parent_category):
        if self.instance is not None and parent_category.id == self.instance.id:
            raise serializers.ValidationError(
                {"parent_category": "Category cannot be its own parent."}
            )

    def _validate_parent_has_same_company(self, parent_category, company):
        if company is not None and parent_category.company_id != company.id:
            raise serializers.ValidationError(
                {"parent_category": "Parent category must belong to the same company."}
            )

    def _validate_parent_has_no_cycle(self, parent_category):
        current_parent = parent_category
        while current_parent is not None:
            if self.instance is not None and current_parent.id == self.instance.id:
                raise serializers.ValidationError(
                    {"parent_category": "Parent category cannot create a cycle."}
                )
            current_parent = current_parent.parent_category

    class Meta:
        model = Category
        fields = [
            "id",
            "company",
            "name",
            "parent_category",
            "created_at",
            "updated_at",
        ]

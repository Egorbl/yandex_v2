from datetime import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import ShopUnit, ShopUnitStatistics


class ShopUnitSerializer(serializers.ModelSerializer):
    """Serializer for ShopUnit model instances"""

    class Meta:
        model = ShopUnit
        fields = '__all__'

    def is_valid(self, raise_exception=False, instance=None, items_id=None):
        validated = super().is_valid(raise_exception)
        self._validate(self.validated_data, instance, items_id)
        return validated

    def _validate(self, item, old_instance, items_id):
        validators = {
            "name": self._validate_name,
            "date": self._validate_date,
            "parentId": self._validate_parent_id,
            "type": self._validate_type,
            "price": self._validate_price,
        }

        for field, validator in validators.items():
            value = item.get(field, "Was not passed")
            validator.__call__(value, item, old_instance, items_id)

        return item

    def _validate_name(self, item_name, item, old_instance, items_id):
        if item_name == "Was not passed" or item_name is None:
            raise ValidationError

    def _validate_date(self, item_date, item, old_instance, items_id):
        if item_date == "Was not passed" or item_date is None:
            raise ValidationError
        try:
            datetime.fromisoformat(item_date.replace('Z', '+00:00'))
        except:
            raise ValidationError

    def _validate_parent_id(self, item_parent_id, item, old_instance, items_id):
        if item_parent_id == "Was not passed" or item_parent_id is None:
            return

        if item_parent_id == item.get("id"):
            raise ValidationError

        if item_parent_id in items_id:
            return

        parent = self.Meta().model.objects.filter(id=item_parent_id)

        if len(parent) == 0:
            raise ValidationError

        parent = parent[0]

        if parent.type == "OFFER":
            raise ValidationError

    def _validate_type(self, item_type, item, old_instance, items_id):
        if item_type == "Was not passed" or item_type is None\
                or (old_instance is not None and item_type != old_instance.type):
            raise ValidationError

        if item_type not in ["CATEGORY", "OFFER"]:
            raise ValidationError

    def _validate_price(self, item_price, item, old_instance, items_id):
        if item.get("type") == "CATEGORY":
            if item_price is None or item_price == "Was not passed":
                return
            raise ValidationError

        if item_price is None:
            raise ValidationError

        if item_price == "Was not passed" and old_instance is None:
            raise ValidationError

        if item_price != "Was not passed" and item_price < 0:
            raise ValidationError


class ShopUnitStatisticsSerializer(serializers.ModelSerializer):
    """Serializer for ShopUnitStatistics model instances"""
    class Meta:
        model = ShopUnitStatistics
        fields = '__all__'

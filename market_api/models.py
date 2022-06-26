from uuid import uuid4
from django.db import models

ShopUnitType = ['OFFER', 'CATEGORY']


class ShopUnit(models.Model):
    """Model for offers and categories and their characteristics"""
    id = models.UUIDField(unique=True,
                          default=uuid4, max_length=36, primary_key=True)
    name = models.CharField(max_length=255, blank=False)
    date = models.CharField(max_length=255)
    parentId = models.CharField(max_length=255, null=True, blank=True)

    unit_types = [(unit_type, unit_type) for unit_type in ShopUnitType]

    type = models.CharField(max_length=255, choices=unit_types)
    price = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_descendants(self):
        stack = [self.id]
        descendants = []

        while stack:
            current_node_id = stack.pop()
            children = self.__class__.objects.filter(parentId=current_node_id)

            for child in children:
                descendants.append(child)
                stack.append(child.id)

        return descendants

    def get_parent_categories(self):
        parents = []
        stack = [self]

        while stack:
            current_node_parent_id = stack.pop().parentId
            if current_node_parent_id is None:
                continue

            parent_nodes = self.__class__.objects.filter(
                id=current_node_parent_id)
            parents += parent_nodes
            stack += parent_nodes

        return parents

    def get_children_price(self):
        sum_price = 0
        count = 0

        children = self.__class__.objects.filter(parentId=self.id)

        for child in children:
            if child.type == "OFFER":
                sum_price += child.price
                count += 1
                continue

            add_price, add_count = child.get_children_price()
            sum_price += add_price
            count += add_count

        return sum_price, count


class ShopUnitStatistics(models.Model):
    """Model for all changes of offers and categories"""
    unit_id = models.CharField(max_length=36)
    name = models.CharField(max_length=255)
    date = models.CharField(max_length=255)
    parentId = models.CharField(max_length=255, null=True, blank=True)

    unit_types = [(unit_type, unit_type) for unit_type in ShopUnitType]

    type = models.CharField(max_length=255, choices=unit_types)
    price = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

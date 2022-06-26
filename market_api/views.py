import datetime

from rest_framework.decorators import api_view, parser_classes
from django.core.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import DestroyAPIView, RetrieveAPIView

from .models import ShopUnit, ShopUnitStatistics
from .serializers import ShopUnitSerializer, ShopUnitStatisticsSerializer
from .parsers import CustomJSONParser


@api_view(['POST', 'GET'])
@parser_classes([CustomJSONParser])
def import_units(request):
    """Validating JSON and sending request to ShopUnitAPIView and ShopUnitStatisticsAPIView if status code of response at ShopUnitAPIView is 200"""
    status_code = request.data.get('code', None)

    if status_code == 400:
        return Response(request.data, status=400)

    shop_unit_api_view = ShopUnitAPIView()
    shop_unit_statistics_api_view = ShopUnitStatisticsAPIView()

    if request.method == "GET":
        return shop_unit_api_view.get(request)

    response = shop_unit_api_view.post(request)

    if response.data and response.data.get("code") == 400:
        return response

    shop_unit_statistics_api_view.post(request)

    return response


class ShopUnitStatisticsAPIView(APIView):
    """GET and POST units"""
    model = ShopUnitStatistics
    serializer_class = ShopUnitStatisticsSerializer
    model_2 = ShopUnit
    serializer_class_2 = ShopUnitSerializer
    status_400 = {"code": 400, "message": "Validation Error"}

    def get(self, request):
        """Allows to get info about all units in database"""
        statistics = self.model.objects.all()
        serializer = self.serializer_class(statistics, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Allows to post new units"""
        data = request.data
        items = data.get("items")
        units_id = [item.get("id") for item in items]
        results = []
        parents = []

        for unit_id in units_id:
            shop_unit_instance = self.model_2.objects.get(id=unit_id)
            serializer_data = self.serializer_class_2(shop_unit_instance).data
            serializer_data["unit_id"] = serializer_data.get("id")
            del serializer_data["id"]

            if shop_unit_instance.type == "CATEGORY":
                sum_price, count = shop_unit_instance.get_children_price()
                serializer_data["price"] = None if count == 0 else sum_price // count

            results.append(self.serializer_class(data=serializer_data))

            parents_new = shop_unit_instance.get_parent_categories()
            parents += parents_new

        for parent in parents:
            parent_data = self.serializer_class_2(parent).data

            if parent.type == "CATEGORY":
                sum_price, count = parent.get_children_price()
                parent_data["price"] = None if count == 0 else sum_price // count
            parent_data["unit_id"] = parent_data.get("id")
            del parent_data["id"]
            results.append(self.serializer_class(data=parent_data))

        for result in results:
            if result.is_valid():
                result.save()

        return


class ShopUnitAPIView(APIView):
    """ShopUnitAPIView handles POST and GET request to /imports"""
    model = ShopUnit
    serializer_class = ShopUnitSerializer
    status_400 = {"code": 400, "message": "Validation Error"}

    def get(self, request: Request) -> Response:
        """Get all ShopUnit instances. Return drf Response object"""
        all_units = self.model.objects.all()
        serializer = self.serializer_class(all_units, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        """Post new units to ShopUnit or update old. Return drf Response object"""

        data = request.data
        items = data.get("items", None)
        date = data.get("updateDate", None)

        if date is None or items is None:
            return Response(self.status_400, status=400)

        serialized_items = []

        items_id = set([item.get("id") for item in items])

        if len(items_id) != len(items):
            return Response(self.status_400, status=400)

        for item in items:
            item["date"] = date
            item_id = item.get("id", None)
            if item_id is None:
                return Response(self.status_400, status=400)
            try:
                existing_item = self.get_model_item(item_id)
            except:
                return Response(self.status_400, status=400)

            if existing_item is None:
                serializer = self.serializer_class(data=item)
            else:
                serializer = self.serializer_class(existing_item, data=item)

            try:
                serializer.is_valid(raise_exception=True,
                                    instance=existing_item, items_id=items_id)
                serialized_items.append(serializer)
            except:
                return Response(self.status_400, status=400)

        for serializer in serialized_items:
            instance = self.perform_create(serializer)
            parents = instance.get_parent_categories()

            for parent in parents:
                parent.date = instance.date
                parent.save()

        return Response(status=200)

    def perform_create(self, serializer):
        return serializer.save()

    def get_model_item(self, item_id):
        items = self.model.objects.filter(id=item_id)
        return None if len(items) == 0 else items[0]


class ShopUnitStatisticsDeleteAPIView(DestroyAPIView):

    model = ShopUnitStatistics
    status_400 = {"code": 400, "message": "Validation Error"}
    status_404 = {"code": 404, "message": "Item not found"}

    def delete(self, request, *args, **kwargs):
        """Delete all statistics of a unit and its descendants"""
        descendants = kwargs["descendants"]

        for unit in descendants:
            unit_id = unit.id
            units_to_delete = self.model.objects.filter(unit_id=unit_id)

            for unit_to_delete in units_to_delete:
                self.perform_destroy(unit_to_delete)

        return Response(status=200)


class ShopUnitDeleteAPIView(DestroyAPIView):

    model = ShopUnit
    model_2 = ShopUnitStatistics
    status_400 = {"code": 400, "message": "Validation Error"}
    status_404 = {"code": 404, "message": "Item not found"}
    shop_unit_statistics_delete = ShopUnitStatisticsDeleteAPIView()

    def delete(self, request, *args, **kwargs):
        """Delete a unit and its descendants from database"""
        unit_id = kwargs["pk"]
        try:
            unit_to_delete = self.model.objects.filter(id=unit_id)
        except:
            return Response(self.status_404, status=404)

        if len(unit_to_delete) == 0:
            return Response(self.status_404)

        instance = unit_to_delete[0]
        descendants = self.model.get_descendants(instance)

        descendants.append(instance)

        kwargs["descendants"] = descendants
        self.shop_unit_statistics_delete.delete(self, request, *args, **kwargs)

        for descendant in descendants:
            self.perform_destroy(descendant)

        return Response(status=200)


class ShopUnitRetrieveAPIView(RetrieveAPIView):
    model = ShopUnit
    serializer_class = ShopUnitSerializer
    status_404 = {"code": 404, "message": "Item not found"}

    def retrieve(self, request, *args, **kwargs):
        """Get all information about a unit"""
        instance_id = kwargs.get("pk")
        try:
            instance = self.model.objects.filter(id=instance_id)
        except ValidationError:
            return Response(self.status_404, status=404)

        if len(instance) == 0:
            return Response(self.status_404, status=404)

        instance = instance[0]
        serialized_instance = self.serializer_class(instance)
        serializer_data = serialized_instance.data

        if instance.type == "CATEGORY":
            children_tree, price, count = self.get_children_tree_and_price(
                instance)
            serializer_data = children_tree
        else:
            serializer_data["children"] = None

        return Response(serializer_data, status=200)

    def get_children_tree_and_price(self, instance):
        """Get a tree of a unit, price of all offers if it is a category and number of offers"""
        serializer = self.serializer_class(instance)
        tree = serializer.data
        tree["children"] = []
        sum_price = 0
        count = 0

        children = self.model.objects.filter(parentId=instance.id)

        for child in children:
            if child.type == "OFFER":
                serialized_child = self.serializer_class(child)
                serialized_child = serialized_child.data
                serialized_child["children"] = None
                tree["children"].append(serialized_child)
                sum_price += child.price
                count += 1
                continue

            tree_add, add_price, add_count = self.get_children_tree_and_price(
                child)
            sum_price += add_price
            count += add_count
            tree["children"].append(tree_add)
        tree["price"] = None if count == 0 else sum_price // count

        return tree, sum_price, count


class SalesAPIView(APIView):
    model = ShopUnitStatistics
    model_2 = ShopUnit
    serializer_class = ShopUnitStatisticsSerializer
    serializer_class_2 = ShopUnitSerializer
    status_400 = {"code": 400, "message": "Validation Error"}

    def get(self, request: Request):
        date_for_sales = request.query_params.get("date")
        try:
            self.validate_date(date_for_sales)
        except:
            return Response(self.status_400, status=400)

        instances = self.model.objects.all()
        results = []

        for instance in instances:
            if instance.type == "OFFER" and self.compare_dates(date_for_sales, instance.date):
                unit_id = instance.unit_id
                shop_unit_instance = self.model_2.objects.get(id=unit_id)
                results.append(shop_unit_instance)

        results = set(results)

        serializer = self.serializer_class_2(results, many=True)

        results = {
            "items": serializer.data
        }

        return Response(results)

    def validate_date(self, item_date):
        if item_date is None:
            raise ValidationError
        try:
            datetime.datetime.fromisoformat(item_date.replace('Z', '+00:00'))
        except:
            raise ValidationError

    def compare_dates(self, first_date, second_date):
        upper_bound = datetime.datetime.fromisoformat(
            first_date.replace('Z', '+00:00'))
        lower_bound = upper_bound - datetime.timedelta(hours=24)
        date = datetime.datetime.fromisoformat(
            second_date.replace('Z', '+00:00'))
        return upper_bound >= date >= lower_bound


class NodeStatisticAPIView(APIView):
    model = ShopUnitStatistics
    model_2 = ShopUnit
    serializer_class = ShopUnitStatisticsSerializer
    status_400 = {"code": 400, "message": "Validation Error"}
    status_404 = {"code": 404, "message": "Item not found"}

    def get(self, request, *args, **kwargs):
        unit_id = kwargs.get("pk")
        date_start = request.query_params.get("dateStart")
        date_end = request.query_params.get("dateEnd")

        try:
            self.validate_date(date_start)
            self.validate_date(date_end)
        except:
            return Response(self.status_400, status=400)

        statistics = self.model.objects.filter(unit_id=unit_id)

        if len(statistics) == 0:
            return Response(self.status_404, status=404)

        results_serialized = []

        for stat in statistics:
            if not self.compare_dates(date_start, date_end, stat.date):
                continue
            if stat.type == "OFFER":
                data = self.serializer_class(stat).data
                del data["id"]
                results_serialized.append(data)
                continue
            shop_unit_instance = self.model_2.objects.get(id=stat.unit_id)
            sum_price, count = self.get_children_price(shop_unit_instance)
            data = self.serializer_class(stat).data
            data["price"] = None if count == 0 else sum_price // count
            del data["id"]
            results_serialized.append(data)

        results = {
            "items": results_serialized
        }

        return Response(results, status=200)

    def get_children_price(self, instance):
        sum_price = 0
        count = 0

        children = self.model_2.objects.filter(parentId=instance.id)

        for child in children:
            if child.type == "OFFER":
                sum_price += child.price
                count += 1
                continue
            print("here")

            add_price, add_count = self.get_children_price(child)
            sum_price += add_price
            count += add_count

        return sum_price, count

    def validate_date(self, item_date):
        if item_date is None:
            raise ValidationError
        try:
            datetime.datetime.fromisoformat(item_date.replace('Z', '+00:00'))
        except:
            raise ValidationError

    def compare_dates(self, lower_bound, upper_bound, date):
        upper_bound = datetime.datetime.fromisoformat(
            upper_bound.replace('Z', '+00:00'))
        lower_bound = datetime.datetime.fromisoformat(
            lower_bound.replace('Z', '+00:00'))
        date = datetime.datetime.fromisoformat(date.replace('Z', '+00:00'))
        return upper_bound >= date >= lower_bound

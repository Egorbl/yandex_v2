import enum
import pprint
from uuid import UUID
from django.test import TestCase
import requests

API_BASEURL = "http://0.0.0.0:80"

imports_200 = [
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Смартфоны",
                "id": 'f7575547-2eae-4f3f-9d27-423a57e133a3'
            },
            {
                "type": "OFFER",
                "name": "jPhone 13",
                "id": '955d67c0-e544-4774-a886-2224636c6c8e',
                "parentId": 'f7575547-2eae-4f3f-9d27-423a57e133a3',
                "price": 79999
            },
            {
                "type": "OFFER",
                "name": "Xomiа Readme 10",
                "id": '31246f85-2089-4621-bf73-c7807e3ad179',
                "parentId": 'f7575547-2eae-4f3f-9d27-423a57e133a3',
                "price": 59999
            }
        ],
        "updateDate": "2022-02-02T12:00:00.000Z"
    },
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Телевизоры",
                "id": '69a1fdd0-a293-4008-b6ca-d8a6f2e92a3e'
            },
            {
                "type": "CATEGORY",
                "name": "Тонкие телевизоры",
                "id": 'a076a0d0-215a-4826-b777-8ab49b5373b7',
                "parentId": '69a1fdd0-a293-4008-b6ca-d8a6f2e92a3e'
            },
            {
                "type": "OFFER",
                "name": "Телевизор HP",
                "id": 'e2d7c5ac-ff12-4355-a321-f22330fbb8dc',
                "parentId": 'a076a0d0-215a-4826-b777-8ab49b5373b7',
                "price": 59999
            },
            {
                "type": "OFFER",
                "name": "Самсунг Телефон",
                "id": 'c2a31894-696e-4643-b617-c70c7242f33b',
                "parentId": 'f7575547-2eae-4f3f-9d27-423a57e133a3',
                "price": 59999
            }
        ],
        "updateDate": "2022-02-02T12:00:00.000Z"
    }
]

imports_400 = [
    {  # 1. Changing type from category to offer
        "items": [
            {
                "type": "OFFER",
                "name": "Телевизоры",
                "id": '69a1fdd0-a293-4008-b6ca-d8a6f2e92a3e',
                "price": 233
            }
        ],
        "updateDate": "2022-02-02T12:00:00.000Z"
    },
    {  # 2. Uuid is unique in 1 request
        "items": [
            {
                "id": '3cf0e803-3cbf-4a34-a8c0-37f0c4c0737b',
                "name": "Оффер",
                "price": 234,
                "type": "OFFER"
            },
            {
                "id": '3cf0e803-3cbf-4a34-a8c0-37f0c4c0737b',
                "name": "Оффер",
                "price": 235,
                "type": "OFFER"
            }
        ],
        "updateDate": "2022-05-28T21:12:01.000Z"
    },
    {  # 3. Parent not exists
        "items": [
            {
                "id": 'e9457a00-9356-40ba-99b2-0d6eef42cd32',
                "name": "Оффер",
                "price": 234,
                "parentId": "abracadabra",
                "type": "OFFER"
            }
        ],
        "updateDate": "2022-05-28T21:12:01.000Z"
    },
    {  # 4. Name cannot be blank
        "items": [
            {
                "id": 'dd330e82-1d38-4e5d-9786-e0014fdb8719',
                "price": 234,
                "type": "OFFER"
            }
        ],
        "updateDate": "2022-05-28T21:12:01.000Z"
    },
    {  # 5. Name cannot be null
        "items": [
            {
                "id": 'e741443f-213b-4961-accc-52098dc5708f',
                "name": None,
                "price": 234,
                "type": "OFFER"
            }
        ],
        "updateDate": "2022-05-28T21:12:01.000Z"
    },
    {  # 6. Price for category
        "items": [
            {
                "id": '60e43d03-27db-419d-be13-2b0a63d57fff',
                "price": 234,
                "type": "CATEGORY",
                "name": "Haha"
            }
        ],
        "updateDate": "2022-05-28T21:12:01.000Z"
    },
    {  # 7. Blank price for not existing offer
        "items": [
            {
                "id": '5bb8968c-f13f-43c9-abf4-0795dc54ef04',
                "type": "OFFER",
                "name": "Haha"
            }
        ],
        "updateDate": "2022-05-28T21:12:01.000Z"
    },
    {  # 8. Null price for not existing offer
        "items": [
            {
                "id": 'b5890c25-5d98-421a-9811-b05f0718cf53',
                "type": "OFFER",
                "name": "Haha",
                "price": None
            }
        ],
        "updateDate": "2022-05-28T21:12:01.000Z"
    },
    {  # 9. Price < 0 for offer
        "items": [
            {
                "id": 'aceedb3c-68f5-4c19-a007-9661c75ef530',
                "type": "OFFER",
                "name": "Haha",
                "price": -123
            }
        ],
        "updateDate": "2022-05-28T21:12:01.000Z"
    },
    {  # 10. Uuid is null
        "items": [
            {
                "type": "OFFER",
                "name": "Haha",
                "price": 123
            }
        ],
        "updateDate": "2022-05-28T21:12:01.000Z"
    },
    {  # 11. Id is not uuid
        "items": [
            {
                "type": "OFFER",
                "name": "Haha",
                "price": 123,
                "id": "1"
            }
        ],
        "updateDate": "2022-05-28T21:12:01.000Z"
    },  # 12. Parent id is not uuid
    {
        "items": [
            {
                "type": "OFFER",
                "name": "Haha",
                "price": 123,
                "id": 'e9457a00-9356-40ba-99b2-0d6eef42cd32',
                "parentId": "1"
            }
        ],
        "updateDate": "2022-05-28T21:12:01.000Z"
    }
]

imports_for_tree = [
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Электроника",
                "id": 'ecd181b5-5238-4bf9-942e-acc51690309a'
            },
            {
                "type": "CATEGORY",
                "name": "Бытовая техника",
                "id": 'b0ae7e94-4e87-492a-a9ff-fd3a715a0f04',
                "parentId": 'ecd181b5-5238-4bf9-942e-acc51690309a'
            }
        ],
        "updateDate": "2021-01-01T00:00:00.000Z"
    },
    {
        "items": [
            {
                "type": "OFFER",
                "name": "Видеокарта NVIDEA",
                "price": 99999999,
                "id": '7a6dc435-1b23-47b9-a0be-0b08cc461676',
                "parentId": 'ecd181b5-5238-4bf9-942e-acc51690309a'
            }
        ],
        "updateDate": "2022-01-01T00:00:00.000Z"
    },
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Холодильники",
                "id": '92f6e9ae-a857-4427-ad54-efa7fc471792',
                "parentId": 'b0ae7e94-4e87-492a-a9ff-fd3a715a0f04'
            },
            {
                "type": "OFFER",
                "name": "Холодильник Bosh",
                "price": 12345,
                "id": '97252990-14ca-430e-be9e-f73953b8aaba',
                "parentId": '92f6e9ae-a857-4427-ad54-efa7fc471792'
            }
        ],
        "updateDate": "2023-01-01T00:00:00.000Z"
    },
    {
        "items": [
            {
                "type": "OFFER",
                "name": "Микроволновка Bosh",
                "price": 10000,
                "id": '53c948c3-3d4e-450c-ac5f-d75a62b9faca',
                "parentId": 'b0ae7e94-4e87-492a-a9ff-fd3a715a0f04'
            },
            {
                "type": "OFFER",
                "name": "Холодильник прямиком с рынка",
                "price": 20000,
                "id": 'a06ca838-adde-4ff3-86bf-a347de5be5d1',
                "parentId": '92f6e9ae-a857-4427-ad54-efa7fc471792'
            },
            {
                "type": "OFFER",
                "name": "Холодильник Pavilion",
                "price": 30000,
                "id": '824dfc5d-4538-4a3d-a99e-7d64938369c5',
                "parentId": '92f6e9ae-a857-4427-ad54-efa7fc471792'
            }
        ],
        "updateDate": "2024-01-01T00:00:00.000Z"
    }
]

correct_tree = {
    "id": 'ecd181b5-5238-4bf9-942e-acc51690309a',
    "name": "Электроника",
    "date": "2024-01-01T00:00:00.000Z",
    "parentId": None,
    "type": "CATEGORY",
    "price": 20014468,
    "children": [
        {
            "id": 'b0ae7e94-4e87-492a-a9ff-fd3a715a0f04',
            "name": "Бытовая техника",
            "date": "2024-01-01T00:00:00.000Z",
            "parentId": 'ecd181b5-5238-4bf9-942e-acc51690309a',
            "type": "CATEGORY",
            "price": 18086,
            "children": [
                {
                    "id": '92f6e9ae-a857-4427-ad54-efa7fc471792',
                    "name": "Холодильники",
                    "date": "2024-01-01T00:00:00.000Z",
                    "parentId": 'b0ae7e94-4e87-492a-a9ff-fd3a715a0f04',
                    "type": "CATEGORY",
                    "price": 20781,
                    "children": [
                        {
                            "id": '97252990-14ca-430e-be9e-f73953b8aaba',
                            "name": "Холодильник Bosh",
                            "date": "2023-01-01T00:00:00.000Z",
                            "parentId": '92f6e9ae-a857-4427-ad54-efa7fc471792',
                            "type": "OFFER",
                            "price": 12345,
                            "children": None
                        },
                        {
                            "id": 'a06ca838-adde-4ff3-86bf-a347de5be5d1',
                            "name": "Холодильник прямиком с рынка",
                            "date": "2024-01-01T00:00:00.000Z",
                            "parentId": '92f6e9ae-a857-4427-ad54-efa7fc471792',
                            "type": "OFFER",
                            "price": 20000,
                            "children": None
                        },
                        {
                            "id": '824dfc5d-4538-4a3d-a99e-7d64938369c5',
                            "name": "Холодильник Pavilion",
                            "date": "2024-01-01T00:00:00.000Z",
                            "parentId": '92f6e9ae-a857-4427-ad54-efa7fc471792',
                            "type": "OFFER",
                            "price": 30000,
                            "children": None
                        }
                    ]
                },
                {
                    "id": '53c948c3-3d4e-450c-ac5f-d75a62b9faca',
                    "name": "Микроволновка Bosh",
                    "date": "2024-01-01T00:00:00.000Z",
                    "parentId": 'b0ae7e94-4e87-492a-a9ff-fd3a715a0f04',
                    "type": "OFFER",
                    "price": 10000,
                    "children": None
                }
            ]
        },
        {
            "id": '7a6dc435-1b23-47b9-a0be-0b08cc461676',
            "name": "Видеокарта NVIDEA",
            "date": "2022-01-01T00:00:00.000Z",
            "parentId": 'ecd181b5-5238-4bf9-942e-acc51690309a',
            "type": "OFFER",
            "price": 99999999,
            "children": None
        }
    ]
}


tree_after_delete = {
    "id": 'ecd181b5-5238-4bf9-942e-acc51690309a',
    "name": "Электроника",
    "date": "2024-01-01T00:00:00.000Z",
    "parentId": None,
    "type": "CATEGORY",
    "price": 10000,
    "children": [
        {
            "id": 'b0ae7e94-4e87-492a-a9ff-fd3a715a0f04',
            "name": "Бытовая техника",
            "date": "2024-01-01T00:00:00.000Z",
            "parentId": 'ecd181b5-5238-4bf9-942e-acc51690309a',
            "type": "CATEGORY",
            "price": 10000,
            "children": [
                {
                    "id": '53c948c3-3d4e-450c-ac5f-d75a62b9faca',
                    "name": "Микроволновка Bosh",
                    "date": "2024-01-01T00:00:00.000Z",
                    "parentId": 'b0ae7e94-4e87-492a-a9ff-fd3a715a0f04',
                    "type": "OFFER",
                    "price": 10000,
                    "children": None
                }
            ]
        }
    ]
}

imports_for_sales = [
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Электроника",
                "id": '1cd181b5-5238-4bf9-942e-acc51690309a'
            },
            {
                "type": "CATEGORY",
                "name": "Бытовая техника",
                "id": '10ae7e94-4e87-492a-a9ff-fd3a715a0f04',
                "parentId": '1cd181b5-5238-4bf9-942e-acc51690309a'
            }
        ],
        "updateDate": "2021-01-01T00:00:00.000Z"
    },
    {
        "items": [
            {
                "type": "OFFER",
                "name": "Видеокарта NVIDEA",
                "price": 99999999,
                "id": '1a6dc435-1b23-47b9-a0be-0b08cc461676',
                "parentId": '1cd181b5-5238-4bf9-942e-acc51690309a'
            }
        ],
        "updateDate": "2022-01-01T00:00:00.000Z"
    },
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Холодильники",
                "id": '12f6e9ae-a857-4427-ad54-efa7fc471792',
                "parentId": '10ae7e94-4e87-492a-a9ff-fd3a715a0f04'
            },
            {
                "type": "OFFER",
                "name": "Холодильник Bosh",
                "price": 12345,
                "id": '17252990-14ca-430e-be9e-f73953b8aaba',
                "parentId": '12f6e9ae-a857-4427-ad54-efa7fc471792'
            }
        ],
        "updateDate": "2023-01-01T00:00:00.000Z"
    },
    {
        "items": [
            {
                "type": "OFFER",
                "name": "Микроволновка Bosh",
                "price": 10000,
                "id": '13c948c3-3d4e-450c-ac5f-d75a62b9faca',
                "parentId": '10ae7e94-4e87-492a-a9ff-fd3a715a0f04'
            },
            {
                "type": "OFFER",
                "name": "Холодильник прямиком с рынка",
                "price": 20000,
                "id": '106ca838-adde-4ff3-86bf-a347de5be5d1',
                "parentId": '12f6e9ae-a857-4427-ad54-efa7fc471792'
            },
            {
                "type": "OFFER",
                "name": "Холодильник Pavilion",
                "price": 30000,
                "id": '124dfc5d-4538-4a3d-a99e-7d64938369c5',
                "parentId": '12f6e9ae-a857-4427-ad54-efa7fc471792'
            }
        ],
        "updateDate": "2024-01-01T00:00:00.000Z"
    }
]

imports_for_sales_update = [
    {
        "items": [
            {
                "id": "106ca838-adde-4ff3-86bf-a347de5be5d1",
                "name": "Холодильник прямиком с рынка",
                "parentId": "12f6e9ae-a857-4427-ad54-efa7fc471792",
                "type": "OFFER",
                "price": 15000
            },
            {
                "id": "124dfc5d-4538-4a3d-a99e-7d64938369c5",
                "name": "Холодильник Pavilion",
                "parentId": "12f6e9ae-a857-4427-ad54-efa7fc471792",
                "type": "OFFER",
                "price": 35000
            },
            {
                "id": "1a6dc435-1b23-47b9-a0be-0b08cc461676",
                "name": "Видеокарта NVIDEA",
                "parentId": "1cd181b5-5238-4bf9-942e-acc51690309a",
                "type": "OFFER",
                "price": 99999
            }
        ],
        "updateDate": "2027-01-01T00:00:00.000Z"
    },
    {
        "items": [
            {
                "id": "106ca838-adde-4ff3-86bf-a347de5be5d1",
                "name": "Холодильник прямиком с рынка",
                "parentId": "12f6e9ae-a857-4427-ad54-efa7fc471792",
                "type": "OFFER",
                "price": 16000
            }
        ],
        "updateDate": "2027-01-01T00:00:00.000Z"
    }
]

sales_correct = {
    "items": [
        {
            "id": "1a6dc435-1b23-47b9-a0be-0b08cc461676",
            "name": "Видеокарта NVIDEA",
            "date": "2027-01-01T00:00:00.000Z",
            "parentId": "1cd181b5-5238-4bf9-942e-acc51690309a",
            "type": "OFFER",
            "price": 99999
        },
        {
            "id": "106ca838-adde-4ff3-86bf-a347de5be5d1",
            "name": "Холодильник прямиком с рынка",
            "date": "2027-01-01T00:00:00.000Z",
            "parentId": "12f6e9ae-a857-4427-ad54-efa7fc471792",
            "type": "OFFER",
            "price": 16000
        },
        {
            "id": "124dfc5d-4538-4a3d-a99e-7d64938369c5",
            "name": "Холодильник Pavilion",
            "date": "2027-01-01T00:00:00.000Z",
            "parentId": "12f6e9ae-a857-4427-ad54-efa7fc471792",
            "type": "OFFER",
            "price": 35000
        }
    ]
}

category_import = [
    {
        "items": [
            {
                "id": "106ca838-adde-4ff3-86bf-a347de5be510",
                "name": "Телефоны",
                "type": "CATEGORY"
            },
            {
                "id": "124dfc5d-4538-4a3d-a99e-7d64938369c5",
                "name": "Холодильник Pavilion",
                "parentId": "12f6e9ae-a857-4427-ad54-efa7fc471792",
                "type": "OFFER",
                "price": 35000
            },
            {
                "id": "1a6dc435-1b23-47b9-a0be-0b08cc461676",
                "name": "Видеокарта NVIDEA",
                "parentId": "1cd181b5-5238-4bf9-942e-acc51690309a",
                "type": "OFFER",
                "price": 99999
            }
        ],
        "updateDate": "2027-01-01T00:00:00.000Z"
    },
    {
        "items": [
            {
                "id": "106ca838-adde-4ff3-86bf-a347de5be5d1",
                "name": "Холодильник прямиком с рынка",
                "parentId": "12f6e9ae-a857-4427-ad54-efa7fc471792",
                "type": "OFFER",
                "price": 16000
            }
        ],
        "updateDate": "2027-01-01T00:00:00.000Z"
    }
]

node_statistic_first_correct = {
    "items": [{'unit_id': '106ca838-adde-4ff3-86bf-a347de5be5d1', 'name': 'Холодильник прямиком с рынка', 'date': '2027-01-01T00:00:00.000Z', 'parentId': '12f6e9ae-a857-4427-ad54-efa7fc471792', 'type': 'OFFER',
               'price': 15000}, {'unit_id': '106ca838-adde-4ff3-86bf-a347de5be5d1', 'name': 'Холодильник прямиком с рынка', 'date': '2027-01-01T00:00:00.000Z', 'parentId': '12f6e9ae-a857-4427-ad54-efa7fc471792', 'type': 'OFFER', 'price': 16000}]
}


def deep_sort_children(node):
    if node.get("children"):
        node["children"].sort(key=lambda x: x["id"])

        for child in node["children"]:
            deep_sort_children(child)


def test_imports_200():
    for index, import_test in enumerate(imports_200):
        response = requests.post(API_BASEURL + "/imports", json=import_test)
        print(f"Proceeding {index + 1} test")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("import test (200). Success")


def test_imports_400():
    for index, import_test in enumerate(imports_400):
        response = requests.post(API_BASEURL + "/imports", json=import_test)
        print(f"Proceeding {index + 1} test")
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    print("import test (400). Success")


def test_imports_for_tree():
    for index, import_test in enumerate(imports_for_tree):
        response = requests.post(API_BASEURL + "/imports", json=import_test)
        print(f"Proceeding {index + 1} test")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    tree_by_request = requests.get(
        API_BASEURL + "/nodes/ecd181b5-5238-4bf9-942e-acc51690309a")
    tree = tree_by_request.json()
    deep_sort_children(correct_tree)
    deep_sort_children(tree)
    assert correct_tree == tree, print("Your tree: ", tree_by_request.json(),
                                       "\n", "Correct tree: ", correct_tree)
    print("Getting nodes: success")


def test_delete():
    unit_to_delete = ['7a6dc435-1b23-47b9-a0be-0b08cc461676',
                      '92f6e9ae-a857-4427-ad54-efa7fc471792']

    for unit in unit_to_delete:
        requests.delete(API_BASEURL + f"/delete/{unit}")

    response = requests.get(
        API_BASEURL + "/nodes/ecd181b5-5238-4bf9-942e-acc51690309a")
    assert tree_after_delete == response.json(), print("Your tree: ", response.json(),
                                                       "\n", "Correct tree: ", tree_after_delete)
    print("Delete: success")


def test_incorrect_node():
    response = requests.get(API_BASEURL + "/nodes/invalid")
    assert response.status_code == 404, print(
        f"Expected status 404, got {response.status_code}")


def test_incorrect_delete():
    response = requests.delete(API_BASEURL + "/delete/invalid")
    assert response.status_code == 404, print(
        f"Expected status 404, got {response.status_code}")


def import_sales_info():
    print("Importing units for sales test")

    for index, new_units in enumerate(imports_for_sales):
        response = requests.post(API_BASEURL + "/imports", json=new_units)
        print(f"Proceeding {index + 1} test")
        assert response.status_code == 200, print(
            f"Expected 200 while importing, got {response.status_code}")

    print("Updating units for sales test")

    for index, new_units in enumerate(imports_for_sales_update):
        response = requests.post(API_BASEURL + "/imports", json=new_units)
        print(f"Proceeding {index + 1} test")
        assert response.status_code == 200, print(
            f"Expected 200 while importing, got {response.status_code}")


def test_sales():

    response = requests.get(API_BASEURL + "/sales", params={
        "date": "2027-01-01T10:00:00.000Z"
    })
    assert response.status_code == 200, print(
        f"Expected status 200, got {response.status_code}")
    tree = response.json()
    deep_sort_children(sales_correct)
    deep_sort_children(tree)
    assert tree == sales_correct, print(
        f"Sales list is not correct \n Your result: \n {response.json()} \n Correct result: \n {sales_correct}")
    print("Sales test: Success")


def test_node_statistic():
    print("Testing node statistic")
    response = requests.get(API_BASEURL + "/node/106ca838-adde-4ff3-86bf-a347de5be5d1/statistic", params={
        "dateStart": "2026-01-01T10:00:00.000Z",
        "dateEnd": "2028-01-01T10:00:00.000Z"
    })
    assert response.status_code == 200, print(
        f"Expected status code 200, got {response.status_code}")
    tree = response.json()
    deep_sort_children(node_statistic_first_correct)
    deep_sort_children(tree)
    assert tree == node_statistic_first_correct, \
        print(
            f"Node statistic is not correct \n Your result: \n {tree} \n Correct result: \n + {node_statistic_first_correct}")

    print("Node statistic: Success")


def test_category_statistic():
    pass


def main():
    test_imports_200()
    test_imports_400()
    test_imports_for_tree()
    test_delete()
    test_incorrect_node()
    test_incorrect_delete()
    import_sales_info()
    test_sales()
    test_node_statistic()
    test_category_statistic()


if __name__ == "__main__":
    main()

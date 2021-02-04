from fastapi.testclient import TestClient
from myapp.base.tools import generate_random_str
from myapp.main import app

client = TestClient(app)

user_example = {
    "display_name": "test_user1",
    "login_name": "test_user" + generate_random_str(2),
    "desc": "test_desc1",
    "password": "password"
}

header = {
    "Authorization": ""
}


def login():
    response = client.post("/auth/token", data={"username": "admin", "password": "password", "grant_type": "password"})
    assert response.status_code == 200
    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"
    return response_data["token_type"], response_data["access_token"]


def test_crud():
    token = login()
    header["Authorization"] = token[0] + " " + token[1]

    # create 210
    response = client.post("/users/", json=user_example, headers=header)
    assert response.status_code == 201
    response_data = response.json()
    assert "data" in response_data
    assert "code" in response_data
    assert "message" in response_data
    assert response_data["data"]["desc"] == user_example["desc"]

    user_uuid = response_data["data"]["uuid"]

    # create 422
    missing_user_example = {"display_": "test_name1", "login_name": False, "desc": "test_desc1"}
    response = client.post("/users/", json=missing_user_example, headers=header)
    assert response.status_code == 422
    response_data = response.json()
    assert "data" in response_data
    assert bool(response_data["message"])
    assert bool(response_data["code"])

    # list 200
    response = client.get("/users/", headers=header)
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data["data"], list)
    response_data["data"].sort(key=lambda k: k.get('created_at', 0), reverse=True)
    assert response_data["data"][0]["desc"] == user_example["desc"]

    # get 200
    response = client.get(f"/users/{user_uuid}", headers=header)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["data"]["desc"] == user_example["desc"]

    # get 404
    response = client.get("/users/1111", headers=header)
    assert response.status_code == 404
    response_data = response.json()
    assert "data" in response_data
    assert bool(response_data["message"])
    assert bool(response_data["code"])

    # patch 200
    response = client.patch(f"/users/{user_uuid}", json={"display_name": "display_name_patched"}, headers=header)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["data"]["display_name"] == "display_name_patched"

    # patch 404
    response = client.patch("/users/1111", json={"display_name": "display_name_patched"}, headers=header)
    assert response.status_code == 404
    response_data = response.json()
    assert "data" in response_data
    assert bool(response_data["message"])
    assert bool(response_data["code"])

    # patch 422
    wrong_user_example = {"display_": "test_name1", "desc": "test_desc1"}
    response = client.patch(f"/users/{user_uuid}", json=wrong_user_example, headers=header)
    assert response.status_code == 422
    response_data = response.json()
    assert "data" in response_data
    assert bool(response_data["message"])
    assert bool(response_data["code"])

    # delete 200
    response = client.delete(f"/users/{user_uuid}", headers=header)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["data"].get("display_name") is None

    # delete 404
    response = client.delete("/users/1111", headers=header)
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["data"].get("display_name") is None




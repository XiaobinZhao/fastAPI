from fastapi.testclient import TestClient
from myapp.main import app

client = TestClient(app)

desktop_example = {
  "display_name": "test_name1",
  "is_default": False,
  "desc": "test_desc1"
}


def test_crud():
    # create 422
    missing_desktop_example = {"display_": "test_name1", "is_default": False, "desc": "test_desc1"}
    response = client.post("/desktops/", json=missing_desktop_example)
    assert response.status_code == 422
    response_data = response.json()
    assert "data" in response_data
    assert bool(response_data["message"])
    assert bool(response_data["code"])

    # create 210
    response = client.post("/desktops/", json=desktop_example)
    assert response.status_code == 201
    response_data = response.json()
    assert "data" in response_data
    assert "code" in response_data
    assert "message" in response_data
    assert response_data["data"]["desc"] == desktop_example["desc"]

    desktop_uuid = response_data["data"]["uuid"]

    # list 200
    response = client.get("/desktops/")
    assert response.status_code == 200
    response_data = response.json()
    assert isinstance(response_data["data"], list)
    response_data["data"].sort(key=lambda k: k.get('created_at', 0), reverse=True)
    assert response_data["data"][0]["desc"] == desktop_example["desc"]

    # get 200
    response = client.get(f"/desktops/{desktop_uuid}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["data"]["desc"] == desktop_example["desc"]

    # get 404
    response = client.get("/desktops/1111")
    assert response.status_code == 404
    response_data = response.json()
    assert "data" in response_data
    assert bool(response_data["message"])
    assert bool(response_data["code"])

    # patch 200
    desktop_example["display_name"] = "display_name_patched"
    response = client.patch(f"/desktops/{desktop_uuid}", json=desktop_example)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["data"]["display_name"] == "display_name_patched"

    # patch 404
    response = client.patch("/desktops/1111", json=desktop_example)
    assert response.status_code == 404
    response_data = response.json()
    assert "data" in response_data
    assert bool(response_data["message"])
    assert bool(response_data["code"])

    # patch 422
    wrong_desktop_example = {"display_": "test_name1", "is_default": False, "desc": "test_desc1"}
    response = client.patch(f"/desktops/{desktop_uuid}", json=wrong_desktop_example)
    assert response.status_code == 422
    response_data = response.json()
    assert "data" in response_data
    assert bool(response_data["message"])
    assert bool(response_data["code"])

    # delete 200
    desktop_example["display_name"] = "display_name_patched"
    response = client.delete(f"/desktops/{desktop_uuid}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["data"].get("display_name") is None

    # delete 404
    desktop_example["display_name"] = "display_name_patched"
    response = client.delete("/desktops/1111")
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["data"].get("display_name") is None




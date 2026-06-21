import pytest

RECIPE_PAYLOAD = {
    "title": "Tarte aux pommes",
    "instructions": "Éplucher, couper, cuire 35 min.",
    "prep_time": 20,
    "cook_time": 35,
    "servings": 6,
}

@pytest.fixture
def created_recipe(client):
    response = client.post("/api/v1/recipes/", json=RECIPE_PAYLOAD)
    return response.json()

def test_create_recipe(client):
    response = client.post("/api/v1/recipes/", json=RECIPE_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == RECIPE_PAYLOAD["title"]
    assert "id" in data
    assert "created_at" in data

def test_get_recipe(client, created_recipe):
    recipe_id = created_recipe["id"]
    response = client.get(f"/api/v1/recipes/{recipe_id}")
    assert response.status_code == 200
    assert response.json()["title"] == RECIPE_PAYLOAD["title"]

def test_get_recipe_not_found(client):
    response = client.get("/api/v1/recipes/999")
    assert response.status_code == 404

def test_list_recipes(client, created_recipe):
    response = client.get("/api/v1/recipes/")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_update_recipe(client, created_recipe):
    recipe_id = created_recipe["id"]
    response = client.patch(
        f"/api/v1/recipes/{recipe_id}",
        json={"title": "Tarte aux poires"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Tarte aux poires"
    assert data["instructions"] == RECIPE_PAYLOAD["instructions"]

def test_delete_recipe(client, created_recipe):
    recipe_id = created_recipe["id"]
    response = client.delete(f"/api/v1/recipes/{recipe_id}")
    assert response.status_code == 204
    response = client.get(f"/api/v1/recipes/{recipe_id}")
    assert response.status_code == 404


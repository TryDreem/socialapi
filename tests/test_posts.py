import pytest


@pytest.mark.asyncio
async def test_create_post(client, auth_headers):
    response = await client.post(
        "/post",
        json={"body": "Test post"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["body"] == "Test post"
    assert "id" in data



@pytest.mark.asyncio
async def test_get_posts_pagination(client, auth_headers):
    for i in range(10):
        await client.post(
            "/post",
            json={"body": f"Test {i}"},
            headers=auth_headers
        )
    response = await client.get("/post?page=1&page_size=3")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    assert data["total"] == 10
    assert data["total_pages"] == 4


@pytest.mark.asyncio
async def test_get_post(client, auth_headers):
    create_response = await client.post(
        "/post",
        json={"body": "Test post"},
        headers=auth_headers
    )

    post_id = create_response.json()["id"]

    response = await client.get(f"/post/{post_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["body"] == "Test post"



@pytest.mark.asyncio
async def test_get_wrong_post(client, auth_headers):
    create_response = await client.post(
        "/post",
        json={"body": "Test post"},
        headers=auth_headers
    )

    post_id = create_response.json()["id"]

    response = await client.get(f"/post/{post_id}1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Post not found"}



@pytest.mark.asyncio
async def test_delete_post(client, auth_headers):

    create_response = await client.post(
        "/post",
        json={"body": "Test post"},
        headers=auth_headers
    )

    post_id = create_response.json()["id"]

    response = await client.delete(
        f"/post/{post_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200


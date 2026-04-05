import pytest

@pytest.mark.asyncio
async def test_follow_user(client, auth_headers,auth_headers2):
    user = await client.get("/auth/me", headers=auth_headers)

    user_id = user.json()["id"]

    response = await client.post(
        f"/users/{user_id}/follow", headers=auth_headers2
    )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_follow_user_twice(client, auth_headers,auth_headers2):
    user = await client.get("/auth/me", headers=auth_headers)

    user_id = user.json()["id"]

    await client.post(
        f"/users/{user_id}/follow", headers=auth_headers2
    )


    response = await client.post(
        f"/users/{user_id}/follow", headers=auth_headers2
    )

    assert response.status_code == 409



@pytest.mark.asyncio
async def test_follow_yourself(client, auth_headers):
    user = await client.get("/auth/me", headers=auth_headers)
    user_id = user.json()["id"]

    response = await client.post(
        f"/users/{user_id}/follow", headers=auth_headers
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_unfollow_user(client, auth_headers, auth_headers2):
    user = await client.get("/auth/me", headers=auth_headers)
    user_id = user.json()["id"]
    await client.post(
        f"/users/{user_id}/follow", headers=auth_headers2
    )

    unfollow = await client.delete(
        f"/users/{user_id}/follow", headers=auth_headers2
    )

    assert unfollow.status_code == 204


@pytest.mark.asyncio
async def test_get_followers(client, auth_headers):
    user = await client.get("/auth/me", headers=auth_headers)
    user_id = user.json()["id"]

    response = await client.get(
        f"/users/{user_id}/followers"
    )

    assert response.status_code == 200


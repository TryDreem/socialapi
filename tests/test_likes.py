import pytest


@pytest.mark.asyncio
async def test_like_post(client, auth_headers, test_post):

    post_id = test_post["id"]

    response = await client.post(
        f"/post/{post_id}/like",
        headers=auth_headers,
    )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_unlike_post(client, auth_headers, test_post):

    post_id = test_post["id"]

    await client.post(
        f"/post/{post_id}/like",
        headers=auth_headers,
    )

    unlike = await client.delete(
        f"/post/{post_id}/like",
        headers=auth_headers,
    )

    assert unlike.status_code == 204


@pytest.mark.asyncio
async def test_like_post_twice(client, auth_headers, test_post):
    post_id = test_post["id"]

    await client.post(
        f"/post/{post_id}/like",
        headers=auth_headers,
    )

    response = await client.post(
        f"/post/{post_id}/like",
        headers=auth_headers,
    )

    assert response.status_code == 409


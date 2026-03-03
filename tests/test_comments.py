import pytest


@pytest.mark.asyncio
async def test_create_comment(client,test_post,auth_headers):

    post_id = test_post["id"]

    response = await client.post(
        f"post/{post_id}/comments",
        json={"body": "test comment"},
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["body"] == "test comment"


@pytest.mark.asyncio
async def test_get_comments(client,test_post,auth_headers):

    post_id = test_post["id"]

    await client.post(
        f"post/{post_id}/comments",
        json={"body": "test comment"},
        headers=auth_headers
    )


    response = await client.get(
        f"post/{post_id}/comments?page=1&page_size=3"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["total_pages"] == 1

@pytest.mark.asyncio
async def test_create_comment_wrong_post(client,test_post,auth_headers):

    post_id = 0

    response = await client.post(
        f"post/{post_id}/comments",
        json={"body": "test comment"},
        headers=auth_headers
    )

    assert response.status_code == 404



@pytest.mark.asyncio
async def test_delete_comment(client,test_post,auth_headers):

    post_id = test_post["id"]

    comment = await client.post(
        f"post/{post_id}/comments",
        json={"body": "test comment"},
        headers=auth_headers
    )

    comment_id = comment.json()["id"]

    response = await client.delete(
        f"post/{post_id}/comments/{comment_id}",
        headers=auth_headers
    )

    assert response.status_code == 204


import pytest

@pytest.mark.asyncio
async def test_get_notifications(client, auth_headers):
    response = await client.get("/notification", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_mark_notification_read(client, auth_headers, auth_headers2, db_session):

    from app.models.notification import Notification, NotificationType

    notification = Notification(
        user_id=1,
        actor_id=2,
        type=NotificationType.follow,
        post_id=None,
        is_read=False
    )

    db_session.add(notification)
    await db_session.commit()
    await db_session.refresh(notification)

    n = await client.get("/notification", headers=auth_headers)
    notification_id = n.json()["items"][0]["id"]

    response = await client.patch(
        f"/notification/{notification_id}/read", headers=auth_headers
    )

    assert response.status_code == 200




import pytest


@pytest.mark.asyncio
async def test_register_user(client):
    response = await client.post(
        "/auth/register",
        json={"email": "newuser@gmail.com", "password": "12345678"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@gmail.com"
    assert data["is_confirmed"] is False



@pytest.mark.asyncio
async def test_register_duplicate_user(client, test_user):
    response = await client.post(
        "/auth/register",
        json={"email": test_user["email"], "password": "12345678"},
    )

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client, test_user, db_session):

    from app.models.user import User
    from sqlalchemy import update

    query = update(User).where(User.email == test_user["email"]).values(is_confirmed=True)

    await db_session.execute(query)
    await db_session.commit()

    response = await client.post(
        "/auth/login",
        json=test_user,
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_unconfirmed_email(client, test_user):

    response = await client.post(
        "/auth/login",
        json=test_user,
    )

    assert response.status_code == 400
    assert "not confirmed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_wrong_password(client, test_user, db_session):
    from app.models.user import User
    from sqlalchemy import update

    query = update(User).where(User.email == test_user["email"]).values(is_confirmed=True)

    await db_session.execute(query)
    await db_session.commit()
    response = await client.post(
        "/auth/login",
        json = {
            "email": test_user["email"],
            "password": "wrongpassword",
        }
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_current_user(client, auth_headers):
    response = await client.get(
        "/auth/me",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@gmail.com"




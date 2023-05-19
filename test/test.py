import requests

url = "http://localhost:3000"
cookies = dict()


def test_register_admin(username, password, email):
    data = {
        'username': username,
        'password': password,
        'email': email
    }
    response = requests.post(f"{url}/api/admin/register",
                             json=data,
                             headers={
                                 "content-type": "application/json"
                             }
                             )
    print(response.json())

    assert response.status_code == 201


def test_register_user(username, password, email):
    data = {
        'username': username,
        'password': password,
        'email': email
    }
    response = requests.post(f"{url}/api/user/register",
                             json=data,
                             headers={
                                 "content-type": "application/json"
                             }
                             )
    print(response.json())

    assert response.status_code == 201


def test_get_one_msg_as_admin(msg_id):
    response = requests.get(
        f"{url}/api/messages/{msg_id}",
        cookies=cookies['admin']
    )
    print(response.json())
    assert response.status_code == 200


def test_create_msg_as_admin(msg):
    response = requests.post(
        f"{url}/api/messages",
        json={
            "message": msg
        },
        cookies=cookies['admin']
    )

    print(response.json())
    assert response.status_code == 201


def test_login_admin(username, password):
    response = requests.post(
        f"{url}/api/admin/login",
        auth=(username, password)
    )

    cookies["admin"] = response.cookies
    assert response.status_code == 200


def test_get_all_messages_as_admin():
    response = requests.get(
        f"{url}/api/messages",
        cookies=cookies['admin']
    )

    print(response.json())

    assert response.status_code == 200


def test_login_user(username, password):
    response = requests.post(
        f"{url}/api/user/login",
        auth=(username, password)
    )

    cookies["user"] = response.cookies
    assert response.status_code == 200


def test_create_msg_as_user(msg):
    response = requests.post(
        f"{url}/api/messages",
        json={
            "message": msg
        },
        cookies=cookies['user']
    )

    print(response.json())
    assert response.status_code == 201


def test_logout_admin():
    response = requests.get(
        f"{url}/api/logout",
        cookies=cookies['admin']
    )

    cookies['admin'] = response.cookies

    assert response.status_code == 200


def test_logout_user():
    response = requests.get(
        f"{url}/api/logout",
        cookies=cookies['user']
    )

    cookies['user'] = response.cookies

    assert response.status_code == 200


def test_get_one_msg_as_user(msg_id):
    response = requests.get(
        f"{url}/api/messages/{msg_id}",
        cookies=cookies['user']
    )
    print(response.json())
    assert response.status_code == 200


def test_get_one_msg_as_user_not_accessible(msg_id):
    response = requests.get(
        f"{url}/api/messages/{msg_id}",
        cookies=cookies['user']
    )
    print(response.json())
    assert response.status_code == 403


def test_get_all_messages_as_user():
    response = requests.get(
        f"{url}/api/messages",
        cookies=cookies['user']
    )

    print(response.json())

    assert response.status_code == 200


if __name__ == "__main__":
    test_register_admin("admin1234", "password123##@", "admin@example.com")
    test_login_admin("admin1234", "password123##@")
    test_create_msg_as_admin("hello another msg from admin")
    test_get_one_msg_as_admin(1)
    test_get_all_messages_as_admin()
    test_logout_admin()

    test_register_user("user123", "password123##@", "user@example.com")
    test_login_user("user123", "password123##@")
    test_create_msg_as_user("Hello, this is another message")
    test_get_one_msg_as_user(2)
    test_get_one_msg_as_user_not_accessible(1)
    test_get_all_messages_as_user()
    test_logout_user()

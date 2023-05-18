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


if __name__ == "__main__":
    # test_register_admin("user123", "password123##@", "user@example.com")
    test_login_admin("user123", "password123##@")
    test_create_msg_as_admin("hello another msg from admin")
    test_get_one_msg_as_admin(2)
    test_get_all_messages_as_admin()

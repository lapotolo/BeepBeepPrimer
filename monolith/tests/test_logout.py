from monolith.tests.utility import client, create_user, login, logout


def test_login(client):
    tested_app, app = client

    # logout without log in
    assert logout(tested_app).status_code == 401

    # creates 'marco@prova.it' with psw '123456'
    assert create_user(tested_app).status_code == 200

    # in the db exists 'marco@prova.it' and 'example@example.com' (the admin)

    # logging in correctly
    reply = login(tested_app, email='marco@prova.it', password='123456')
    assert reply.status_code == 200

    # logout correctly
    assert logout(tested_app).status_code == 200

    # trying to access a page the require login
    assert tested_app.get('/delete_user').status_code == 401







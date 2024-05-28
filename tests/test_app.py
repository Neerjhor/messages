import pytest
from fastapi.testclient import TestClient
from messages import create_app
from messages.database import get_database

app = create_app("testing")
client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    get_database().create_db_and_tables()
    yield
    get_database().drop_all_tables()

def setup_user(username):
    client.post("/users/", json={"name": "Alice", "username": f"{username}"})

def send_message(sender_username, recipient_username, content):
    return client.post(f"/users/{recipient_username}/messages/", json={
        "sender_username": f"{sender_username}",
        "content": f"{content}"
    })

def test_create_user_succeeds():
    response = client.post("/users/", json={"name": "Alice", "username": "alice"})
    assert response.status_code == 200
    assert response.json() == {"Message": "User successfully created"}

def test_create_user_fails_with_400_when_username_already_exists():
    client.post("/users/", json={
        "name": "Alice",
        "username": "alice"
    })

    response = client.post("/users/", json={
        "name": "Alice",
        "username": "alice"
    })

    assert response.status_code == 400
    assert "Username already exists" in response.json()["detail"]

def test_create_user_fails_with_400_when_username_is_empty():
    response = client.post("/users/", json={
        "name": "Alice",
        "username": ""
    })

    assert response.status_code == 400
    assert "Username cannot be an empty string" in response.json()["detail"]

def test_send_message_succeeds():
    setup_user("alice")
    setup_user("bob")
    # Send message from Alice to Bob
    response = send_message("alice", "bob", "hej hej")

    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["content"] == "hej hej"
    assert response.json()["sender_username"] == "alice"
    assert response.json()["recipient_username"] == "bob"

def test_send_message_fails_with_404_when_recipient_does_not_exist():
    setup_user("alice")
    # Send message from Alice to Bob
    response = send_message("alice", "bob", "hej hej")

    assert response.status_code == 404
    assert "Recipient does not exist" in response.json()["detail"]

def test_send_message_fails_with_404_when_sender_does_not_exist():
    setup_user("bob")
    # Send message from Alice to Bob
    response = send_message("alice", "bob", "hej hej")

    assert response.status_code == 404
    assert "Sender does not exist" in response.json()["detail"]

def test_get_all_messages_success():
    setup_user("alice")
    setup_user("bob")
    send_message("alice", "bob", "hej hej")
    send_message("alice", "bob", "trevlig att träffas")

    response = client.get("/users/bob/messages/")
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 2
    assert messages[0].get("content") == "hej hej"
    assert messages[1].get("content") == "trevlig att träffas"

def test_get_all_messages_fails_when_user_does_not_exist():
    response = client.get("/users/bob/messages/")

    assert response.status_code == 404
    assert "User does not exist" in response.json()["detail"]
    

def test_get_new_messages_succeeds():
    setup_user("alice")
    setup_user("bob")
    send_message("alice", "bob", "hej hej")
    send_message("alice", "bob", "trevlig att träffas")

    response = client.get("/users/bob/messages/new")
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 2

    send_message("alice", "bob", "vi ses")
    response = client.get("/users/bob/messages/new")
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 1
    assert messages[0].get("content") == "vi ses"

def test_get_new_messages_succeeds_when_no_new_message():
    setup_user("alice")
    setup_user("bob")
    send_message("alice", "bob", "hej hej")
    send_message("alice", "bob", "trevlig att träffas")

    response = client.get("/users/bob/messages/new")
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 2

    response = client.get("/users/bob/messages/new")
    assert response.status_code == 200
    assert response.json() == {"Message": "No new messages."}

def test_delete_message_succeeds():
    setup_user("alice")
    setup_user("bob")
    send_message("alice", "bob", "hej hej")
    send_message("alice", "bob", "trevlig att träffas")
    response_send_message = send_message("alice", "bob", "vi ses")
    message_id = response_send_message.json()["id"]

    response_get_message = client.get("/users/bob/messages/")
    messages = response_get_message.json()
    assert len(messages) == 3

    response_delete_message = client.delete(f"/users/bob/messages/{message_id}")
    assert response_delete_message.status_code == 200
    assert response_delete_message.json() == {"Message": "Message deleted"}

    response_get_message = client.get("/users/bob/messages/")
    messages = response_get_message.json()
    assert len(messages) == 2
    assert not any(message['id'] == message_id for message in messages)

def test_delete_message_fails_when_user_does_not_exist():
    response = client.delete(f"/users/bob/messages/randomid")
    assert response.status_code == 404
    assert "User does not exist" in response.json()["detail"]

def test_delete_message_fails_when_message_does_not_exist():
    setup_user("alice")
    setup_user("bob")
    send_message("alice", "bob", "hej hej")

    response = client.delete(f"/users/bob/messages/randomid")
    assert response.status_code == 404
    assert "No message with this message id exists" in response.json()["detail"]

def test_delete_multiple_messages_success():
    setup_user("alice")
    setup_user("bob")
    send_message("alice", "bob", "hej hej")
    response_send_message_1 = send_message("alice", "bob", "trevlig att träffas")
    response_send_message_2 = send_message("alice", "bob", "vi ses")
    message_id_1 = response_send_message_1.json()["id"]
    message_id_2 = response_send_message_2.json()["id"]

    response_get_message = client.get("/users/bob/messages/")
    messages = response_get_message.json()
    assert len(messages) == 3

    # Because client.delete doesn't allow a payload anymore.
    response_delete_message = client.request("DELETE", "/users/bob/messages/", json={"message_ids": [f"{message_id_1}", f"{message_id_2}"]})
    assert response_delete_message.status_code == 200
    assert response_delete_message.json() == {"Message": "Messages deleted"}

    response_get_message = client.get("/users/bob/messages/")
    messages = response_get_message.json()
    assert len(messages) == 1
    assert not any(message['id'] == message_id_1 for message in messages)
    assert not any(message['id'] == message_id_2 for message in messages)


# Messages

## Installation

**With python**

```shell
$ git clone https://github.com/Neerjhor/messages.git
$ cd messages
$ python3 -m venv myenv
$ source myenv/bin/activate
$ pip3 install -r requirements.txt
$ python run.py
```

## Description

Users need to be created before sending or getting messages. If messages are sent to a non-existent user, then error will be thrown. Similarly, to get messages for a user, that user needs to be created.

The unique identifier for each user is their username. No two user can be created with the same username.

## API Usage

### Create a new user

**Definition**

`POST /users/`

**Request**

content-type: application/json

Body data should be a json object with the following fields

- `"name" : string` the name of the user
- `"username" : string` the username of the user (this cannot be empty)

Ex:
```json
{
    "name": "Alice",
    "username": "alice"
}
```

**Response**

- `200 OK` on success

```json
{
    "Message" : "User successfully created.",
}
```

- `400 BAD_REQUEST` on failure on duplicate user

```json
{
    "detail" : "Username already exists.",
}
```

- `400 BAD_REQUEST` on failure on empty username

```json
{
    "detail" : "Username cannot be an empty string.",
}
```

### Submit a new message to user

**Definition**

`POST /users/<username>/messages`

**Request**

content-type: application/json

Body data should be a json object with the following fields

- `"sender_username" : string` the username of the sender
- `"content" : string` message content

Ex:
```json
{
    "sender_username": "alice",
    "content": "hej hej"
}
```

**Response**

- `200 OK` on success

```json
{
    "sender_username": "alice",
    "recipient_username" : "bob",
    "timestamp": "2024-05-24T15:27:14.459730",
    "content": "hej hej",
    "id" : "some_uuid"
}
```

- `404 NOT_FOUND` on failure on non-existent user

```json
{
    "detail" : "User does not exist.",
}
```

### Get all messages for user

**Definition**

`GET /users/<username>/messages`

Will fetch all received messages.

**Response**

- `200 OK` on success

```json
[
    {
        "sender_username": "alice",
        "recipient_username" : "bob",
        "timestamp": "2024-05-24T15:27:14.459730",
        "content": "hej hej",
        "id" : "some_uuid"
    },
    {
        "sender_username": "alice",
        "recipient_username" : "bob",
        "timestamp": "2024-05-24T15:35:14.459730",
        "content": "vi ses",
        "id" : "another_uuid"
    }
]
```

- `404 NOT_FOUND` on failure on non-existent user

```json
{
    "detail" : "User does not exist.",
}
```

### Get new messages for user

**Definition**

`GET /users/<username>/messages/new`

Will fetch only new messages (since the last time any message was fetched).

**Response**

- `200 OK` on success

```json
[
    {
        "sender_username": "alice",
        "recipient_username" : "bob",
        "timestamp": "2024-05-24T15:27:14.459730",
        "content": "hej hej",
        "id" : "some_uuid"
    },
    {
        "sender_username": "alice",
        "recipient_username" : "bob",
        "timestamp": "2024-05-24T15:35:14.459730",
        "content": "vi ses",
        "id" : "another_uuid"
    }
]
```

- `404 NOT_FOUND` on failure on non-existent user

```json
{
    "detail" : "User does not exist.",
}
```

### Delete a specific message for user.

**Definition**

`DELETE "/users/<username>/messages/<message_id>"`

Deletes a specific message for a specific user.

**Response**

- `200 OK` on success

```json
{
    "Message": "Message deleted."
}
```

- `404 NOT_FOUND` on failure on non-existent user

```json
{
    "detail" : "User does not exist.",
}
```

- `404 NOT_FOUND` on failure on non-existent message with that message_id

```json
{
    "detail" : "No message with this message id exists.",
}
```

### Delete multiple messages for user.

**Definition**

`DELETE /users/<username>/messages/`

If some message_id from the list does not exist, it doesn't throw an error in this case. It deletes the messages that exist.

**Request**

content-type: application/json

Body data should be a list containing the message ids to be deleted.

Ex:
```json
{
    "message_ids" : ["some_id", "another_id"]
}
```

**Response**

```json
{
    "Message": "Message deleted."
}
```

## Using the endpoints with `curl`

### Create an user

```
curl -X POST "http://127.0.0.1:8000/users/" \
-H "Content-Type: application/json" \
-d '{"name": "Alice", "username": "alice"}'
```

### Send a message

```
curl -X POST "http://127.0.0.1:8000/users/bob/messages/" \
-H "Content-Type: application/json" \
-d '{"content": "hej hej", "sender_username": "alice"}'
```

### Get all messages for a user

```
curl "http://127.0.0.1:8000/users/bob/messages/"
```

### Get new messages for a user

```
curl "http://127.0.0.1:8000/users/bob/messages/new"
```

### Delete a specific message for a user

```
curl -X DELETE "http://127.0.0.1:8000/users/bob/messages/message_id"
```

### Delete multiple messages for a user

```
curl -X DELETE "http://127.0.0.1:8000/users/bob/messages/" \
-H "Content-Type: application/json" \
-d '{"message_ids": ["message_id_1", "message_id_2"]}'
```

## Future Work

- Authentication should be done for users, before fetching or sending messages.
- Deleting multiple messages can be improved. We can return a list of messages that were deleted.
- We can add some healthcheck and monitoring.


from fastapi import HTTPException, status, Body, APIRouter
from pydantic import BaseModel
from ..database import UsernameAlreadyExistsError, UserNotFoundError, MessageDoesNotExistError, UsernameCannotBeEmptyError, get_database
from ..models import User, Message
from typing import Annotated


class MessageInfo(BaseModel):
    sender_username: str
    content: str

router = APIRouter()

@router.post("/users/")
def create_user(user: User):
    try:
        get_database().create_user(user)
    except UsernameCannotBeEmptyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UsernameAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"Message" : "User successfully created"}

@router.post("/users/{recipient_username}/messages/", response_model=Message)
def send_message(recipient_username: str, message_info: MessageInfo = Body(...)):
    try:
        message = get_database().create_message(message_info.content, recipient_username, message_info.sender_username)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return message

@router.get("/users/{username}/messages/")
def get_all_messages(username: str):
    try:
        messages = get_database().get_messages_for_user(username)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return messages

@router.get("/users/{username}/messages/new")
def get_new_messages(username: str):
    try:
        messages = get_database().get_new_messages_for_user(username)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    if not messages:
        return {"Message" : "No new messages."}
    return messages

@router.delete("/users/{username}/messages/{message_id}")
def delete_message(username: str, message_id: str):
    try:
        get_database().delete_message(username, message_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except MessageDoesNotExistError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"Message": "Message deleted"}

@router.delete("/users/{username}/messages/")
def delete_messages(username: str, message_ids: Annotated[list[str], Body(embed=True)]):
    try:
        get_database().delete_messages(username, message_ids)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"Message": "Messages deleted"}

# curl commands

# 1. create an user

# curl -X POST "http://127.0.0.1:8000/users/" \
# -H "Content-Type: application/json" \
# -d '{"name": "John Doe", "username": "john123", "email": "john@example.com", "phone_number": "1234567890"}'

# 2. send a message

# curl -X POST "http://127.0.0.1:8000/users/jane123/messages/" \
# -H "Content-Type: application/json" \
# -d '{"content": "Hello Jane, this is John!", "sender_username": "john123"}'

# 3. get all messages for a user

# curl "http://127.0.0.1:8000/users/jane123/messages/"

# 4. get a specific message for a user 

# curl "http://127.0.0.1:8000/users/jane123/messages/message_id"

# 5. delete a specific message for a user

# curl -X DELETE "http://127.0.0.1:8000/users/jane123/messages/message_id"

# 6. delete multiple messages for a user

# This one won't work as there's only one body parameter.
# curl -X DELETE "http://127.0.0.1:8000/users/jane123/messages/" \
# -H "Content-Type: application/json" \
# -d '{"message_ids": ["message_id1", "message_id2"]}'

# It has to be like this
# curl -X DELETE "http://127.0.0.1:8000/users/jane123/messages/" \
# -H "Content-Type: application/json" \
# -d '["message_id1", "message_id2"]'

# For the first one to work, look at FastAPI documentation.

# 7. get new messages for a user

# curl "http://127.0.0.1:8000/users/jane123/messages/new"




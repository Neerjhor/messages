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
    return {"Message" : "User successfully created."}

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
    return {"Message": "Message deleted."}

@router.delete("/users/{username}/messages/")
def delete_messages(username: str, message_ids: Annotated[list[str], Body(embed=True)]):
    try:
        get_database().delete_messages(username, message_ids)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"Message": "Messages deleted."}




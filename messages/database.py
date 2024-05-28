from sqlmodel import SQLModel, create_engine, Session, select, StaticPool
from .models import User, Message
from datetime import datetime
from zoneinfo import ZoneInfo

class UsernameAlreadyExistsError(Exception):
    pass

class UserNotFoundError(Exception):
    pass

class MessageDoesNotExistError(Exception):
    pass

class UsernameCannotBeEmptyError(Exception):
    pass

def get_database():
    return Database()

# This is a singleton.
class Database:
    _instance = None
    
    def __new__(cls, engine_url: str = None):
        if cls._instance is None:
            if not engine_url:
                raise ValueError("An engine URL must be provided to initialize the Database for the first time.")
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.engine = create_engine(engine_url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
        return cls._instance

    def create_db_and_tables(self):
        SQLModel.metadata.create_all(self.engine)
    
    def drop_all_tables(self):
        SQLModel.metadata.drop_all(self.engine)

    def create_user(self, user: User) -> None:
        if not user.username:
            raise UsernameCannotBeEmptyError("Username cannot be an empty string.")
        existing_user = self._get_user_by_username(user.username)
        if existing_user:
            raise UsernameAlreadyExistsError("Username already exists.")
        with Session(self.engine) as session:
            self._update_user_or_message(session, user)

    def _get_user_by_username(self, username: str) -> User:
        with Session(self.engine) as session:
            user = session.exec(select(User).where(User.username == username)).one_or_none()
        return user

    def create_message(self, content: str, recipient_username: str, sender_username: str) -> Message:
        with Session(self.engine) as session:
            recipient = self._get_user_by_username(recipient_username)
            sender = self._get_user_by_username(sender_username)
            if not recipient:
                raise UserNotFoundError("Recipient does not exist.")
            if not sender:
                raise UserNotFoundError("Sender does not exist.")
            new_message = Message(content=content, recipient_username=recipient.username, sender_username=sender.username)
            self._update_user_or_message(session, new_message)
        return new_message

    def get_messages_for_user(self, username: str) -> list:
        with Session(self.engine) as session:
            user = self._get_user_by_username(username)
            if not user:
                raise UserNotFoundError("User does not exist.")
            current_time = datetime.now(ZoneInfo("UTC"))
            messages = session.exec(select(Message)
                                    .where(Message.recipient_username == user.username)
                                    .order_by(Message.timestamp)).all()
            user.last_seen = current_time
            self._update_user_or_message(session, user)
            for message in messages:
                session.refresh(message)
        return messages
    
    def get_new_messages_for_user(self, username: str) -> list:
        with Session(self.engine) as session:
            user = self._get_user_by_username(username)
            if not user:
                raise UserNotFoundError("User does not exist.")
            current_time = datetime.now(ZoneInfo("UTC"))
            messages = session.exec(select(Message)
                                    .where(Message.recipient_username == user.username,
                                           Message.timestamp > user.last_seen)
                                    .order_by(Message.timestamp)).all()
            user.last_seen = current_time
            self._update_user_or_message(session, user)
            for message in messages:
                session.refresh(message)
        return messages

    def delete_message(self, username: str, message_id: str) -> None:
        with Session(self.engine) as session:
            user = self._get_user_by_username(username)
            if not user:
                raise UserNotFoundError("User does not exist.")
            message = session.exec(select(Message).where(Message.recipient_username == user.username, Message.id == message_id)).one_or_none()
            if not message:
                raise MessageDoesNotExistError("No message with this message id exists.")
            session.delete(message)
            session.commit()

    def delete_messages(self, username: str, message_ids: list[str]) -> None:
        with Session(self.engine) as session:
            user = self._get_user_by_username(username)
            if not user:
                raise UserNotFoundError("User does not exist.")
            messages = session.exec(select(Message).where(Message.recipient_username == user.username, Message.id.in_(message_ids))).all()
            for message in messages:
                session.delete(message)
            session.commit()

    def _update_user_or_message(self, session, user_or_message: User | Message) -> None:
        session.add(user_or_message)
        session.commit()
        session.refresh(user_or_message)

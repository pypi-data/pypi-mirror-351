from clicker_bot.onebot import MessagePost
from clicker_bot.storage import db, Account


def login_required(message: MessagePost) -> bool:
    return db.session.get(Account, message.user_id) is not None

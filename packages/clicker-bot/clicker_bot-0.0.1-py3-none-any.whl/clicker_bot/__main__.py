import datetime
import json
import random
import time
from pprint import pprint
from zlib import adler32

from flask import Flask, request

from clicker_bot.command import Command, respond
from clicker_bot.onebot import validate_post, MessagePost
from clicker_bot.storage import db, Account, Practice, SignIn
from clicker_bot.util import login_required

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///storage.db"

db.init_app(app)

command = Command()


@command.register_command("用户 注册")
@command.add_criterion(lambda e: not login_required(e))
def account_register(event: MessagePost):
    account = Account(
        user_id=event.user_id,
        ident=hex(adler32(bin(event.user_id).encode()))[2:].ljust(8, "0").upper(),
        created_at=time.time(),
    )
    db.session.add(account)
    db.session.commit()
    return ""


@command.register_command("用户 信息")
@command.add_criterion(login_required)
def account_info(event: MessagePost):
    account = db.session.get(Account, event.user_id)
    return respond.reply(
        "用户信息:\n"
        f"标识符: {account.ident}\n"
        f"修为: {account.cultivation}\n"
        f"灵石: {account.spirit_stone}"
    )


@command.register_command("签到")
@command.register_command("今日人品")
@command.register_command("jrrp")
@command.add_criterion(login_required)
def sign_in(event: MessagePost):
    account = db.session.get(Account, event.user_id)
    if sign_in_record := db.session.query(SignIn).filter_by(user_id=account.user_id, day=datetime.date.today().toordinal()).first():
        return respond.reply(
            "今日已签到\n"
            f"今日人品: {sign_in_record.luck}"
        )
    sign_in_record = SignIn(
        user_id=account.user_id,
        day=datetime.date.today().toordinal(),
        luck=int(random.random() * 100)
    )
    account.spirit_stone += sign_in_record.luck
    db.session.add(sign_in_record)
    db.session.commit()
    return respond.reply(
        "签到成功\n"
        f"今日人品: {sign_in_record.luck}\n"
        "已记入灵石"
    )


@command.register_command("闭关")
@command.add_criterion(login_required)
def start_practice(event: MessagePost):
    if db.session.query(Practice).filter_by(user_id=event.user_id, end_at=None).first():
        return respond.reply("正在修炼")
    else:
        practice = Practice(user_id=event.user_id, start_at=time.time())
        db.session.add(practice)
        db.session.commit()
        return respond.reply("开始修炼")


@command.register_command("出关")
@command.add_criterion(login_required)
def end_practice(event: MessagePost):
    account = db.session.get(Account, event.user_id)
    if practice := db.session.query(Practice).filter_by(user_id=event.user_id, end_at=None).first():
        practice.end_at = time.time()
        dt = practice.end_at - practice.start_at
        fdt = account.cultivation
        cdt = (0.5 + random.random()) * dt * 0.1
        account.cultivation += cdt
        db.session.commit()
        return respond.reply(
            "修炼完成\n"
            f"时长: {dt:.1f}秒\n"
            f"修为: {fdt:.1f} -> {cdt:.1f}"
        )
    else:
        return respond.reply("未在修炼")


@app.route("/")
def index():
    return "Hello, world"


@app.post("/onebot/v11/")
def onebot_handler():
    try:
        post = validate_post(request.data)
        if isinstance(post, MessagePost):
            return command.execute_command(post)
    except ValueError as e:
        if app.debug:
            pprint(json.loads(request.data))
            raise e
    return ""


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=8080)


from pprint import pprint
from typing import Callable

import clicker_bot.command.respond
from clicker_bot.onebot import MessagePost, Sender

_arg_type_mapping = {
    "str": str,
    "int": int,
}


T_criterion = Callable[[MessagePost], bool]
T_handler = Callable[[MessagePost, ...], str]


class Command:
    def __init__(self, prefix="/"):
        self.prefix = prefix
        self._commands: dict[str, tuple[T_handler, list[T_criterion]]] = {}

    def register_command(self, command: str):
        def wrapper(f: tuple[T_handler, list[T_criterion]] | T_handler):
            if isinstance(f, tuple):
                self._commands[command] = f
                return f[0]
            else:
                self._commands[command] = (f, [])
                return f
        return wrapper

    @staticmethod
    def add_criterion(criterion: T_criterion):
        def wrapper(f: T_handler | tuple[T_handler, list[T_criterion]]):
            if isinstance(f, tuple):
                return f[0], f[1] + [criterion]
            return f, [criterion]
        return wrapper

    def parse_command(self, command: str) -> (dict[str, str | int], tuple[T_handler, list[T_criterion]]):
        tokens = command.split(" ")
        for pattern, handler in self._commands.items():
            result = {}
            for template, token in zip(pattern.split(" "), tokens):
                if template.startswith("<") and template.endswith(">"):
                    arg_type, arg_name = template[1:-1].split(":")
                    try:
                        result[arg_name] = _arg_type_mapping[arg_type](token)
                    except ValueError:
                        break
                elif template == token:
                    continue
                else:
                    break
            else:
                return result, handler
        raise ValueError

    def execute_command(self, event: MessagePost) -> str:
        if event.raw_message.startswith(self.prefix):
            kwargs, (handler, criteria) = self.parse_command(event.raw_message[1:])
            for criterion in criteria:
                if not criterion(event):
                    return respond.reply("不满足条件")
            else:
                return handler(event, **kwargs)
        return ""


if __name__ == "__main__":
    command = Command()

    @command.register_command("aaa")
    def b():
        print("b called")

    def criterion_a(event: MessagePost):
        return event.user_id == 3488229708

    def criterion_b(event: MessagePost):
        return event.raw_message == "/test 123"

    @command.register_command("test <int:sth>")
    @command.add_criterion(criterion_a)
    @command.add_criterion(criterion_b)
    def a(event: MessagePost, sth: int):
        print(f"a is called, sth={sth}")
        return "a is called"

    message = MessagePost(time=0, self_id=0, post_type="message", message_type="group", sub_type="normal", message_id=0, user_id=3488229708, message=[], raw_message="/test 123", font=0, sender=Sender(user_id=3488229708, nickname="笨蛋猫猫"))

    pprint(command.execute_command(message))

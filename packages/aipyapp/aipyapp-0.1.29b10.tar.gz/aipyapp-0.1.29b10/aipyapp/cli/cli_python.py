#!/usr/bin/env python
# -*- coding: utf-8 -*-
import code
import builtins
from pathlib import Path

from rich.console import Console
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.history import FileHistory
from pygments.lexers.python import PythonLexer

from .. import __version__
from ..aipy import TaskManager
from ..aipy.i18n import T, set_lang
from ..aipy.config import ConfigManager

class PythonCompleter(WordCompleter):
    def __init__(self, ai):
        names = ['exit()']
        names += [name for name in dir(builtins)]
        names += [f"ai.{attr}" for attr in dir(ai) if not attr.startswith('_')]
        super().__init__(names, ignore_case=True)
    
def main(args):
    console = Console(record=True)
    console.print(f"[bold cyan]🚀 Python use - AIPython ({__version__}) [[green]https://aipy.app[/green]]")

    conf = ConfigManager(args.config_dir)
    conf.check_config()
    settings = conf.get_config()

    lang = settings.get('lang')
    if lang: set_lang(lang)
    
    try:
        ai = TaskManager(settings, console=console)
    except Exception as e:
        console.print_exception(e)
        return

    update = ai.get_update(True)
    if update and update.get('has_update'):
        console.print(f"[bold red]🔔 号外❗ {T('Update available')}: {update.get('latest_version')}")

    if not ai.llm:
        console.print(f"[bold red]{T('no_available_llm')}")
        return
    
    names = ai.llm.names
    console.print(f"{T('banner1_python')}", style="green")
    console.print(f"[cyan]{T('default')}: [green]{names['default']}，[cyan]{T('enabled')}: [yellow]{' '.join(names['enabled'])}")

    interp = code.InteractiveConsole({'ai': ai})

    completer = PythonCompleter(ai)
    lexer = PygmentsLexer(PythonLexer)
    auto_suggest = AutoSuggestFromHistory()
    history = FileHistory(str(Path.cwd() / settings.history))
    session = PromptSession(history=history, completer=completer, lexer=lexer, auto_suggest=auto_suggest)
    while True:
        try:
            user_input = session.prompt(HTML('<ansiblue>>> </ansiblue>'))
            if user_input.strip() in {"exit()", "quit()"}:
                break
            interp.push(user_input)
        except EOFError:
            console.print("[bold yellow]Exiting...")
            break
        except Exception as e:
            console.print(f"[bold red]Error: {e}")

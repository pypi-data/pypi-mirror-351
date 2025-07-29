#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from functools import wraps

from term_image.image import from_file, from_url

from . import utils
from .plugin import event_bus
from .i18n import T
from ..exec import BaseRuntime

def restore_output(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__

        try:
            return func(self, *args, **kwargs)
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr
    return wrapper

class Runtime(BaseRuntime):
    def __init__(self, task):
        super().__init__(task.envs)
        self.gui = task.gui
        self.task = task
        self.console = task.console
        self._auto_install = task.settings.get('auto_install')
        self._auto_getenv = task.settings.get('auto_getenv')

    @restore_output
    def install_packages(self, *packages):
        self.console.print(f"\n⚠️ LLM {T('ask_for_packages')}: {packages}")
        ok = utils.confirm(self.console, f"💬 {T('agree_packages')} 'y'> ", auto=self._auto_install)
        if ok:
            ret = self.ensure_packages(*packages)
            self.console.print("\n✅" if ret else "\n❌")
            return ret
        return False
    
    @restore_output
    def get_env(self, name, default=None, *, desc=None):
        self.console.print(f"\n⚠️ LLM {T('ask_for_env', name)}: {desc}")
        try:
            value = self.envs[name][0]
            self.console.print(f"✅ {T('env_exist', name)}")
        except KeyError:
            if self._auto_getenv:
                self.console.print(f"✅ {T('auto_confirm')}")
                value = None
            else:
                value = self.console.input(f"💬 {T('input_env', name)}: ")
                value = value.strip()
            if value:
                self.set_env(name, value, desc)
        return value or default
    
    @restore_output
    def display(self, path=None, url=None):
        image = {'path': path, 'url': url}
        event_bus.broadcast('display', image)
        if not self.gui:
            image = from_file(path) if path else from_url(url)
            image.draw()

    @restore_output
    def input(self, prompt=''):
        return self.console.input(prompt)    
    
    def get_code_by_id(self, code_id):
        return self.task.code_blocks.get_code_by_id(code_id)
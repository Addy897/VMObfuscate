import random
from typing import Any
class InstructionToken:
    _instruction_tokens = {
        "push": None, "pop": None, "mov": None, "lea": None, "ret": None,
        "call": None, "cmp": None, "test": None, "jmp": None, "jg": None,
        "je": None, "jne": None, "jb": None, "add": None, "sub": None,
        "mul": None, "div": None, "rax": None, "rbx": None, "rcx": None,
        "rdx": None, "rsi": None, "rdi": None, "rsp": None, "rbp": None,
        "r8": None, "r9": None
    }
    _available_opcodes = list(range(1, 128))

    _aliases = {
        'ah': 'rax','al': 'rax','ax': 'rax', 'eax': 'rax',
        'bh': 'rbx','bl': 'rbx','bx': 'rbx','ebx': 'rbx',
        'ch': 'rcx','cl': 'rcx','cx': 'rcx','ecx': 'rcx',
        'dh': 'rdx','dl': 'rdx','dx': 'rdx','edx': 'rdx',
        'si': 'rsi','esi': 'rsi',
        'di': 'rdi','edi': 'rdi',
        'sp': 'rsp','esp': 'rsp',
        'bp': 'rbp','ebp': 'rbp',
        'r8b': 'r8','r8w': 'r8','r8d': 'r8',
        'r9b': 'r9','r9w': 'r9','r9d': 'r9'
    }
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> int | Any:
        resolved = cls._aliases.get(key, key)
        return cls._instruction_tokens.get(resolved, default)

    @classmethod
    def set(cls, key: str, value: int) -> None:
        resolved = cls._aliases.get(key, key)
        cls._instruction_tokens[resolved] = value

    @classmethod
    def keys(cls):
        return cls._instruction_tokens.keys()

    @classmethod
    def items(cls):
        return cls._instruction_tokens.items()

    @classmethod
    def __str__(cls):
        return str(cls._instruction_tokens)
    @classmethod
    def __repr__(cls):
        return str(cls._instruction_tokens)
    
    @classmethod
    def randomize(cls):
        random.shuffle(cls._available_opcodes)

        for i,key in enumerate(cls._instruction_tokens.keys()):
            cls._instruction_tokens[key]=cls._available_opcodes[i]
    @classmethod
    def sorted_values(cls) -> []:
        return  [cls._instruction_tokens[i] for i in sorted(cls._instruction_tokens)]

INTERNAL_FUNCTON={
 "__main":1
}

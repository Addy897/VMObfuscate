import subprocess
import re
from .rdata import RDATA
from .constants import INTERNAL_FUNCTON, OPCODES, REGISTERS
class Translator:
    def __init__(self) -> None:
        self.asm_dump=None
        self.binary_file:str|None=None
        self.funcs={}
        self.call_graph={}
        self.rdata=None
        self.translated_funcs={}
        self.opcodes_pattern=re.compile(r"^\s*(?P<addr>[0-9A-Fa-f]+):\s+(?P<bytes>(?:[0-9A-Fa-f]{2}\s+)+)(?P<mnemonic>\w+)\s*(?P<operands>.*)$")
    def _disassemble(self) -> None:
        if(self.binary_file is not None):
            try:
                self.asm_dump=subprocess.check_output(["objdump","-d","-Mintel",self.binary_file]).decode()
            except subprocess.CalledProcessError:
                raise Exception(f"No file {self.binary_file} found.")
        else:
            raise ValueError("Empty binary file.")
    def transalte(self,file) -> None:
        self.binary_file=file
        self.rdata=RDATA(file)
        self._disassemble()
        self._extract_funcs()
        self.translate_func("main")
        self.write_to_file()
    def _is_user_func_name(self, name: str) -> bool:
        return bool(re.match(r"^(?:[A-Za-z]\w*|_Z\w+)$", name))

    def _extract_funcs(self) -> None:
            header_re = re.compile(r'^\s*([0-9A-Fa-f]+)\s+<([A-Za-z0-9_@]+)>:')
            current = None
            lines = []
            if( self.asm_dump is None):
                raise Exception("No Diassembly found")
            for text in self.asm_dump.splitlines():
                m = header_re.match(text)
                if m:
                    addr, name = m.groups()
                    if current:
                        self.funcs[current] = lines
                    if self._is_user_func_name(name):
                        current = name
                        lines = []
                    else:
                        current = None
                        lines = []
                elif current:
                    if text.strip().endswith("nop") or text=='':
                        continue
                    lines.append(text)

            if current:
                self.funcs[current] = lines
    def _strip_prologue(self,asm_lines):
        prologue=[("sub","rsp,")]
        found_prologue=True

        for i,asm_line in enumerate(asm_lines[:1]):
            match=self.opcodes_pattern.match(asm_line)
            if(match):
                current_opcode=match.group('mnemonic')
                operands=match.group('operands').replace(" ","")
                if(current_opcode!=prologue[i][0] or not operands.startswith(prologue[i][1])):
                    found_prologue=False
            else:
                break
        if(found_prologue):
            asm_lines=asm_lines[1:]
        return asm_lines
    def _strip_epilogue(self,asm_lines):
        epilogue=[("add","rsp,")]
        found_epilogue=False
        k=0
        for i in range(len(asm_lines)-1,-1,-1):
            asm_line=asm_lines[i]
            match=self.opcodes_pattern.match(asm_line)
            if(match):
                current_opcode=match.group('mnemonic')
                operands=match.group('operands').replace(" ","")
                if(current_opcode==epilogue[0][0] or operands.startswith(epilogue[0][1])):
                    found_epilogue=True
                    k=i
                    break
            else:
                break
        if(found_epilogue):
            asm_lines=asm_lines[:k]+asm_lines[k+1:]
        return asm_lines

    def write_to_file(self):
        if(self.binary_file):
            base_file=self.binary_file.removesuffix(".exe")
            with open(f"{base_file}.vmo","w") as f:
                for key,value in self.translated_funcs.items():
                    f.write(f"{key}:\n")
                    for line in value.splitlines():
                        f.write(f"{line}\n")
    def translate_func(self,func_name) -> None:
        if(self.rdata is None):
            raise Exception("No .rdata section found")
        asm_lines=self.funcs[func_name]
        asm_lines=self._strip_prologue(asm_lines)
        asm_lines=self._strip_epilogue(asm_lines)
        addr_func_pat=re.compile(r"(?P<addr>[0-9A-Fa-f]+)\s<(?P<name>[0-9a-zA-Z_]+)>")
        parsed_code=""
        for asm_line in asm_lines:
            match=self.opcodes_pattern.match(asm_line)
            if(match):
                current_opcode=match.group('mnemonic')

                operands=match.group('operands')
                operands=operands.split(",")
                if(current_opcode=="call"):
                    qword_ptr_pat=re.compile(r"QWORD PTR \[rip.*\]\s*#\s*[0-9A-Fa-fx]+\s+<([A-Za-z0-9_@]+)>")
                    qword_ptr_match=qword_ptr_pat.match(operands[0])
                    call_func=addr_func_pat.match(operands[0])
                    if(call_func):
                        call_func_name=call_func.group("name")
                        if(INTERNAL_FUNCTON.get(call_func_name)):
                            continue
                        if(not call_func_name.startswith("__")):
                            self.translate_func(call_func_name)
                        operands[0]=call_func_name
                    elif(qword_ptr_match):
                        operands[0]=qword_ptr_match.group(1)

                elif(current_opcode=='lea'):
                    first,second=operands
                    rdata_addr_pat=re.compile(r"\[rip\+.+\]\s*#\s([0-9A-Fa-f]+)\s<.rdata.*\>$")
                    rdata_addr_match=rdata_addr_pat.match(second)
                    if(rdata_addr_match):
                        addr=hex(int(rdata_addr_match.group(1),16))
                        operands[1]=hex(int(self.rdata.get(addr,"0"),16))
                elif(current_opcode=="mov"):
                    qword_ptr_pat=re.compile(r"QWORD PTR \[rip\+[0-9a-fA-F]+\]\s*#\s[0-9A-Fa-f]+\s<__imp_([A-Za-z]+)>")
                    qword_ptr_match=qword_ptr_pat.match(operands[1])
                    if(qword_ptr_match):
                        operands[1]=qword_ptr_match.group(1)
                parsed_code+=str(OPCODES.get(current_opcode,current_opcode))
                for operand in operands:
                    parsed_code+=" "+str(REGISTERS.get(operand,operand))
                parsed_code+="\n"

        self.translated_funcs[func_name]=parsed_code

import subprocess
import re
from .rdata import RDATA
from .constants import INTERNAL_FUNCTON,InstructionToken
import random,bisect
from pprint import pprint
class Translator:
    def __init__(self) -> None:
        self.asm_dump=None
        self.binary_file:str|None=None
        self.funcs={}
        self.call_stack=[]
        self.rdata=None
        self.translated_funcs={}
        InstructionToken.randomize()
        self.distance={}
        self.already_parsed = {}
        self.opcodes_pattern = re.compile(r'^\s*(?P<addr>[0-9A-Fa-f]+):\s+(?P<bytes>(?:[0-9A-Fa-f]{2}\s+)+)\t(?P<mnemonic>\w+)\s*(?P<operands>.*)$')
    def _disassemble(self) -> None:
        if(self.binary_file is not None):
            try:
                self.asm_dump=subprocess.check_output(["objdump","-d","-Mintel",self.binary_file]).decode()
            except subprocess.CalledProcessError:
                raise Exception(f"No file {self.binary_file} found.")
        else:
            raise ValueError("Empty binary file.")
    def translate(self,file,write=True) -> None:
        
        self.binary_file=file
        self.rodata=RDATA(file)
        self._disassemble()
        self._extract_funcs()
        self.translate_func()
        if(write):
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
                    if(self.opcodes_pattern.match(text)):
                        lines.append(text)

            if current:
                self.funcs[current] = lines
    def _strip_prologue(self,asm_lines):
        prologue=[("sub","rsp,")]
        found_prologue=False
        k =0
        for i,asm_line in enumerate(asm_lines):
            match=self.opcodes_pattern.match(asm_line)
            if(match):
                current_opcode=match.group('mnemonic')
                operands=match.group('operands').replace(" ","")
                if(current_opcode==prologue[0][0] and operands.startswith(prologue[0][1])):
                    found_prologue=True
                    k=i
                    break
            else:
                break
        if(found_prologue):
            asm_lines=asm_lines[:k]+asm_lines[k+1:]
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
                if(current_opcode==epilogue[0][0] and operands.startswith(epilogue[0][1])):
                    found_epilogue=True
                    k=i
                    break
            else:
                break
        if(found_epilogue):
            asm_lines=asm_lines[:k]+asm_lines[k+1:]
        return asm_lines

    def write_to_file(self):
        enc_key = random.randint(1, 255)
        if(self.binary_file):
            base_file=self.binary_file.removesuffix(".exe")
            with open(f"{base_file}.vmo","wb") as f:
                f.write(bytes([enc_key]))
                for tok in InstructionToken.sorted_values():
                    f.write(bytes([enc_key^tok]))
                for key,value in self.translated_funcs.items():
                    data=bytearray((f"{key}:\n{value}").encode('utf-8'))
                    for i in range(len(data)):
                        data[i] ^= enc_key
                    f.write(data)


    def parse_asm_lines(self,func_name:str,asm_lines:list[str]) -> list[str]:
        current_line = 0
        parsed_lines = []
        self.already_parsed[func_name] = 1    
        addr_func_pat=re.compile(r"(?P<addr>[0-9A-Fa-f]+)\s<(?:__mingw_)?(?P<name>[A-Za-z0-9]+)")
        for asm_line in asm_lines:
            match=self.opcodes_pattern.match(asm_line)
            if(match):
                current_opcode=match.group('mnemonic')
                operands=match.group('operands')
                inst_addr = match.group("addr")
                self.distance[inst_addr] = current_line
                operands=operands.split(",")
                if(current_opcode=="call"):
                    qword_ptr_pat=re.compile(r"QWORD PTR \[rip.*\]\s*#\s*[0-9A-Fa-fx]+\s+<([A-Za-z0-9_@]+)>")
                    qword_ptr_match=qword_ptr_pat.match(operands[0])
                    call_func=addr_func_pat.match(operands[0])
                    if(call_func):
                        call_func_name=call_func.group("name")
                        if(not INTERNAL_FUNCTON.get(call_func_name) and call_func_name != func_name and not self.already_parsed.get(call_func_name,0)):
                            self.call_stack.append(call_func_name)
                        operands[0]=call_func_name
                    elif(qword_ptr_match):
                        operands[0]=qword_ptr_match.group(1)
                    else:
                        continue
                elif(current_opcode=='lea'):
                    first,second=operands
                    rdata_addr_pat=re.compile(r"\[rip\+.+\]\s*#\s([0-9A-Fa-f]+)\s<.*\>$")
                    rdata_addr_match=rdata_addr_pat.match(second)
                    lea_pat2= re.compile(r"\[(?P<register>[a-z]{3,4})(?P<num>[\+\-]0x[a-fA-F0-9]+)\]")
                    lea_match2 = lea_pat2.match(second)
                    if(rdata_addr_match):
                        addr=hex(int(rdata_addr_match.group(1),16))
                        operands[1]="0x"+self.rodata.get(addr,"0")
                    elif(lea_match2 and lea_match2.group('register') !='rip'):
                        reg = lea_match2.group('register')
                        parsed_lines.append(f"mov {first} {reg}")
                        num = lea_match2.group('num')
                        func = 'add' if num[0] == '+' else 'sub'
                        parsed_lines.append(f"{func} {first} {num[1:]}")
                        current_line+=1
                        continue    
                        
                    else:
                        print(f"rodata did not matched for {operands}")    
                        
                elif(current_opcode=="mov"):
                    word_ptr_pat=re.compile(r".WORD PTR \[rsp\+0x[0-9a-fA-F]+\]")
                    word_ptr_push_match=word_ptr_pat.match(operands[0])
                    word_ptr_pop_match=word_ptr_pat.match(operands[1])
                    if(word_ptr_push_match):
                        operands[0]=operands[1]
                        operands.pop(1)
                        current_opcode = "push"
                    elif(word_ptr_pop_match):
                        current_opcode = "pop"
                        operands.pop(1)
                elif(current_opcode[0] == "j"):
                    loc_pat = re.compile(r"(?P<addr>[0-9A-Fa-f]+)\s<(?P<name>[A-Za-z0-9]+)(?P<loc>[\+\-0x]+[a-fA-F0-9]+)>")
                    loc=loc_pat.match(operands[0])
                    if(loc):
                        operands[0] = loc.group("addr")

                parsed_code=f"{current_opcode}"    
                for operand in operands:
                    parsed_code+=" "+operand
                parsed_lines.append(parsed_code)
                current_line+=1

        return parsed_lines
    def bs(self,arr, x):
        i = bisect.bisect_right(arr, x)
        if i != len(arr):
            return i 
        else:
            return -1
    def translate_func(self) -> None:
        if(self.rodata is None):
            raise Exception("No .rodata section found")
        self.call_stack.append("main")
        while(len(self.call_stack)>0):
            func_name = self.call_stack.pop(-1)
            asm_lines=self.funcs[func_name]
            asm_lines=self._strip_prologue(asm_lines)
            asm_lines=self._strip_epilogue(asm_lines)
            parsed_lines = self.parse_asm_lines(func_name,asm_lines)
            parsed_code = ""
            for i in range(len(parsed_lines)):
                line = parsed_lines[i]
                ops = line.split(" ")
                if(line[0] == 'j'):
                    jmp_loc = self.distance.get(ops[1],-1)
                    if(jmp_loc == -1):
                        arr = sorted([int(x,16) for x in self.distance.keys()])
                        index = bisect.bisect_right(arr, int(ops[1],16))
                        if index < len(arr):
                            k = hex(arr[index]).replace("0x","")
                            jmp_loc = self.distance.get(k,-1)
                    ops[1] = hex(jmp_loc)
                    parsed_lines[i] = f"{ops[0]} {ops[1]}" 
                parsed_code +=f"{InstructionToken.get(ops[0],ops[0])}"
                if(ops[0] == "call"):
                    parsed_code +=f" {ops[1]}"
                else:
                    for op in ops[1:]:    
                        parsed_code +=f" {InstructionToken.get(op,op)}"
                parsed_code+="\n"
            self.translated_funcs[func_name]=parsed_code
            self.funcs[func_name]=parsed_lines
        keys = list(self.funcs.keys())
        for k in keys:
            if(k not in self.translated_funcs):
                self.funcs.pop(k)

if __name__ == '__main__':
    translator = Translator();
    translator.translate("../payloads/payload",False)

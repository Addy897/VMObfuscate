import subprocess
import re
from .rodata import RODATA
from .constants import INTERNAL_FUNCTON,InstructionToken
import random
from pprint import pprint
class Translator:
	def __init__(self) -> None:
		self.asm_dump=None
		self.binary_file:str|None=None
		self.funcs={}
		self.call_graph={}
		self.rodata=None
		self.translated_funcs={}
		InstructionToken.randomize()
		self.opcodes_pattern = re.compile(r'^\s*(?P<addr>[0-9A-Fa-f]+):\s+(?P<bytes>(?:[0-9A-Fa-f]{2}\s+)+)\t(?P<mnemonic>\w+)\s*(?P<operands>.*)$')
	def _disassemble(self) -> None:
		if(self.binary_file is not None):
			try:
				self.asm_dump=subprocess.check_output(["objdump","-d","-Mintel",self.binary_file]).decode()
			except subprocess.CalledProcessError:
				raise Exception(f"No file {self.binary_file} found.")
		else:
			raise ValueError("Empty binary file.")
	def translate(self,file,write_to_file=True) -> None:
		
		self.binary_file=file
		self.rodata=RODATA(file)
		self._disassemble()
		self._extract_funcs()
		self.translate_func("main")
		if(write_to_file):
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
			 
	def translate_func(self,func_name) -> None:
		if(self.rodata is None):
			raise Exception("No .rodata section found")
		asm_lines=self.funcs[func_name]
		asm_lines=self._strip_prologue(asm_lines)
		asm_lines=self._strip_epilogue(asm_lines)
		addr_func_pat=re.compile(r"(?P<addr>[0-9A-Fa-f]+)\s<(?P<name>[A-Za-z0-9]+)")
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
						if(not INTERNAL_FUNCTON.get(call_func_name) and call_func_name != func_name):
							self.translate_func(call_func_name)
						operands[0]=call_func_name
					elif(qword_ptr_match):
						operands[0]=qword_ptr_match.group(1)

				elif(current_opcode=='lea'):
					first,second=operands
					rodata_addr_pat=re.compile(r"\[rip\+.+\]\s*#\s([0-9A-Fa-f]+)\s<.*\>$")
					rodata_addr_match=rodata_addr_pat.match(second)
					lea_pat2= re.compile(r"\[(?P<register>[a-z]{3,4})(?P<num>[\+\-]0x[a-fA-F0-9]+)\]")
					lea_match2 = lea_pat2.match(second)
					if(rodata_addr_match):
						addr=hex(int(rodata_addr_match.group(1),16))
						operands[1]="0x"+self.rodata.get(addr,"0")
					elif(lea_match2 and lea_match2.group('register') !='rip'):
						reg = lea_match2.group('register')
						parsed_code += f"{InstructionToken.get('mov','mov')} {InstructionToken.get(first,first)} {InstructionToken.get(reg,reg)}\n" 
						num = lea_match2.group('num')
						func = 'add' if num[0] == '+' else 'sub'
						parsed_code+= f"{InstructionToken.get(func,func)} {InstructionToken.get(first,first)} {num[1:]}\n"

						continue	
						
					else:
						print(f"rodata did not matched for {operands}")	
						
				elif(current_opcode=="mov"):
					qword_ptr_pat=re.compile(r"QWORD PTR \[rip\+[0-9a-fA-F]+\]\s*#\s[0-9A-Fa-f]+\s<__imp_([A-Za-z]+)>")
					qword_ptr_match=qword_ptr_pat.match(operands[1])
					if(qword_ptr_match):
						operands[1]=qword_ptr_match.group(1)
				elif(current_opcode[0] == "j"):
					loc_pat = re.compile(r"(?P<addr>[0-9A-Fa-f]+)\s<(?P<name>[A-Za-z0-9]+)(?P<loc>[\+\-0x]+[a-fA-F0-9]+)>")
					loc=loc_pat.match(operands[0])
					if(loc):
						operands[0]=loc.group("loc")
	
							
				parsed_code+=str(InstructionToken.get(current_opcode,current_opcode))
				if(current_opcode == "call"):
					parsed_code += " " + operands[0]
				else:
					for operand in operands:
						parsed_code+=" "+str(InstructionToken.get(operand,operand))
				parsed_code+="\n"

		self.translated_funcs[func_name]=parsed_code

if __name__ == '__main__':
	translator = Translator();
	translator.translate("../payloads/payload")

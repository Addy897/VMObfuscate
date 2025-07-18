#include"main.h"
   
VM::VM(string filename){
	
	ifstream f(filename,ios::binary);
	if (!f.is_open()) {
			cerr << "Error opening the file!";
			return;
	}

	char key;
	f.read(&key, 1);
	for(int i=0;i<TOKENS_LEN;i++){
		int c = f.get();
		if (c != EOF) {
			tokens[i] = static_cast<unsigned char>(c ^ key);
		} else {
			break;
		}
	}
	while (!f.eof()) {
		char c;
		f.get(c);
		if (!f.eof()) {
			c ^= key;
			buffer.put(c);
		}
	}
	f.close();
	load_vmo();
}
void VM::load_vmo(){
	regex rgx("(\\w+):");
	string line;
	char del=' ';
	int start=0,end=-1;
	string current;
	while(getline(buffer,line)){
			
			smatch m;
			if(regex_search(line, m, rgx)){
				if(current.length()!=0){
					function_addr[current]=vector<int>{start,end};
				}
				current=m.str(1);
				start=end+1;
			}
			else{
				stringstream l(line);
				string t;
				Instruction inst;
				getline(l, t, del);
				int opcode_int=stoi(t);
				inst.opcode=stoi(t);
				getline(l,inst.operand1 , del);
				getline(l,inst.operand2,del);
				code.push_back(inst);
				end++;

			}
	}
	if(current.length()!=0){
		function_addr[current]={start,end};
	}
}
void VM::handle_internal_function(INTERNAL_FUNCTION func) {
	switch (func) {
		case INTERNAL_FUNCTION::CALL_MessageBoxA:{
			int arg1,arg4;
			string arg2,arg3;
			int rcx=tokens[TOKENS_TYPE::RCX];
			int rdx =tokens[TOKENS_TYPE::RDX];
			int r8=tokens[TOKENS_TYPE::R8];
			int r9 =tokens[TOKENS_TYPE::R9];
			arg1 = vars[rcx].get_int();
			arg2 = vars[rdx].get_str();
			arg3 = vars[r8].get_str();
			arg4 = vars[r9].get_int();
			 MessageBoxA(
				(HWND)(uintptr_t)arg1,      
				arg2.c_str(),                
				arg3.c_str(),              
				arg4                  
			);
			vars.erase(rcx);
			vars.erase(rdx);
			vars.erase(r8);
			vars.erase(r9);

			break;
		}

		case INTERNAL_FUNCTION::CALL_printf:{
			string arg1;		
			int rcx=tokens[TOKENS_TYPE::RCX];
			arg1 = vars[rcx].get_str();
			printf(arg1.c_str());
			vars.erase(rcx);
			break;
			
		}

		default:
			cerr << "[internal] Unknown internal function\n";
			break;
	}
}
void VM::fromhex(string& hexstr,string& result){
		if (hexstr.rfind("0x", 0) != string::npos) hexstr = hexstr.substr(2);
		for (size_t i = 0; i < hexstr.length(); i += 2) {
			string byteStr = hexstr.substr(i, 2);
			char c = static_cast<char>(stoi(byteStr, nullptr, 16));
			result.push_back(c);
		}
}
void VM::run_function(const string& func_name) {
	if (function_addr.find(func_name) == function_addr.end()) {
		cerr << "Function not found: " << func_name << "\n";
		return;
	}
	
	auto range = function_addr[func_name];
	for (int i = range[0]; i <= range[1]; ++i) {
		auto& inst = code[i];
		int var_id;
		if(inst.opcode==tokens[TOKENS_TYPE::CALL]){
				if (internal_function_map.count(inst.operand1)) {
					handle_internal_function(internal_function_map[inst.operand1]);
				} else if (function_addr.count(inst.operand1)) {
					run_function(inst.operand1);
				} else {
					cerr << "[error] Unknown function: " << inst.operand1 << "\n";
				}
		}else if(inst.opcode==tokens[TOKENS_TYPE::MOV]){
				var_id = stoi(inst.operand1);
				Value val = stoi(inst.operand2, nullptr, 0);
				vars[var_id] = val;
		}else if(inst.opcode==tokens[TOKENS_TYPE::LEA]){
				var_id = stoi(inst.operand1);
				string hexstr = inst.operand2;
				string result;
				fromhex(hexstr,result);
				vars[var_id] = result;
		}else if(inst.opcode==tokens[TOKENS_TYPE::RET]){
				return;
		}else{
			cout << "[unhandled opcode] " << static_cast<int>(inst.opcode)<< "\n";
				
		}
	}
}
void VM::start_runtime(){
	run_function("main");
	
}
	

int main(){
    VM vm =VM("payload.vmo");
    vm.start_runtime();
    return 0;
}

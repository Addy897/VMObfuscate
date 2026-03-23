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




void VM::vm_print(){	
string arg1;
string final_string;
// 6 cause rdi or rcx is arg1
int args[5] ={-1,-1,-1,-1,-1};
#ifdef _WIN32
	// TODO: Complete for windows too
	arg1;
#elif defined(__linux__)
	// printf args are  pushed in this order rdi,rsi,rdx,rcx,r8,r9
	int rdi=tokens[TOKENS_TYPE::RDI];
	arg1 = vars[rdi].get_str();
	args[0] = tokens[TOKENS_TYPE::RSI]; 
	args[1] = tokens[TOKENS_TYPE::RDX]; 
	args[2] = tokens[TOKENS_TYPE::RCX]; 
	args[3] = tokens[TOKENS_TYPE::R8]; 
	args[4] = tokens[TOKENS_TYPE::R9]; 

#endif
	bool format_specifier = false;


	int arg_p = 0;
	int args_len = 5;
	int i =0;
	int size = arg1.length();
	bool pop_stack = false;
	while(i<size){
		char c = arg1[i];
		if(c == '%'){
			if(i+1 < size){
				i++;
				c = arg1[i];
				i++;
				if(arg_p >=args_len){
					pop_stack = true;
				}  	
				if(!pop_stack && ( args[arg_p] == -1 || vars.count(args[arg_p]) <=0)){
					final_string.push_back('%');
					final_string.push_back(c);
					continue;
				}
				Value val;  
				if(!pop_stack){
					val = vars[args[arg_p]];	
					arg_p++;
				}else{
					if(vm_stack.empty()){
						final_string.push_back('%');
						final_string.push_back(c);
						continue;
					}
					val = vm_stack.top();
					vm_stack.pop();
				}
				switch(c){
					case 'd': {
						final_string+=to_string(val.get_int());
						continue;			
					}
					case 'c':{
						final_string.push_back(val.get_int());
						continue;
					}
					case 's': {
						final_string+=val.get_str();
						continue;			
					}
					default:{
						final_string.push_back('%');
						final_string.push_back(c);
						continue;	
					 } 
				}
			}
		}
	

		i++;
		final_string.push_back(c);


	}

	cout << final_string;

	

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
	#ifdef _WIN32
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
	#endif

		case INTERNAL_FUNCTION::CALL_printf:{
			vm_print();	
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
	int i = range[0];
	 while(true){
		auto& inst = code[i];
		i++;
		int var_id;
		if(inst.opcode==tokens[TOKENS_TYPE::CALL]){
				if (internal_function_map.count(inst.operand1)) {
					handle_internal_function(internal_function_map[inst.operand1]);
				} else if (function_addr.count(inst.operand1)) {
					range = function_addr[inst.operand1];
					vm_call_stack.push(i);
					i = range[0];
				} else {
					cerr << "[error] Unknown function: " << inst.operand1 << "\n";
				}
		}else if(inst.opcode==tokens[TOKENS_TYPE::MOV]){
				var_id = stoi(inst.operand1);
				Value val;
				if(inst.operand2.starts_with("0x")){
					val = stoi(inst.operand2, nullptr, 16);
				}else{
					int var_id2 = stoi(inst.operand2);
					val = vars[var_id2];	
				}
				vars[var_id] = val;
		}else if(inst.opcode==tokens[TOKENS_TYPE::LEA]){
				var_id = stoi(inst.operand1);
				string hexstr = inst.operand2;
				string result;
				fromhex(hexstr,result);
				vars[var_id] = result;
		}else if(inst.opcode == tokens[TOKENS_TYPE::PUSH]){
				Value val;
				if(inst.operand1.starts_with("0x")){
					val = Value(stoi(inst.operand1,nullptr,16));
				}else{
					var_id = stoi(inst.operand1);
					val = vars[var_id];
				}
				vm_stack.push(val);

		}else if(inst.opcode==tokens[TOKENS_TYPE::ADD]){
				var_id = stoi(inst.operand1);
				int val;
				if(inst.operand2.starts_with("0x")){
					val = stoi(inst.operand2, nullptr, 16);
				}else{
					int var_id2 = stoi(inst.operand2);
					val = vars[var_id2].get_int();	
				}
				vars[var_id] = vars[var_id].get_int() + val;
		}else if(inst.opcode==tokens[TOKENS_TYPE::RET]){
			if(vm_call_stack.empty())
				return;
			i = vm_call_stack.top();
			vm_call_stack.pop();
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

#include<iostream>
#include<fstream>
#include<sstream>
#include<regex>
#include <unordered_map>
#include <variant>
#include"const.h"
#include<windows.h>
using namespace std;
class VM{
	
    private:
	unordered_map<string, VMC::INTERNAL_FUNCTION> internal_function_map = {
    {"__imp_MessageBoxA", VMC::INTERNAL_FUNCTION::MessageBoxA},
    {"__mingw_printf", VMC::INTERNAL_FUNCTION::printf},
	};
    unordered_map<int, variant<int, string>> vars;
	vector<VMC::Instruction> code;
	unordered_map<string, vector<int>> function_addr;

    stringstream buffer;
    public:
    VM(string filename){
		
        ifstream f(filename,ios::binary);
        if (!f.is_open()) {
                cerr << "Error opening the file!";
                return;
        }

		char key;
		f.read(&key, 1);
	
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
	void load_vmo(){
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
					VMC::Instruction inst;
					getline(l, t, del);
					int opcode_int=stoi(t);
					if (opcode_int < static_cast<int>(VMC::push) || opcode_int > static_cast<int>(VMC::div)) {
						throw std::invalid_argument("Invalid opcode value: " + t);
					}
					inst.opcode=static_cast<VMC::OPCODES>(stoi(t));
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
	void handle_internal_function(VMC::INTERNAL_FUNCTION func) {
		switch (func) {
			case VMC::INTERNAL_FUNCTION::MessageBoxA:{
				int arg1,arg4;
				string arg2,arg3;
				if (vars.count(VMC::REGISTERS::rcx) && holds_alternative<int>(vars[VMC::REGISTERS::rcx]))
					arg1 = get<int>(vars[VMC::REGISTERS::rcx]);

				if (vars.count(VMC::REGISTERS::rdx) && holds_alternative<string>(vars[VMC::REGISTERS::rdx]))
					arg2 = get<string>(vars[VMC::REGISTERS::rdx]);

				if (vars.count(VMC::REGISTERS::r8) && holds_alternative<string>(vars[VMC::REGISTERS::r8]))
					arg3 = get<string>(vars[VMC::REGISTERS::r8]);

				if (vars.count(VMC::REGISTERS::r9) && holds_alternative<int>(vars[VMC::REGISTERS::r9]))
					arg4 = get<int>(vars[VMC::REGISTERS::r9]);
				 MessageBoxA(
					(HWND)(uintptr_t)arg1,      
					arg2.c_str(),                
					arg3.c_str(),              
					arg4                  
				);
				vars.erase(VMC::REGISTERS::rcx);
				vars.erase(VMC::REGISTERS::rdx);
				vars.erase(VMC::REGISTERS::r8);
				vars.erase(VMC::REGISTERS::r9);

				break;
			}

			case VMC::INTERNAL_FUNCTION::printf:{
				string arg1;				
				if (vars.count(VMC::REGISTERS::rcx) && holds_alternative<string>(vars[VMC::REGISTERS::rcx]))
					arg1 = get<string>(vars[VMC::REGISTERS::rcx]);
				printf(arg1.c_str());
				vars.erase(VMC::REGISTERS::rcx);
				break;
				
			}

			default:
				cerr << "[internal] Unknown internal function\n";
				break;
		}
	}
	void fromhex(string& hexstr,string& result){
			if (hexstr.rfind("0x", 0) != string::npos) hexstr = hexstr.substr(2);
			for (size_t i = 0; i < hexstr.length(); i += 2) {
				string byteStr = hexstr.substr(i, 2);
				char c = static_cast<char>(stoi(byteStr, nullptr, 16));
				result.push_back(c);
			}
	}
	void run_function(const string& func_name) {
    if (function_addr.find(func_name) == function_addr.end()) {
        cerr << "Function not found: " << func_name << "\n";
        return;
    }
	
    auto range = function_addr[func_name];
    for (int i = range[0]; i <= range[1]; ++i) {
        auto& inst = code[i];
		int var_id;
        switch (inst.opcode) {
            case VMC::OPCODES::call:{
                if (internal_function_map.count(inst.operand1)) {
					handle_internal_function(internal_function_map[inst.operand1]);
				} else if (function_addr.count(inst.operand1)) {
					run_function(inst.operand1);
				} else {
					cerr << "[error] Unknown function: " << inst.operand1 << "\n";
				}
				break;
			}

            case VMC::OPCODES::mov:{
				var_id = stoi(inst.operand1);
				int val = stoi(inst.operand2, nullptr, 0);
				vars[var_id] = val;
                break;
			}
			case VMC::OPCODES::lea:{
				var_id = stoi(inst.operand1);
				string hexstr = inst.operand2;
				string result;
				fromhex(hexstr,result);
				vars[var_id] = result;
				break;
			}
            case VMC::OPCODES::ret:{
                return;
			}

            default:
                cout << "[unhandled opcode] " << static_cast<int>(inst.opcode) << "\n";
                break;
        }
    }
}
	void start_runtime(){
		run_function("main");
		
	}
	
};
int main(){
    VM vm =VM("payload.vmo");
    vm.start_runtime();
    return 0;
}

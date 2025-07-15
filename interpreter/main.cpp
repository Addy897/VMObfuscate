#include<iostream>
#include<fstream>
#include<sstream>
#include<regex>
#include <unordered_map>
#include"const.h"
using namespace std;
class VM{
	
    private:
	vector<VMC::Instruction> code;
	unordered_map<string, vector<int>> function_addr;

    stringstream buffer;
    public:
    VM(string filename){
        ifstream f(filename);
        if (!f.is_open()) {
                cerr << "Error opening the file!";
                return;
        }
        buffer<<f.rdbuf();
		f.close();
    }
	void start_runtime(){
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
		for (const auto& addr_vec : function_addr["main"]) {
			cout << ", start: " << addr_vec<<"\n";
			
		}
	}
	
};
int main(){
    VM vm =VM("test32.vmo");
    vm.start_runtime();
    return 0;
}

#include <string>
#include <vector>

#include"value.h"


#ifdef _WIN32
#include<windows.h>
#endif
#include<iostream>
#include<fstream>
#include<sstream>
#include<regex>
#include <unordered_map>
#include<array>
#include<stdint.h>
#include<stack>
#define TOKENS_LEN 27
using namespace std;


class VM {
	 private:
		 enum TOKENS_TYPE {
			ADD=0,CALL=1,CMP=2,DIV=3,JB=4,JE=5,JG=6,JMP=7,JNE=8,
			LEA=9,MOV=10,MUL=11,POP=12,PUSH=13,R8=14,R9=15,RAX=16,
			RBP=17,RBX=18,RCX=19,RDI=20,RDX=21,RET=22,RSI=23,
			RSP=24,SUB=25,TEST=26,
		};
		array<int,TOKENS_LEN> tokens;
		stack<Value> vm_stack;
		stack<int> vm_call_stack;
		uint8_t vm_flags;
		

		struct Instruction {
			unsigned char opcode;
			string operand1;
			string operand2;
			
		};
		// TO CALL
		enum INTERNAL_FUNCTION{
			 CALL_MessageBoxA, 
			 CALL_printf,
		};
		unordered_map<string, INTERNAL_FUNCTION> internal_function_map = {
			#ifdef _WIN32
			{"__imp_MessageBoxA", INTERNAL_FUNCTION::CALL_MessageBoxA},
			#endif
			{"__mingw_printf", INTERNAL_FUNCTION::CALL_printf},
			{"printf", INTERNAL_FUNCTION::CALL_printf},
			{"puts", INTERNAL_FUNCTION::CALL_printf},
		};
		unordered_map<int, Value> vars;
		vector<Instruction> code;
		unordered_map<string, vector<int>> function_addr;

		stringstream buffer;
	private: 
		void load_vmo();
		void handle_internal_function(INTERNAL_FUNCTION func);
		void fromhex(string&,string&);
		void vm_print();
		void run_function(const string&);

    public:
		VM(string);
		void start_runtime();

	

};

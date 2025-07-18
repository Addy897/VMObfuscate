#include <string>
#include <vector>
#include<windows.h>
#include<iostream>
#include<fstream>
#include<sstream>
#include<regex>
#include <unordered_map>
#include <variant>
#include<array>
#define TOKENS_LEN 27
using namespace std;
enum class ValueType {
    INT,
    FLOAT,
    BOOL,
    STRING
};

struct Value {
    ValueType type;
    union {
        int i;
        float f;
        bool b;
        string* s;
    };
	Value() : type(ValueType::INT), i(0) {}
    Value(int val) : type(ValueType::INT), i(val) {}
    Value(float val) : type(ValueType::FLOAT), f(val) {}
    Value(bool val) : type(ValueType::BOOL), b(val) {}
    Value(const std::string& val) : type(ValueType::STRING), s(new std::string(val)) {}
    ~Value() {
        if (type == ValueType::STRING) {
            delete s;
        }
    }
	Value(const Value& other) : type(other.type) {
		switch (type) {
			case ValueType::INT: i = other.i; break;
			case ValueType::FLOAT: f = other.f; break;
			case ValueType::BOOL: b = other.b; break;
			case ValueType::STRING: s = new std::string(*other.s); break;
			default: i = 0; break;
		}
	}
    Value& operator=(const Value& other) {
        if (this != &other) {
            if (type == ValueType::STRING) delete s;

            type = other.type;
            switch (type) {
                case ValueType::INT: i = other.i; break;
                case ValueType::FLOAT: f = other.f; break;
                case ValueType::BOOL: b = other.b; break;
                case ValueType::STRING: s = new std::string(*other.s); break;
            }
        }
        return *this;
    }
	int get_int(){
		return i;
	}
	bool get_bool(){
			return b;
	}
	float get_float(){
		return f;
	}
	string get_str(){
			return *s;
	}
};

class VM {
	 private:
		 enum TOKENS_TYPE {
			ADD=0,CALL=1,CMP=2,DIV=3,JB=4,JE=5,JG=6,JMP=7,JNE=8,
			LEA=9,MOV=10,MUL=11,POP=12,PUSH=13,R8=14,R9=15,RAX=16,
			RBP=17,RBX=18,RCX=19,RDI=20,RDX=21,RET=22,RSI=23,
			RSP=24,SUB=25,TEST=26,
		};
		array<int,TOKENS_LEN> tokens;
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
			{"__imp_MessageBoxA", INTERNAL_FUNCTION::CALL_MessageBoxA},
			{"__mingw_printf", INTERNAL_FUNCTION::CALL_printf},
		};
		unordered_map<int, Value> vars;
		vector<Instruction> code;
		unordered_map<string, vector<int>> function_addr;

		stringstream buffer;
	private: 
		void load_vmo();
		void handle_internal_function(INTERNAL_FUNCTION func);
		void fromhex(string&,string&);
		void run_function(const string&);

    public:
		VM(string);
		void start_runtime();

	

};

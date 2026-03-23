#pragma once 
#include<iostream>
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
        std::string* s;
    };
	Value() : type(ValueType::INT), i(0) {}
	Value(int val) : type(ValueType::INT), i(val) {}
	Value(float val) : type(ValueType::FLOAT), f(val) {}
	Value(bool val) : type(ValueType::BOOL), b(val) {}
	~Value();
	Value(const std::string& val) : type(ValueType::STRING), s(new std::string(val)) {}
	Value(const Value& other);
	Value& operator=(const Value& other);
	int get_int();
	bool get_bool();
	float get_float();
	std::string get_str();
};

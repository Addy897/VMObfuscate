#include"value.h"
Value::~Value() {
	if (type == ValueType::STRING) {
		delete s;
	}
}
Value::Value(const Value& other) : type(other.type) {
	switch (type) {
		case ValueType::INT: i = other.i; break;
		case ValueType::FLOAT: f = other.f; break;
		case ValueType::BOOL: b = other.b; break;
		case ValueType::STRING: s = new std::string(*other.s); break;
		default: i = 0; break;
	}
}
Value& Value::operator=(const Value& other) {
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
int Value::get_int(){return i;}
bool Value::get_bool(){return b;}
float Value::get_float(){ return f; }
std::string Value::get_str(){return *s;}

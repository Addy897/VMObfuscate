#include <string>
#include <vector>

using std::string;
using std::vector;

namespace VMC {

enum OPCODES {
    push=0x1,
    pop=0x2,
    mov=0x3,
    lea=0x4,
    ret=0x5,
    call=0x6,
    cmp=0x7,
    test=0x8,
    jmp=0x9,
    jg=0xA,
    je=0xB,
    jne=0xC,
    jb=0xD,
    add=0xE,
    sub=0xF,
    mul=0x10,
    div=0x11
};

struct Instruction {
    OPCODES opcode;
    string operand1;
	string operand2;
	
};

enum REGISTERS {
    rax=31,eax=31,ax=31,ah=31,al=31,
    rbx=32,ebx=32,bx=32,bl=32,bh=32,
    rcx=33,ecx=33,cx=33,cl=33,ch=33,
    rdx=34,edx=34,dx=34,dl=34,dh=34,
    rsi=35,esi=35,si=35,sil=35,
    rdi=36,edi=36,di=36,dil=36,
    rsp=37,esp=37,sp=37,spl=37,
    rbp=38,ebp=38,bp=38,bpl=38,
    r8=39,r8d=39,r8w=39,r8b=39,
    r9=40,r9d=40,r9w=40,r9b=40
};

}

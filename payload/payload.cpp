#include <windows.h>
#include<stdio.h>
void payload() {
    MessageBoxA(nullptr, "This is VM-payload", "Demo", MB_OK);
	printf("test\n");
}

int main() {
    payload();
    return 0;
}

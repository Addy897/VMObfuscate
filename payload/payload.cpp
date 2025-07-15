#include <windows.h>
void payload() {
    MessageBoxA(nullptr, "This is VM-payload", "Demo", MB_OK);

}

int main() {
    payload();
    return 0;
}

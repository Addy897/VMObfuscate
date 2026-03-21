
#include<stdio.h>
void add(int a,int b) {
	printf("a + b = %d\n",a+b);
}
void sub(int a,int b) {
	printf("a - b = %d\n",a-b);
}
void mul(int a,int b) {
	printf("a * b = %d\n",a*b);
}
int main() {
   
    add(4,5);
    sub(5,4);
    mul(4,5);
    return 0;
}


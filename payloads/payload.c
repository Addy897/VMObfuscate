
#include<stdio.h>


int add(int x){
	if(x < 2){
		return 1;
	}else{

		return x*add(x-1);
	}
}
int main() {
  	printf("Factorial of 5 is: %d\n",add(5)); 
	return 0;
}


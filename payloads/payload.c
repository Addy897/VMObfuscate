
#include<stdio.h>


int fact(int x){
	if(x < 2){
		return 1;
	}else{

		return x*fact(x-1);
	}
}
int main() {
	int x = fact(10);
	if(x<1000)
  	printf("Factorial  is: %d\n",x); 
	else
  	printf("Factorial: %d\n",x); 
	return 0;
}


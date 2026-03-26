
#include <stdio.h>
#if 1
int fact(int x) {
  if (x < 2) {
    return 1;
  } else {

    return x * fact(x - 1);
  }
}
int main() {
  int x = fact(10);
  if (x < 1000)
    printf("Factorial  is: %d\n", x);
  else
    printf("Factorial: %d\n", x);
  return 0;
}
#else

int main() {
  printf("Hello World %d %d %d %d %d %s %c\n", 1, 2, 3, 4, 5, "SIX", 65);
  return 0;
}

#endif

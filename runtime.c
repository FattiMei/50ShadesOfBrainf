#include <stdio.h>


int run(char *memory);


#ifndef MEMORY_SIZE
#define MEMORY_SIZE 1000
#endif


char memory[MEMORY_SIZE] = {0};


int main() {
	int ok = run(memory);

	if (ok != 0) {
		printf("Found an infinite loop... quitting\n");
		return 1;
	}

	return 0;
}

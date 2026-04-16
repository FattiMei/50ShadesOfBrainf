void run(char *memory);


#ifndef MEMORY_SIZE
#define MEMORY_SIZE 1000
#endif


char memory[MEMORY_SIZE] = {0};


int main() {
	run(memory);
	return 0;
}

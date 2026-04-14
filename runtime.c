void run(char *memory);


#ifndef MEMORY_SIZE
#define MEMORY_SIZE 1000
#endif


char memory[MEMORY_SIZE];


int main() {
	for (int i = 0; i < MEMORY_SIZE; ++i) memory[i] = 0;
	run(memory);
	return 0;
}

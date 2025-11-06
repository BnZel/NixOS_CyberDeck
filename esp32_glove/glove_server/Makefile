CFLAGS = -g -std=c99 -Wall -Wextra -pedantic \
 -I. \
 -I/usr/local/include \

LDFLAGS = -g -L/usr/local/include 

build: clean main

main: main.o network.o
	gcc $^ -o $@ $(LDFLAGS)

main.o: main.c
	gcc $(CFLAGS) -c $< -o $@

network.o: src/network.c
	gcc $(CFLAGS) -c $< -o $@

run: main
	./main

debug: clean main
	gdb --tui ./main

clean:
	echo `clear`
	rm -f main *.o 

all: clean build run

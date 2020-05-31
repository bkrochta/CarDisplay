CC = gcc
CCFLAGS := -Iinclude -g -Wall `pkg-config --cflags gtk+-3.0`
LDFLAGS = -lpthread -lm `pkg-config --libs gtk+-3.0`
PROGS = car_display

CFILES := $(wildcard src/*.c)
OBJFILES := $(addprefix obj/, $(notdir $(CFILES:%.c=%.o)))

all: $(PROGS)

$(PROGS): $(OBJFILES)
	$(CC) $(LDFLAGS) -o $@ $^

obj/%.o: src/%.c include/%.h
	$(CC) $(CCFLAGS) -c -o $@ $<

clean:
	rm -rf obj/* car_display
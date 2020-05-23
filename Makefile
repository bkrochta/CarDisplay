CC = gcc
CCFLAGS := -Iinclude
LDFLAGS = -lpthread
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
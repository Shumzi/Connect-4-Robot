CXX = g++
CXXFLAGS = -std=c++11 -Wall -Wextra -O3 -DNDEBUG

SRCS = Solver.cpp
OBJS = $(SRCS:.cpp=.o)

all: c4solver generator

c4solver: $(OBJS) main.o
	$(CXX) $(CXXFLAGS) -o c4solver.exe main.o $(OBJS)

generator: generator.o
	$(CXX) $(CXXFLAGS) -o generator.exe generator.o

clean:
	rm -f *.o c4solver.exe generator.exe
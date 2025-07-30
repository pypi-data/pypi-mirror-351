# Cyda
Cyda is a *much* simpler build system for C/C++. Designed after feeling lazy to write Makefiles for each new project. 

Whenever I started a new project in C/C++, I would always manually create folders to organize my code and then finally, create the Makefile. 
Here is what my makefile would *generally* look like at the start of a brand new project
```make
CC = gcc
CFLAGS = -Wall -Ilib
OBJ = lib/lib1.o lib/lib2.o
TARGET = main

all: $(TARGET)

$(TARGET): $(OBJ) src/main.o
	$(CC) -o $@ $^

lib/lib1.o: lib/lib1.c lib/lib1.h
	$(CC) $(CFLAGS) -c $< -o $@

lib/lib2.o: lib/lib2.c lib/lib2.h
	$(CC) $(CFLAGS) -c $< -o $@

src/main.o: src/main.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f lib/*.o src/*.o $(TARGET)
```
Multiple symbols like $<, $@, $^, etc. Although some of you may say 'just learn it, you'll get used to it', but *i was lazy.*

Here is what my *cydafile* looks like in new projects now:
```
compiler gcc
flags -Wall
// include lib => -Ilib
include lib
// Target main
exec main

// You'll notice that the header file for the c files are not given, cyda assumes that lib1.c has a coresponding lib1.h since its standard
file lib/lib1.c
file lib/lib2.c
file src/main.c
// This is like ~50% smaller than the makefile at the start of this readme!
```
Aaand you're done! 
No rules needed for .o, or cleaning the .o files later

Here is how it works -- 
```
%cyda --help
Welcome to using Cyda! A simpler CMake alternative.
Use --help  to get this message
Use --version  to, you know, get the installed version
Use --syntax  to get up to speed with the syntax of Cyda. Do visit the Github page for more information
Use --build  to build but not run the executable
Use --run  to build the files, clear the screen, and run the executable immediately
Use --clean  to clean the .o files generated
Use --new <project name>   -c/cpp   --compiler -gcc/g++/clang/clang++  to create a new template project. use -c or -cpp/-cxx/-c++ to specify project language type.
	   Optionally, specify the compiler using --compiler gcc/clang/clang++/g++/etc. By default cyda uses gcc/g++ :D

Use --makefile  to generate a makefile for the given cyda script
(Note: Some features like wildcards and setting output directories is not available for makefiles
    It generates files in the current directory and searches paths explicitly
    If you need those features, use --build/--run directly)
```
`--new <project name> -c/c++/cxx/cpp --compiler gcc/clang/g++/clang++` is the concept I borrowed from cargo, because once again, I was quite tired of setting up manually my folder structure. It automatically creates a new folder named `<project name>` with starter files for `C/C++` according to the flag and then optionally, you can specify the compiler. 
The folder structure it generates is quite standard --
```
PROJECT_NAME
  | --- libs/
  |       | --- lib1.c  / or lib1.cpp
  |       | --- lib1.h
  |
  | --- src/
  |       | --- main.c  / or main.cpp 
  |
  | --- cydafile
```
And the cydafile generated matches the folder structure already. 

Cyda Syntax: `use --syntax to learn as well ;)`
```
1. compiler <compiler name>
    - Select the desired compiler. Permitted values are gcc, g++, clang, clang++. You can choose a different compiler and override later, if you'd like.

2. flags <compiler flags>
    - Set the desired flags for the compiler. This is compiler dependant

3. include <paths/dirs to include in compilation>
    - This corresponds to -I flag in gcc, ignore if your compiler doesnt support it

4. file <filename, along with path>
    - This is the complete filename from the present working directory. e.g if its in the pwd, then main.c should suffice, else specify using src/main.c

5. set output obj <directory>
    - Determines where the generated object files will reside. e.g setting it to object_files will make it generate in ./object_files/*.o

5. set output exe <directory>
    - Determines where the generated executable will reside. e.g setting it to dist will make it generate in ./dist/*

6. exec <name>
    - Just sets the name of the final executable, can be anything
```

## NOTE -
Currently some features are missing which I will add in the future - 
  * ~~Ability to control where the output object files are located, although I wont add granular control for per file~~         - ADDED
  * ~~Ability to control where the output executable file is generated~~							- ADDED
  * Ability to add wildcard like `*.c` to dynamically add files to the compilation without needing to specify each one
  * More *motivating* quotes in the future (you'll know when you use --run/--build)
  
May or may not add support for assembly (linux only)


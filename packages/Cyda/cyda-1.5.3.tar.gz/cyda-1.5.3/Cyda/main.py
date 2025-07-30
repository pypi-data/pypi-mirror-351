import shlex, sys, os
from time import time as stopwatch
import random
from pathlib import Path
import platform

PLATFORM_NAME = platform.system()

# Some fun, totally motivating quotes for when the build fails
motivating_sentences = [
	"The disappointment of the gods is palpable",
	"Tsk tsk, Claude is coming",
	"Make it work or an LLM is gonna take your job",
	"I believe in you!",
	"GIT GUD",
	"........",
	"And you thought that would work?!?",
	"Remember that deadline? Yep, time to move it again.",
	"Remember that deadline? Yep, time to forget it.",
	"My LLM could write better code than that (I have no LLM)",
	"Forgot the semi-colon again? Sigh.",
	"Got a 19 page thesis summary of your template instantiation error? Sigh."
]
motivating_sentence = random.choice(motivating_sentences)

class Cydafile:
	def __init__(self, compiler:str, flags:str, files:list[str], include_paths:list[str], executable_name:str, output_obj:str, output_exe:str):
		self.compiler = compiler
		self.flags = flags
		self.files = files
		self.include_paths = include_paths
		self.executable_name = executable_name
		self.output_obj = output_obj
		self.output_exe = output_exe

def red(str):
	return f"\x1b[31m{str}\x1b[0m"

def green(str):
	return f"\x1b[32m{str}\x1b[0m"

def yellow(str):
	return f"\x1b[33m{str}\x1b[0m"

# Main function for parsing the cydafile itself
def read_cydafile() -> Cydafile:
	i = 1
	compiler = ""
	include_paths = []
	flags = ""
	executable_name = ""
	files = []
	output_obj = ""
	output_exe = ""

	if "cydafile" in os.listdir("."):
		for line in open("./cydafile", "r").readlines():
			command = shlex.split(line)
			if not len(command) > 0: continue   # if the command is empty, skip
			match command[0]:
				case "//":
					continue

				case "compiler":
					try:
						compiler = command[1]
					except:
						raise RuntimeError(f"Error on line {i}. Compiler not specified. Exiting...")

				case "set":
					try:
						command2 = command[1] + " " + command[2]
					except:
						raise RuntimeError(f"Error on line {i}. You didn't tell me *what* to set D: Exiting...")
					match command2:
						case "output obj":
							output_obj = command[3]
						case "output exe":
							output_exe = command[3]

				case "include":
					try:
						path = command[1]
					except:
						raise RuntimeError(f"Error on line {i}. Did you forget to add a include path? Exiting...")
					include_paths.append(path)

				case "flags":
					flags = " ".join([flag for flag in command[1:]])
				
				case "file":
					try:
						files.append(command[1])
					except:
						raise RuntimeError(f"Error on line {i}. File name not specified. Exiting...")


				case "exec":
					if executable_name != "":
						raise RuntimeError(f"Error on line {i}. Executable name already set to {executable_name}.\nPlease mention only one executable name. Exiting...")
					else:
						try:
							executable_name = command[1]
						except:
							raise RuntimeError(f"Error on line {i}. Executable name not specified. Exiting...")
			i+=1

		if compiler == "":
			raise RuntimeError("Compiler not set. Exiting...")
		if len(files) == 0:
			raise RuntimeError("No files given. Exiting...")
		if executable_name == "":
			raise RuntimeError("Executable name not set. Exiting...")
	else:
		raise RuntimeError("Uh, cydafile isn't found in this directory. Exiting...")
	
	return Cydafile(compiler, flags, files, include_paths, executable_name, output_obj, output_exe)

def get_last_modified_exe(path:str):
	if (PLATFORM_NAME == "Windows"):
		return os.path.getmtime(f"./{path}.exe")
	else:
		return os.path.getmtime(f"./{path}")
	

def compile_files(cyda:Cydafile) -> tuple[bool, list[str]]:
	"""
	
	If compilation succeeds, returns True
	else returns False

	Also returns list of obj files generated
	
	"""
	
	if cyda.compiler not in ["gcc", 'g++', 'clang', 'clang++']:
		i = input("I dont know the given compiler. Are you sure you want to proceed? (You can change the compiler later in the cydafile) [y/N]:")
		if i == "n" or not i:
			raise RuntimeError(red("Unrecognised compiler. Exiting..."))

	start = stopwatch()
	total = len(cyda.files)
	success = 0
	obj_files = []
	if cyda.output_obj == "": cyda.output_obj = "."
	else: Path(f"./{cyda.output_obj}/").mkdir(exist_ok=True)
	if cyda.output_exe == "": cyda.output_exe = "."
	else: Path(f"./{cyda.output_exe}/").mkdir(exist_ok=True)

	for file in cyda.files:
		fn = file.split(".")[0]
		fn = fn.split("/")
		fn = fn[len(fn) - 1]
		obj_files.append(f"{cyda.output_obj}/{fn}.o")
		mod_obj = os.path.getmtime(f"{cyda.output_obj}/{fn}.o")
		mod_c   = os.path.getmtime(file)
		if mod_c > mod_obj:
			exit_code = os.system(f"{cyda.compiler} {cyda.flags} {' '.join(f'-I{d}' for d in cyda.include_paths)} -c {file} -o {cyda.output_obj}/{fn}.o")
			if exit_code == 0:
				success += 1
		else:
			total -= 1

	end = stopwatch()

	print("\n-------------------------------------------")
	print(f"DURATION: {round(end-start, 3)}s")
	if total == 0:
		print(yellow("*** Nothing to do, already up to date object files. ***"))
		return (True, obj_files)
	else:
		print(green(f"OK: {success}/{total}"))
		print(red(f"FAIELD: {total-success}/{total}"))
		return (success == total, obj_files)

def need_recompile_executable(cyda) -> bool:
	final_exe_time = 0
	if (PLATFORM_NAME == "Windows"):
		final_exe_time = get_last_modified_exe(f"./{cyda.output_exe}/{cyda.executable_name}.exe")
	else:
		final_exe_time = get_last_modified_exe(f"./{cyda.output_exe}/{cyda.executable_name}")
	for file in cyda.files:
		fn = file.split(".")[0]
		fn = fn.split("/")
		fn = fn[len(fn) - 1]
		mod_obj_time = os.path.getmtime(f"{cyda.output_obj}/{fn}.o")
		if mod_obj_time > final_exe_time:
			return True
	return False
		

def build():
	"""
	
	The function that is called when --build is used
	
	"""
	cyda = read_cydafile()
	result = compile_files(cyda)
	
	if not need_recompile_executable(cyda):
		print(yellow("*** The executable is already up to date ***"))
		print(yellow("*** Nothing to do, exiting... ***"))
		sys.exit(0)

	# result[0] is the success of the compilation, result[1] is the list of object files
	if result[0]:
		os.system(f"{cyda.compiler} {cyda.flags} {' '.join(f'-I{d}' for d in cyda.include_paths)} {" ".join(result[1])} -o {cyda.output_exe}/{cyda.executable_name}")
	else:
		print(yellow(motivating_sentence))

def run():
	"""
	
	The function that is called when --run is used
	
	"""
	cyda = read_cydafile()
	result = compile_files(cyda)

	# result[0] is the success of the compilation, result[1] is the list of object files
	if result[0]:
		print(green(f"No failed compiles. Hurray!"))
		if need_recompile_executable(cyda):
			os.system(f"{cyda.compiler} {cyda.flags} {' '.join(f'-I{d}' for d in cyda.include_paths)} {" ".join(result[1])} -o {cyda.output_exe}/{cyda.executable_name}")
		else:
			print(yellow("*** The executable is already up to date ***"))
		print("-------------------------------------------\n")
		os.system(f"./{cyda.output_exe}/{cyda.executable_name}")
	else:
		print(red(f"FAILED IN RUNNING."))
		print(yellow(motivating_sentence))


def clean():
	"""
	
	The function that is called when --clean is used

	"""
	cyda = read_cydafile()
	if cyda.output_obj == "": cyda.output_obj = "."
	else: Path(f"./{cyda.output_obj}/").mkdir(exist_ok=True)
	if cyda.output_exe == "": cyda.output_exe = "."
	else: Path(f"./{cyda.output_exe}/").mkdir(exist_ok=True)

	for file in cyda.files:
		fn = file.split(".")[0]
		fn = fn.split("/")
		fn = fn[len(fn) - 1]
		os.system(f"rm -f ./{cyda.output_obj}/{fn}.o")

	if PLATFORM_NAME == "Windows":
		os.system(f"rm -f ./{cyda.output_exe}/{cyda.executable_name}.exe")
	else:
		os.system(f"rm -f ./{cyda.output_exe}/{cyda.executable_name}")

def generate_makefile():
	"""
	
	The function that is called when --makefile is used
	It does not support all functionality yet

	"""
	cyda = read_cydafile()
	if cyda.output_obj != "" or cyda.output_exe != "":
		print(red("Please note that Cyda currently does not support generating makefiles that include\n  - Custom object file output directories\n  - Custom executable output directories\n  - Wildcards for files"))

	with open("Makefile", "w+") as file:
		file.truncate(0)
		
		# COMPILERS AND FLAGS
		file.writelines([
			f"CC = {cyda.compiler}\n",
			f"CFLAGS = {cyda.flags}\n",
			"\n",  
		])

		# FILE RULES
		for f in cyda.files:
			splitfilename = f.split(".")
			objfilename = splitfilename[0].split("/")
			objfilename = objfilename[len(objfilename) - 1]
			print(splitfilename[0], objfilename)
			file.write(f"\n{objfilename}.o: {f}\n	$(CC) $(CFLAGS) {' '.join(f'-I{d}' for d in cyda.include_paths)} -c {splitfilename[0]}.c -o {objfilename}.o\n")
		file.write("\n")

		# FINAL EXECUTABLE RULE
		file.write(f"{cyda.executable_name}: ")   
		for f in cyda.files:
			splitfilename = f.split(".")
			objfilename = splitfilename[0].split("/")
			objfilename = objfilename[len(objfilename) - 1]
			
			file.write(f"{objfilename}.o ")
			
		file.write("\n	$(CC) ")
		
		for f in cyda.files:
			splitfilename = f.split(".")
			objfilename = splitfilename[0].split("/")
			objfilename = objfilename[len(objfilename) - 1]
			
			file.write(f"{objfilename}.o ")
			
		file.write(f"{' '.join(f'-I{d}' for d in cyda.include_paths)} -o {cyda.executable_name}\n")

		
		# CLEAN AND RUN RULES
		file.write("clean: \n")
		file.write(f"	rm -f *.o {cyda.executable_name}\n")

		file.write("run:\n")
		file.write(f"	make {cyda.executable_name}\n")
		
	print(green("If you see this message, your makefile is ready!"))

def new_project(name, projtype, compiler_name):
	"""
	
	The function that is called when new projects are made. Supports C/C++ project types and gnu or clang compilers

	"""
	if projtype not in ["-c", "-cpp", "-c++", "-cxx"]:
		raise RuntimeError(red(f"I don't know the specified project type {projtype} D:"))
	
	if compiler_name not in ["gcc", 'g++', 'clang', 'clang++']:
		i = input("I dont know the given compiler. Are you sure you want to proceed? (You can change the compiler later in the cydafile) [y/N]:")
		if i == "n" or not i:
			raise RuntimeError(red("Unrecognised compiler. Exiting..."))
	
	os.makedirs(f"./{name}/libs")
	os.makedirs(f"./{name}/src")
	if projtype == "-c":
		if compiler_name in ["g++", "clang++"]:
			print(red("Incompatible compiler for cxx used. Using fallback gcc"))
		compiler_name = "gcc"
		
		with open(f"{name}/src/main.c", "w+") as file:
			file.writelines([
				"#include <stdio.h>\n"
				"#include \"lib.h\"      // Cyda manages include paths! no need to specify!\n"
				"\n",
				"int main(){\n"
				"	printf(\"Hello Cyda!\\n\");\n",
				"	hello_from_lib();\n"
				"	return 0;\n",
				"}\n"
			])

		with open(f"{name}/libs/lib.c", "w+") as file:
			file.writelines([
				"#include <stdio.h>\n"
				"\n",
				"void hello_from_lib(){\n"
				"	printf(\"Hi there!\\n\");\n"
				"}\n"
			])

		with open(f"{name}/libs/lib.h", "w+") as file:
			file.writelines([
				"#pragma once\n",
				"\n",
				"void hello_from_lib();\n"
			])
		
		with open(f"{name}/cydafile", "w+") as file:
			file.writelines([
				f"compiler {compiler_name}\n",
				"flags -Wall \n",
				"// Turning on warnings, Write good code for the sake of Torvalds, okay?\n",
				"include libs\n",
				"// This is also a flag, it sets -I\n",
				" \n",
				"// BTW, // itself is a command, for comments :p\n",
				"file src/main.c\n",
				"file libs/lib.c   // explicit path to be given\n",
				"set output obj objs_directory\n",
				"set output exe dist\n",
				f"exec {name}\n"
			])

	elif projtype != "-c":
		if compiler_name in ["gcc", "clang"]:
			print(red("Incompatible compiler for cxx used. Using fallback g++"))
		
		compiler_name = "g++"
		with open(f"{name}/src/main.cpp", "w+") as file:
			file.writelines([
				"#include <iostream>\n"
				"#include \"lib.h\"      // Cyda manages include paths! no need to specify!\n"
				" \n",
				"int main(){\n"
				"	std::cout << \"Hello from Cyda!\" << std::endl;\n",
				"	std::cout << add_from_lib(3,5) << \"\\n\" << std::endl;\n",
				"	return 0;\n",
				"}\n"
			])

		with open(f"{name}/libs/lib.cpp", "w+") as file:
			file.writelines([
				"#include <iostream>\n",
				"\n",
				"int add_from_lib(int a, int b){\n",
				"	return a + b;\n",
				"}\n",
			])

		with open(f"{name}/libs/lib.h", "w+") as file:
			file.writelines([
				"#pragma once\n",
				" \n",
				"int add_from_lib(int, int);\n"
			])
		
		with open(f"{name}/cydafile", "w+") as file:
			file.writelines([
				f"compiler {compiler_name}\n",
				"flags -Wall   \n",
				"// Turning on warnings, Write good code for the sake of Torvalds, okay?\n" 
				"include libs   ",
				"// This is also a flag, it sets -I\n"
				" \n",
				"// BTW, // itself is a command, for comments :p\n",
				"file src/main.cpp\n",
				"file libs/lib.cpp   // explicit path to be given\n",
				"set output obj objs_directory\n",
				"set output exe dist\n",
				f"exec {name}\n"
			])
	print(green(f"Project creation complete with name {name}!"))


# lazy
def y(s):
	return yellow(s)

def show_version_information():
	print("Currently running on version " + yellow("v1.5.0"))
	print("Recent additions include:\n    * Refactored code (you're welcome Github)\n    * Made open source and pushed on " + yellow("Github") + " btw!\n    * Output directories for " + yellow("object files") + " and " + yellow("executable") + "\n    * Added new command line arguments\n" + "\nThank you for using " + yellow("Cyda") + "! Please let the author know if you have any suggestions!")

def teach_syntax():
	print(yellow("Quick, time to get you up and running with Cyda as soon as possible!"))
	print(f"1. {y("compiler")} <compiler name>")
	print(f"    - Select the desired compiler. Permitted values are {y("gcc, g++, clang, clang++")}. You can choose a different compiler and {red("override")} later, if you'd like.\n")
	print(f"2. {y("flags")} <compiler flags>")
	print(f"    - Set the desired flags for the compiler. This is compiler dependant\n")
	print(f"3. {y("include")} <paths/dirs to include in compilation>")
	print(f"    - This corresponds to {y("-I")} flag in {y("gcc")}, ignore if your compiler doesnt support it\n")
	print(f"4. {y("file")} <filename, along with path>")
	print(f"    - This is the complete filename from the present working directory. e.g if its in the pwd, then {y("main.c")} should suffice, else specify using {y("src/main.c")}\n")
	print(f"5. {y("set output obj")} <directory>")
	print(f"    - Determines where the generated {y("object")} files will reside. e.g setting it to {y("object_files")} will make it generate in ./{y("object_files")}/*.o\n")
	print(f"5. {y("set output exe")} <directory>")
	print(f"    - Determines where the generated {y("executable")} will reside. e.g setting it to {y("dist")} will make it generate in ./{y("dist")}/*\n")
	print(f"6. {y("exec")} <name>")
	print(f"    - Just sets the name of the final executable, can be anything\n")
	print(f"And you're done! You know the basics of Cyda now! Have fun and I hope you find it easier than other build tools :p\n")

def show_help_information():
	print(yellow("Welcome to using Cyda! A simpler CMake alternative."))
	print("Use " + yellow("--help")     + "  to get this message")
	print("Use " + yellow("--version")  + "  to, you know, get the installed version")
	print("Use " + yellow("--syntax")   + "  to get up to speed with the syntax of Cyda. Do visit the Github page for more information")
	print("Use " + yellow("--build")    + "  to build but not run the executable")
	print("Use " + yellow("--run")      + "  to build the files, clear the screen, and run the executable immediately")
	print("Use " + yellow("--clean")    + "  to clean the .o files generated")
	print("Use " + yellow("--new <project name>   -c/cpp   --compiler -gcc/g++/clang/clang++") + "  to create a new template project. use -c or -cpp/-cxx/-c++ to specify project language type.\n	   Optionally, specify the compiler using --compiler gcc/clang/clang++/g++/etc. By default cyda uses gcc/g++ :D\n")
	print("Use " + yellow("--makefile") + "  to generate a makefile for the given cyda script\n(Note: Some features like wildcards and setting output directories is not available for makefiles\n    It generates files in the current directory and searches paths explicitly\n    If you need those features, use --build/--run directly)\n")

def main():
	# Now for parsing the command line arguments
	commands = sys.argv[1:]

	if len(commands) == 0:	
		print("Use "+ yellow("--help") + " for, you guessed it, getting help.")
		sys.exit(1)

	match commands[0]:
		case "--help":
			show_help_information()
		case "--version":
			show_version_information()
		case "--syntax":
			teach_syntax()
		case "--build":
			build()
		case "--run":
			run()
		case "--clean":
			clean()
		case "--makefile":
			generate_makefile()
		case "--new":
			try:
				name = commands[1]
			except:
				print(red("Name of project not specified. Exiting..."))
				sys.exit(1)
			try:
				_type = commands[2]
			except:
				print(red("Project type (C/C++) not specified. Exiting..."))
				sys.exit(1)
			
			try:
				compiler_name = commands[3]
			except:
				if _type == "-c":
					compiler_name = "gcc"
				else:
					compiler_name = "g++"

			new_project(name, _type, compiler_name)


main()
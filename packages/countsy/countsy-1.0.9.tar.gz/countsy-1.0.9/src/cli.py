import glob
import os
from tqdm import tqdm
import sys
from src.parsing import *
from src.output_formatting import *
from src.counting import *

# TODO: more programming languages

		
def main():
	args = init_parser()
	
	all_python_files = return_all_files_in_folder(args.folder_path)
	
	# If returned element is a list, the folder_path was valid
	if isinstance(all_python_files, list):
		# If returned list is empty, no Python-Files have been found
		if not all_python_files:
			print(f"There are no Python-Files in {args.folder_path}")
			sys.exit(1)
		raw_output = return_sum_of_lines_in_folder(all_python_files, args)
		
		format_output(raw_output, all_python_files, args)
		
	else:
		print(all_python_files)
	
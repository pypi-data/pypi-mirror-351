def format_output(raw_output, all_python_files, args):
	"""
	Format and print the output results
	:param raw_output: Results from return_sum_of_lines_in_folder
	:param all_python_files: List of all Python files processed
	:param args
	"""
	
	if "errors" in raw_output:
		print("Errors encountered:")
		for error in raw_output["errors"]:
			print(f"  - {error}")
		print()
	try:
		key = next(k for k in raw_output.keys() if k != "errors")
		value = raw_output[key]
	except StopIteration:
		# nothing but errors, we already printed them above
		from sys import exit
		exit(1)
		return 1

	if len(all_python_files) != 1:
		name = "directory"
		line = "  Total files in "

		if args.folder_path == "./":
			line += f"current {name}: "
		else:
			line += f"{args.folder_path}: "
		line += str(len(all_python_files))
		print(line)  # Output specific message
	else:
		name = "file"

	if key == "no_tracking":
		print(f"  Total lines: ", value["total"])
	
	elif key == "track_blank_lines":
		print(f"  Total lines of Python-Code: {value['code']}")
		print(f"  Total blank lines in Python-Files: {value['blank_lines']}")
		print(f"  Total lines: {value['total']}")
	
	elif key == "track_comments":
		print(f"  Total lines of Python-Code: {value['code']}")
		print(f"  Total comments in Python-Files: {value['comments']}")
		print(f"  Total lines: {value['total']}")
		
	elif key == "track_both":
		print(f"  Total lines of Python-Code: {value['code']}")
		print(f"  Total blank lines in Python-Files: {value['blank_lines']}")
		print(f"  Total comments in Python-Files: {value['comments']}")
		print(f"  Total lines: {value['total']}")

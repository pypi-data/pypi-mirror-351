def return_all_files_in_folder(folder_path: str) -> list or str:
	"""
	Returns all Python-Files in a given folder that have been found recursively if folder_path is valid
	:param folder_path:
	:return: all_python_files:
	"""
	from os.path import isfile, isdir
	from glob import glob
	
	if isfile(folder_path):
		return [folder_path]
	if not isdir(folder_path):
		return f"{folder_path} is not a valid folder path or you lack permission to access the folder."
	return glob(folder_path + '/**/*.py', recursive=True)


def analyze_lines(file: list, track_comments: bool, track_blank_lines: bool) -> dict:
	"""
	Analyze lines in a file, optionally tracking comments and/or blank lines.

	:param file: List of lines from the file
	:param track_comments: Whether to detect and count comments separately
	:param track_blank_lines: Whether to detect and count blank lines separately
	:return: Dictionary with counts based on tracking flags
	"""
	code_lines = 0
	comment_lines = 0
	blank_lines = 0
	
	multiline_comment_flag = False
	
	if not track_comments and not track_blank_lines:
		return {"code": len(file)}
	
	for line in file:
		stripped = line.strip()
		is_comment = False
		is_blank = False
		
		if track_blank_lines and stripped == "":
			is_blank = True
		
		# Check for comments (if tracking)
		if track_comments:
			# Single line comment
			if stripped.startswith('#'):
				is_comment = True
				comment_lines += 1
			# Multiline comment start/end (TODO: Add ''' support)
			elif stripped.startswith('"""') or (multiline_comment_flag and stripped.endswith('"""')):
				is_comment = True
				comment_lines += 1
				multiline_comment_flag = not multiline_comment_flag
			# Inside multiline comment
			elif multiline_comment_flag:
				is_comment = True
				comment_lines += 1
		
		if is_blank and not is_comment:
			blank_lines += 1
		
		# Count as code if it's not a comment or blank (based on what we're tracking)
		if not is_comment and not is_blank:
			code_lines += 1
	
	# Return appropriate dictionary based on what was tracked
	result = {"code": code_lines}
	if track_comments:
		result["comments"] = comment_lines
	if track_blank_lines:
		result["blank_lines"] = blank_lines
	return result


def return_lines_of_code(filename: str, args) -> dict:
	"""
	Returns the line length of a given file. Does not track blank lines or comments.
	:param filename:
	:param args: arg parser arguments
	:return: file_length:
	"""
	track_blank_lines = args.track_blank_lines
	track_comments = args.track_comments
	
	try:
		with open(filename) as f:
			file = f.read().split('\n')
			if not track_blank_lines and not track_comments:
				return {"no_tracking": analyze_lines(file, False, False)}
			elif track_blank_lines and not track_comments:
				return {"track_blank_lines": analyze_lines(file, False, True)}
			elif not track_blank_lines and track_comments:
				return {"track_comments": analyze_lines(file, True, False)}
			elif track_blank_lines and track_comments:
				return {"track_both": analyze_lines(file, True, True)}
	
	except Exception as e:
		return {"error": e}


def return_sum_of_lines_in_folder(list_of_files, args):
	"""
	Returns the sum of all single lengths of code with proper error handling
	:param list_of_files: List of file paths to process
	:param args: arg parser arguments
	:return: Dictionary with totals and any errors encountered
	"""
	pbar = args.pbar
	track_blank_lines = args.track_blank_lines
	track_comments = args.track_comments
	
	# Initialize totals
	total_code = 0
	total_comments = 0
	total_blank_lines = 0
	total_lines = 0
	errors = []
	
	# Handle single file case
	if len(list_of_files) == 1:
		result = return_lines_of_code(list_of_files[0], args)
		if "error" in result:
			return {"error": result["error"]}
		
		dictionary = next(iter(result.values()))
		total = sum(dictionary.values())
		next(iter(result.values()))["total"] = total
		
		return result
	
	# Process multiple files
	from tqdm import tqdm
	iterator = tqdm(list_of_files) if pbar else list_of_files
	
	result = None
	
	for file_path in iterator:
		file_result = return_lines_of_code(file_path, args)
		
		# Handle errors
		if "error" in file_result:
			errors.append(f"Error in {file_path}: {file_result['error']}")
			continue
		
		if "no_tracking" in file_result:
			total_lines += file_result["no_tracking"]["code"]
		
		elif "track_blank_lines" in file_result:
			data = file_result["track_blank_lines"]
			total_code += data["code"]
			total_blank_lines += data["blank_lines"]
		
		elif "track_comments" in file_result:
			data = file_result["track_comments"]
			total_code += data["code"]
			total_comments += data["comments"]
		
		elif "track_both" in file_result:
			data = file_result["track_both"]
			total_code += data["code"]
			total_comments += data["comments"]
			total_blank_lines += data["blank_lines"]
	
	if not track_blank_lines and not track_comments:
		result = {"no_tracking": {"total": total_lines, "code": total_lines}}
	elif track_blank_lines and not track_comments:
		total = total_code + total_blank_lines
		result = {"track_blank_lines": {"total": total, "code": total_code, "blank_lines": total_blank_lines}}
	elif not track_blank_lines and track_comments:
		total = total_code + total_comments
		result = {"track_comments": {"total": total, "code": total_code, "comments": total_comments}}
	elif track_blank_lines and track_comments:
		total = total_code + total_comments + total_blank_lines
		result = {"track_both": {"total": total, "code": total_code, "comments": total_comments, "blank_lines": total_blank_lines}}
	
	if errors:
		result = {"errors": errors}
	
	# TODO: Find out what error this could be
	if result is None:
		print("Unknown error occurred")
		sys.exit(1)
	
	return result
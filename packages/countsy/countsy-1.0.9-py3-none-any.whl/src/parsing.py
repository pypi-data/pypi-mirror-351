import argparse

def init_binary_flag(parser, name, desc, action="store_true", default=False):
	parser.add_argument(
		f"--{name}",
		help=desc,
		action="store_true",
		default=False
	)


def init_parser():
	"""
	Initializes parser and returns the folder path
	:return: folder_path
	"""
	parser = argparse.ArgumentParser(description="Count total lines of Python code in a folder.")
	
	parser.add_argument(
		"folder_path",
		help="Path to the folder containing Python files",
		nargs='?',
		default="./"
	)
	
	init_binary_flag(parser, "pbar", "Includes progress bar")
	init_binary_flag(parser, "track-comments", "Tracks comments")
	init_binary_flag(parser, "track-blank-lines", "Tracks blank lines")
	init_binary_flag(parser, "track", "Tracks both comments and blank lines (eq. to 'countsy --track-blank-lines --track-comments) [overwrites both options]")
	
	args = parser.parse_args()
	
	if args.track:
		args.track_blank_lines = True
		args.track_comments = True
	
	return args
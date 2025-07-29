from unittest import TestCase
from argparse import Namespace


class Test(TestCase):
	def test_return_sum_of_lines_in_folder(self):
		from src.cli import return_sum_of_lines_in_folder, return_all_files_in_folder
		
		test_dir_path = 'test_dir/'
		test_dir = return_all_files_in_folder(test_dir_path)
		
		test_file_1 = test_dir_path + 'test_file_1.py'
		test_file_2 = test_dir_path + 'test_file_2.py'
		test_file_3 = test_dir_path + 'test_file_3.py'
		
		self.assertEqual(sorted(test_dir),
		                 ['test_dir/test_file_1.py', 'test_dir/test_file_2.py', 'test_dir/test_file_3.py'])
		
		def make_args(pbar=False, track_comments=False, track_blank_lines=False):
			return Namespace(
				pbar=pbar,
				track_comments=track_comments,
				track_blank_lines=track_blank_lines,
				track=False,
				folder_path=None
			)
		
		self.assertEqual(return_sum_of_lines_in_folder([test_file_1], make_args()), {'no_tracking': {'code': 31, 'total': 31}})
		self.assertEqual(return_sum_of_lines_in_folder([test_file_1], make_args(track_comments=True)), {'track_comments': {'code': 20, 'comments': 11, 'total': 31}})
		self.assertEqual(return_sum_of_lines_in_folder([test_file_1], make_args(track_blank_lines=True)), {'track_blank_lines': {'blank_lines': 12, 'code': 19, 'total': 31}})
		self.assertEqual(return_sum_of_lines_in_folder([test_file_1], make_args(track_comments=True, track_blank_lines=True)), {'track_both': {'blank_lines': 12, 'code': 8, 'comments': 11, 'total': 31}})
		
		self.assertEqual(return_sum_of_lines_in_folder([test_file_2], make_args()), {'no_tracking': {'code': 30, 'total': 30}})
		self.assertEqual(return_sum_of_lines_in_folder([test_file_2], make_args(track_comments=True)), {'track_comments': {'code': 25, 'comments': 5, 'total': 30}})
		self.assertEqual(return_sum_of_lines_in_folder([test_file_2], make_args(track_blank_lines=True)), {'track_blank_lines': {'blank_lines': 25, 'code': 5, 'total': 30}})
		self.assertEqual(return_sum_of_lines_in_folder([test_file_2], make_args(track_comments=True, track_blank_lines=True)), {'track_both': {'blank_lines': 25, 'code': 0, 'comments': 5, 'total': 30}})
		
		self.assertEqual(return_sum_of_lines_in_folder([test_file_3], make_args()), {'no_tracking': {'code': 9, 'total': 9}})
		self.assertEqual(return_sum_of_lines_in_folder([test_file_3], make_args(track_comments=True)), {'track_comments': {'code': 7, 'comments': 2, 'total': 9}})
		self.assertEqual(return_sum_of_lines_in_folder([test_file_3], make_args(track_blank_lines=True)), {'track_blank_lines': {'blank_lines': 1, 'code': 8, 'total': 9}})
		self.assertEqual(return_sum_of_lines_in_folder([test_file_3], make_args(track_comments=True, track_blank_lines=True)), {'track_both': {'blank_lines': 1, 'code': 6, 'comments': 2, 'total': 9}})
		
		self.assertEqual(return_sum_of_lines_in_folder(test_dir, make_args()), {'no_tracking': {'code': 70, 'total': 70}})
		self.assertEqual(return_sum_of_lines_in_folder(test_dir, make_args(track_comments=True)), {'track_comments': {'code': 52, 'comments': 18, 'total': 70}})
		self.assertEqual(return_sum_of_lines_in_folder(test_dir, make_args(track_blank_lines=True)), {'track_blank_lines': {'blank_lines': 38, 'code': 32, 'total': 70}})
		self.assertEqual(return_sum_of_lines_in_folder(test_dir, make_args(track_comments=True, track_blank_lines=True)), {'track_both': {'blank_lines': 38, 'code': 14, 'comments': 18, 'total': 70}})
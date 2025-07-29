import os
import tempfile
import unittest
from source_to_text_converter.source_to_text_converter import UnifiedSourceToTextConverter as CodebaseToText
from io import StringIO
import sys
from docx import Document
from unittest import mock
import git
from tests.base_test import BaseTest
import builtins

class TestCodebaseToText(BaseTest):
    def get_file_contents_section(self, content):
        file_contents_start = content.find("File Contents")
        return content[file_contents_start:]

    def setUp(self):
        # Create a temporary directory with some test files
        super().setUp()
        self.file1_path = os.path.join(self.test_dir.name, "file1.py")
        self.file2_path = os.path.join(self.test_dir.name, "file2.txt")
        self.hidden_file_path = os.path.join(self.test_dir.name, ".hiddenfile")
        with open(self.file1_path, "w") as f:
            f.write("print('Hello World')")
        with open(self.file2_path, "w") as f:
            f.write("This is a text file.")
        with open(self.hidden_file_path, "w") as f:
            f.write("Hidden content")

    def test_local_directory_txt_output(self):
        converter = CodebaseToText(
            input_path=self.test_dir.name,
            output_path=self.output_file.name,
            output_type="txt",
            verbose=False,
            exclude_hidden=False,
            include_exts=None
        )
        converter.get_file()
        with open(self.output_file.name, "r") as f:
            content = f.read()
        self.assertIn("file1.py", content)
        self.assertIn("file2.txt", content)
        self.assertIn("print('Hello World')", content)
        self.assertIn("This is a text file.", content)

    def test_exclude_hidden_files(self):
        converter = CodebaseToText(
            input_path=self.test_dir.name,
            output_path=self.output_file.name,
            output_type="txt",
            verbose=False,
            exclude_hidden=True
        )
        converter.get_file()
        with open(self.output_file.name, "r") as f:
            content = f.read()
        # Only check the File Contents section for hidden files exclusion
        file_contents = self.get_file_contents_section(content)
        self.assertNotIn(".hiddenfile", file_contents)
        self.assertNotIn("Hidden content", file_contents)

    def test_exclude_nested_hidden_folders(self):
        # Create nested hidden folders and files
        nested_hidden_dir = os.path.join(self.test_dir.name, ".hiddenfolder")
        os.makedirs(nested_hidden_dir)
        nested_hidden_file = os.path.join(nested_hidden_dir, "file_in_hidden.py")
        with open(nested_hidden_file, "w") as f:
            f.write("print('Inside hidden folder')")

        converter = CodebaseToText(
            input_path=self.test_dir.name,
            output_path=self.output_file.name,
            output_type="txt",
            verbose=False,
            exclude_hidden=True
        )
        converter.get_file()
        with open(self.output_file.name, "r") as f:
            content = f.read()
        file_contents = self.get_file_contents_section(content)
        self.assertNotIn(".hiddenfolder", file_contents)
        self.assertNotIn("file_in_hidden.py", file_contents)
        self.assertNotIn("Inside hidden folder", file_contents)

    def test_include_ext_filter(self):
        converter = CodebaseToText(
            input_path=self.test_dir.name,
            output_path=self.output_file.name,
            output_type="txt",
            verbose=False,
            exclude_hidden=False,
            include_exts=[".py"]
        )
        converter.get_file()
        with open(self.output_file.name, "r") as f:
            content = f.read()
        # Only check the File Contents section for extension filter
        file_contents = self.get_file_contents_section(content)
        self.assertIn("file1.py", file_contents)
        self.assertIn("print('Hello World')", file_contents)
        self.assertNotIn("file2.txt", file_contents)

    def test_invalid_output_type(self):
        converter = CodebaseToText(
            input_path=self.test_dir.name,
            output_path=self.output_file.name,
            output_type="invalid",
            verbose=False,
            exclude_hidden=False,
            include_exts=None
        )
        with self.assertRaises(ValueError):
            converter.get_file()

    def test_docx_output(self):
        converter = CodebaseToText(
            input_path=self.test_dir.name,
            output_path=self.output_file.name,
            output_type="docx",
            verbose=False,
            exclude_hidden=False,
            include_exts=None
        )
        converter.get_file()
        doc = Document(self.output_file.name)
        texts = [p.text for p in doc.paragraphs]
        self.assertIn("Folder Structure", texts)
        self.assertTrue(any("file1.py" in t for t in texts))
        self.assertTrue(any("print('Hello World')" in t for t in texts))

    def test_verbose_output(self):
        converter = CodebaseToText(
            input_path=self.test_dir.name,
            output_path=self.output_file.name,
            output_type="txt",
            verbose=True,
            exclude_hidden=False,
            include_exts=None
        )
        with self.assertLogs('source_to_text_converter.source_to_text_converter', level='DEBUG') as log:
            converter.get_file()
        self.assertTrue(any("Processing:" in message for message in log.output))

    def test_github_clone_scenarios(self):
        test_cases = [
            {"url": "https://github.com/user/repo.git", "expected_calls": "https://github.com/user/repo.git"},
            {"url": "https://username:token@github.com/user/private-repo.git", "expected_calls": "https://username:token@github.com/user/private-repo.git"}
        ]
        for case in test_cases:
            with self.subTest(url=case["url"]):
                import tempfile as real_tempfile
                temp_dir = real_tempfile.mkdtemp()
                with mock.patch('source_to_text_converter.source_to_text_converter.git.Repo') as mock_repo:
                    with mock.patch('source_to_text_converter.source_to_text_converter.tempfile.mkdtemp', return_value=temp_dir):
                        mock_repo_instance = mock_repo.return_value
                        mock_repo_instance.clone_from.return_value = None
                        converter = CodebaseToText(
                            input_path=case["url"],
                            output_path=self.output_file.name,
                            output_type="txt",
                            verbose=True,
                            exclude_hidden=False,
                            include_exts=None
                        )
                        with mock.patch.object(converter, '_parse_folder', return_value="folder structure"):
                            with mock.patch.object(converter, '_process_files', return_value="file contents"):
                                converter.get_file()
                        mock_repo_instance.clone_from.assert_called_once_with(case["expected_calls"], temp_dir)

    def test_file_read_error_handling(self):
        # Mock open to raise an exception when reading file1.py
        def open_side_effect(file_path, *args, **kwargs):
            if file_path == self.file1_path:
                raise IOError("Error reading file")
            return original_open(file_path, *args, **kwargs)

        original_open = builtins.open
        with mock.patch("builtins.open", side_effect=open_side_effect):
            with self.assertLogs('source_to_text_converter.source_to_text_converter', level='WARNING') as log:
                converter = CodebaseToText(
                    input_path=self.test_dir.name,
                    output_path=self.output_file.name,
                    output_type="txt",
                    verbose=False,
                    exclude_hidden=False,
                    include_exts=None
                )
                converter.get_file()
                self.assertTrue(any("Error reading file" in message for message in log.output))

    def test_file_permission_error_handling(self):
        # Mock open to raise a PermissionError when reading a specific file
        original_open = open

        def open_side_effect(file_path, *args, **kwargs):
            if "no_read_permission.py" in file_path:
                raise PermissionError("Permission denied")
            return original_open(file_path, *args, **kwargs)

        perm_file_path = os.path.join(self.test_dir.name, "no_read_permission.py")
        with open(perm_file_path, "w") as f:
            f.write("print('No read permission')")

        with mock.patch("builtins.open", side_effect=open_side_effect):
            with self.assertLogs('source_to_text_converter.source_to_text_converter', level='WARNING') as log:
                converter = CodebaseToText(
                    input_path=self.test_dir.name,
                    output_path=self.output_file.name,
                    output_type="txt",
                    verbose=False,
                    exclude_hidden=False,
                    include_exts=None
                )
                converter.get_file()
                self.assertTrue(any("warning" in message.lower() for message in log.output))

    def test_corrupted_file_handling(self):
        # Create a file with invalid utf-8 bytes
        corrupted_file_path = os.path.join(self.test_dir.name, "corrupted_file.py")
        with open(corrupted_file_path, "wb") as f:
            f.write(b'\xff\xfe\xfa\xfb')

        with self.assertLogs('source_to_text_converter.source_to_text_converter', level='WARNING') as log:
            converter = CodebaseToText(
                input_path=self.test_dir.name,
                output_path=self.output_file.name,
                output_type="txt",
                verbose=False,
                exclude_hidden=False,
                include_exts=None
            )
            converter.get_file()
            self.assertTrue(any("Could not decode file" in message for message in log.output))

if __name__ == "__main__":
    unittest.main()

if __name__ == "__main__":
    unittest.main()

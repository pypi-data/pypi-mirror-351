import os
import tempfile
import unittest
from source_to_text_converter.source_to_text_converter import UnifiedSourceToTextConverter as CodebaseToText
import time
import shutil
from tests.base_test import BaseTest
from unittest import mock

class TestIntegrationPerformance(BaseTest):
    def test_large_number_of_files(self):
        # Create a large number of small files
        num_files = 1000
        for i in range(num_files):
            file_path = os.path.join(self.test_dir.name, f"file_{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"This is file number {i}")

        converter = CodebaseToText(
            input_path=self.test_dir.name,
            output_path=self.output_file.name,
            output_type="txt",
            verbose=False,
            exclude_hidden=False,
            include_exts=None
        )
        start_time = time.time()
        converter.get_file()
        duration = time.time() - start_time
        self.assertTrue(duration < 10, f"Processing took too long: {duration} seconds")

    def test_large_file_processing(self):
        # Create a very large file (~10MB)
        large_file_path = os.path.join(self.test_dir.name, "large_file.py")
        with open(large_file_path, "w") as f:
            f.write("print('Line')\n" * 500000)  # 500,000 lines

        converter = CodebaseToText(
            input_path=self.test_dir.name,
            output_path=self.output_file.name,
            output_type="txt",
            verbose=False,
            exclude_hidden=False,
            include_exts=None
        )
        start_time = time.time()
        converter.get_file()
        duration = time.time() - start_time
        self.assertTrue(duration < 20, f"Processing large file took too long: {duration} seconds")

    def test_deeply_nested_directories(self):
        # Create deeply nested directories
        base_path = self.test_dir.name
        depth = 20
        for i in range(depth):
            base_path = os.path.join(base_path, f"nested_{i}")
            os.makedirs(base_path)
            # Add a file at each level
            file_path = os.path.join(base_path, f"file_{i}.py")
            with open(file_path, "w") as f:
                f.write(f"print('File at depth {i}')")

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
        # Check for files at deepest level
        self.assertIn("nested_19", content)
        self.assertIn("file_19.py", content)
        self.assertIn("print('File at depth 19')", content)

    @mock.patch('source_to_text_converter.source_to_text_converter.git.Repo.clone_from')
    def test_github_repo_integration(self, mock_clone):
        import shutil
        import tempfile
        import os

        def fake_clone_from(url, to_path, branch=None):
            # Copy a local test repo folder to to_path to simulate cloning
            local_repo_path = os.path.join(os.path.dirname(__file__), "testdata", "Hello-World")
            if os.path.exists(to_path):
                shutil.rmtree(to_path)
            shutil.copytree(local_repo_path, to_path)

        mock_clone.side_effect = fake_clone_from

        # Use a small public GitHub repo for testing
        github_url = "https://github.com/octocat/Hello-World.git"
        converter = CodebaseToText(
            input_path=github_url,
            output_path=self.output_file.name,
            output_type="txt",
            verbose=True,
            exclude_hidden=True,
            include_exts=None
        )
        converter.get_file()

        with open(self.output_file.name, "r") as f:
            content = f.read()
        # Check for known file or folder names in the repo
        self.assertIn("README", content)
        # Assert that .git related content is excluded
        self.assertNotIn(".git/config", content)
        self.assertNotIn(".git/HEAD", content)
        self.assertNotIn(".gitignore", content)
        # Check for content of a known file
        self.assertIn("Hello World!", content)

if __name__ == "__main__":
    unittest.main()

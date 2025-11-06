import unittest
from src.processor import process_image

class TestProcessor(unittest.TestCase):

    def test_process_image(self):
        # Test with a sample bingo card image
        result = process_image("tests/sample_bingo_card.png")
        expected_result = [
            ['1', '2', '3', '4', '5'],
            ['6', '7', '8', '9', '10'],
            ['11', '12', '13', '14', '15'],
            ['16', '17', '18', '19', '20'],
            ['21', '22', '23', '24', '25']
        ]
        self.assertEqual(result, expected_result)

    def test_empty_image(self):
        # Test with an empty image
        result = process_image("tests/empty_image.png")
        expected_result = [['', '', '', '', ''],
                           ['', '', '', '', ''],
                           ['', '', '', '', ''],
                           ['', '', '', '', ''],
                           ['', '', '', '', '']]
        self.assertEqual(result, expected_result)

    def test_invalid_image(self):
        # Test with an invalid image path
        with self.assertRaises(FileNotFoundError):
            process_image("tests/non_existent_image.png")

if __name__ == '__main__':
    unittest.main()
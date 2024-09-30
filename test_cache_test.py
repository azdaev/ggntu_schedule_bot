import unittest
from unittest.mock import patch
import datetime
import cache

class TestSecondsUntilNextMonday(unittest.TestCase):
    @patch('datetime.datetime')
    @patch('datetime.date')
    def test_seconds_until_next_monday(self, mock_date, mock_datetime):
        # Arrange
        monday_morning = datetime.datetime(2024, 3, 25, 3, 0, 0)
        end_of_today = monday_morning.replace(hour=23, minute=59, second=59)
        expected_result = int((end_of_today - monday_morning).total_seconds()) + 6 * 24 * 60 * 60

        mock_datetime.now.return_value = monday_morning
        mock_date.today.return_value = datetime.date(2024, 3, 25)

        # Act
        actual_result = cache.seconds_until_next_monday()

        # Assert
        self.assertEqual(expected_result, actual_result)

if __name__ == '__main__':
    unittest.main()
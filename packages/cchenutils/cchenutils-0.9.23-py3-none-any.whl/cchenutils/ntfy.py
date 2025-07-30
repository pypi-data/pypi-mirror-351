import os
import time

import pandas as pd
from schedule import every, repeat, run_pending

from .files import count_lines
from .session import Session


def notify(topic, title, content, priority=3, tags=None):
    """
    Send a notification via ntfy.sh.

    Args:
        topic (str): The ntfy topic to send the notification to.
        title (str): The title of the notification.
        content (str): The body/content of the notification.
        priority (int, optional): Priority level (1–5). Default is 3.
                                  Level 5 automatically adds a 'warning' tag if no tags are provided.
        tags (str, optional): Comma-separated tags for the notification (e.g., 'warning,mailsrv13,daily-backup').
                              See available tags and emojis at: https://docs.ntfy.sh/publish/#tags-emojis

    Returns:
        bool: True if the request was sent successfully, False if an exception occurred.
    """

    try:
        with Session(timeout=10) as sess:
            url = f'https://ntfy.sh/{topic}'
            data = content
            headers = {'Title': f'{title}',
                       'Priority': f'{priority}'}
            if tags is not None:
                headers |= {'Tags': tags}
            elif priority == 5:
                headers |= {'Tags': 'warning'}
            sess.post(url, data=data, headers=headers)
        return True
    except:
        return False


class DailyFileWatcher:
    """
    Monitors one or more files for line growth. Sends a push notification
    if a file stops growing or at the end of the day with a summary.

    Attributes:
        file_paths (list[str]): List of file paths to watch.
        check_time (str): Time string (e.g., ':50') for when checks are performed (schedule syntax).
        report_hour (int): Hour (0–23) to send the daily report.
        report_server (str): Notification topic for sending the report.
        history (dict): Internal tracking of last line counts per file.

    Example:
        watcher = DailyFileWatcher(
            '/path/to/file1.csv', '/path/to/file2.csv',
            report_server='your_topic',
            check_time=':50', report_hour=23
        )
        watcher.schedule()
    """

    def __init__(self, *fps, server='cchendailycheckin', check_time=':50', report_hour=23):
        """
        Initialize the DailyFileWatcher.

        Args:
            *fps: Variable number of file paths to be monitored.
            server (str): Notification topic for sending alerts/reports.
            check_time (str): Schedule time string (e.g., ':50') for when checks occur.
            report_hour (int): Hour (0–23) to send the daily report.
        """
        if not fps:
            raise ValueError("At least one file path must be provided.")
        self.file_paths = fps
        self.server = server
        self.check_time = check_time
        self.report_hour = report_hour
        self.history = {}

    def check_growth(self, fp):
        """Check line growth for a single file and send alert if no growth."""
        this_count = count_lines(fp)
        last_count = self.history.get(fp, -1)
        if this_count <= last_count:
            notify(self.server,
                   f'{os.path.basename(fp)} interrupted!',
                   f'{pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")}')
        self.history[fp] = this_count

    def check_all(self):
        """Check growth of all watched files and send a daily report at the configured hour."""
        now = pd.Timestamp.now()
        for fp in self.file_paths:
            self.check_growth(fp)
        if now.hour == self.report_hour:
            notify(self.server,
                   f'{now.strftime("%Y-%m-%d")} Report',
                   '\n'.join(f'{os.path.basename(fp)}: {count}' for fp, count in self.history.items()))

    def run(self):
        """Schedule periodic file checks and start monitoring."""

        @repeat(every().hours.at(self.check_time))
        def _():
            self.check_all()

        while True:
            run_pending()
            time.sleep(10)

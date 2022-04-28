import pytest

from shop_site import tasks
from unittest.mock import patch


#
@pytest.mark.skip
@patch("shop_site.tasks.send_email_task.run")
def test_task(mock_run):
    assert tasks.send_email_task.run(1)
    assert tasks.send_email_task.run(2)
    assert tasks.send_email_task.run(3)

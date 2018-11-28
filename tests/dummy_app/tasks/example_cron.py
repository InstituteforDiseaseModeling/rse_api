from rse_api.decorators import cron
from tests.dummy_app.tasks import example_worker


@cron('*/1 * * * *')
def get_new_message():
    example_worker.send('yay')
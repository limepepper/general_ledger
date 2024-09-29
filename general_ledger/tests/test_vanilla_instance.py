import logging

from django.apps import apps

from general_ledger.tests import GeneralLedgerBaseTest


# this is to test that vanilla instances can be created
# without an error
class TestVanillaInstances(GeneralLedgerBaseTest):

    logger = logging.getLogger(__name__)

    def test_stuff1(self):
        """
        test vanilla instances can be created
        """
        app_models = apps.get_app_config("general_ledger").get_models()
        for model in app_models:
            self.logger.debug(f"Model: {model}")
            o = model()

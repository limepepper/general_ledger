from django.test.runner import DiscoverRunner


class PersistentTestRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        return super().setup_databases(**kwargs)
        return None

    def teardown_databases(self, old_config, **kwargs):
        # Override to prevent database destruction
        pass

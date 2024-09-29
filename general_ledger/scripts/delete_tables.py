from django.apps import apps


def main():

    models = apps.all_models["general_ledger"]


if __name__ == "__main__":
    main()

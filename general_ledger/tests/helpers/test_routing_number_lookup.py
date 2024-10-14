import pytest
from rich import inspect

from general_ledger.helpers.routing_number_lookup import create_sort_code_trie
from general_ledger.helpers.sort_code_lookup import sort_codes


class TestRoutingNumberLookup:

    trie = create_sort_code_trie(sort_codes)

    def test_simple_routing_number_lookup(self):

        routing_number = "123456789"
        bank_name = "Bank Name"

        # assert bank_name == routing_number_lookup.lookup(routing_number)

        #inspect(trie)
        # print(trie.display_tree())

        assert self.trie.lookup("60-24-77") == "NatWest Bank"
        assert self.trie.lookup("20-48-95") == "Barclays Bank"
        assert self.trie.lookup("99-99-99") is None
        assert self.trie.lookup("02-00-00") is None
        print(self.trie.lookup("938616"))
        print(self.trie.lookup("938654"))
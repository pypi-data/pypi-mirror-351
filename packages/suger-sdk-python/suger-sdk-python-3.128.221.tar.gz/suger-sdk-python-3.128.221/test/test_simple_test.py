import unittest

from suger_sdk_python.api.api_api import ApiClient
from suger_sdk_python.api.offer_api import OfferApi
from suger_sdk_python.api.product_api import ProductApi
from suger_sdk_python.exceptions import ApiException
from suger_sdk_python.configuration import Configuration
from suger_sdk_python.api.entitlement_api import EntitlementApi


class TestSimpleTest(unittest.TestCase):

    def setUp(self) -> None:
        test_config = Configuration(
            host="https://api.dev.suger.cloud",
        )
        test_config.api_key[
            'APIKeyAuth'] = 'Key 95d2983ca68bd6f9655b9d026b05e9afbdb6a601a700c18007f9eb3accec7a067b306e8233278dd36f88d028c6007053cfe3fc7a585ed2aef4f3cf14b99482ca'
        api_client = ApiClient(test_config)
        self.api = api_client

    def test_get_offer(self) -> None:
        org_id = 'w43Vc6UfM'
        offer_id = '1Edc6L49p'
        try:
            result = OfferApi(self.api).get_offer(org_id, offer_id)
            print("The response of OfferApi:\n")
            print(result)
            self.assertEqual(result.id, offer_id)
            pass
        except ApiException as e:
            print("Exception when calling OfferApi->get_offer: %s\n" % e)
            assert False

    def test_get_product(self) -> None:
        org_id = 'w43Vc6UfM'
        product_id = 'uD4BR9VfM'
        try:
            result = ProductApi(self.api).get_product(org_id, product_id)
            print("The response of ProductApi:\n")
            print(result)
            self.assertEqual(result.id, product_id)
            pass
        except ApiException as e:
            print("Exception when calling ProductApi->get_product: %s\n" % e)
            assert False

    def test_get_entitlement(self) -> None:
        org_id = 'w43Vc6UfM'
        entitlement_id = '7DuaETO_S'
        try:
            result = EntitlementApi(self.api).get_entitlement(org_id, entitlement_id)
            print("The response of EntitlementApi:\n")
            print(result)
            self.assertEqual(result.id, entitlement_id)
            pass
        except ApiException as e:
            print("Exception when calling EntitlementApi->get_entitlement: %s\n" % e)
            assert False


if __name__ == '__main__':
    unittest.main()

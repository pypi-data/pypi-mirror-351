# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from iosanita.policy.testing import RESTAPI_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from transaction import commit

import unittest


class TestStrutturaSchema(unittest.TestCase):
    layer = RESTAPI_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.news = api.content.create(
            container=self.portal,
            type="News Item",
            title="Test news",
            parliamo_di=["Alimentazione", "Donazione organi e sangue"],
            a_chi_si_rivolge_tassonomia=["bambini"],
        )
        self.event = api.content.create(
            container=self.portal,
            type="Event",
            title="Test Event",
            parliamo_di=["Alimentazione"],
            a_chi_si_rivolge_tassonomia=["foo"],
        )

        commit()

    def tearDown(self):
        self.api_session.close()

    def test_endpoint_reply_bad_request_if_missing_parameter(self):
        res = self.api_session.get("@search-tassonomie")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["message"], "Missing parameter: type")

    def test_passing_type_reply_all_results(self):
        res = self.api_session.get("@search-tassonomie?type=parliamo_di").json()

        self.assertEqual(res["items_total"], 2)
        self.assertEqual(res["items"][0]["title"], self.news.title)
        self.assertEqual(res["items"][1]["title"], self.event.title)

    def test_passing_sort_order_reply_sorted_results(self):
        res = self.api_session.get(
            "@search-tassonomie?type=parliamo_di&sort_on=sortable_title"
        ).json()

        self.assertEqual(res["items_total"], 2)
        self.assertEqual(res["items"][0]["title"], self.event.title)
        self.assertEqual(res["items"][1]["title"], self.news.title)

        res = self.api_session.get(
            "@search-tassonomie?type=parliamo_di&sort_on=sortable_title&sort_order=descending"
        ).json()

        self.assertEqual(res["items_total"], 2)
        self.assertEqual(res["items"][0]["title"], self.news.title)
        self.assertEqual(res["items"][1]["title"], self.event.title)

    def test_passing_type_and_value_reply_filtered_results(self):
        res = self.api_session.get(
            "@search-tassonomie?type=parliamo_di&value=Alimentazione"
        ).json()

        self.assertEqual(res["items_total"], 2)
        self.assertEqual(res["items"][0]["title"], self.news.title)
        self.assertEqual(res["items"][1]["title"], self.event.title)

        res = self.api_session.get(
            "@search-tassonomie?type=parliamo_di&value=Donazione organi e sangue"
        ).json()

        self.assertEqual(res["items_total"], 1)
        self.assertEqual(res["items"][0]["title"], self.news.title)

    def test_passing_not_accepted_index_reply_bad_request(self):
        res = self.api_session.get("@search-tassonomie?type=xxx")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["message"], "Unkwnown taxonomy: xxx")

    def test_if_content_has_wrong_value_it_has_not_been_indexed(self):
        res = self.api_session.get(
            "@search-tassonomie?type=a_chi_si_rivolge_tassonomia&value=foo"
        ).json()
        self.assertEqual(res["items_total"], 0)

        res = self.api_session.get(
            "@search-tassonomie?type=a_chi_si_rivolge_tassonomia&value=bambini"
        ).json()
        self.assertEqual(res["items_total"], 1)

    def test_endpoint_reply_facets_for_all_portal_types_with_at_least_one_reference(
        self,
    ):
        res = self.api_session.get(
            "@search-tassonomie?type=parliamo_di&value=Alimentazione"
        ).json()

        self.assertEqual(len(res["facets"]["portal_types"]), 2)
        self.assertEqual(res["facets"]["portal_types"][0]["token"], "Event")
        self.assertEqual(res["facets"]["portal_types"][1]["token"], "News Item")

        res = self.api_session.get(
            "@search-tassonomie?type=parliamo_di&value=Alimentazione"
        ).json()
        self.assertEqual(len(res["facets"]["portal_types"]), 2)
        self.assertEqual(res["facets"]["portal_types"][0]["token"], "Event")
        self.assertEqual(res["facets"]["portal_types"][1]["token"], "News Item")

        res = self.api_session.get(
            "@search-tassonomie?type=parliamo_di&value=xxx"
        ).json()
        self.assertEqual(len(res["facets"]["portal_types"]), 0)

# -*- coding: utf-8 -*-
from collective.taxonomy import PATH_SEPARATOR
from collective.taxonomy.interfaces import ITaxonomy
from iosanita.policy import _
from plone import api
from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


ALLOWED_TAXONOMIES = ["parliamo_di", "a_chi_si_rivolge_tassonomia"]

BASE_FILTERS = [
    "portal_type",
    "sort_on",
    "sort_order",
    "fullobjects",
    "b_start",
    "b_size",
]


class SearchTassonomieGet(Service):
    def reply(self):
        index = self.request.form.get("type", "")
        value = self.request.form.get("value", "")

        if not index:
            raise BadRequest(
                api.portal.translate(
                    _("missing_parameter_type_error", default="Missing parameter: type")
                )
            )
        if index not in ALLOWED_TAXONOMIES:
            raise BadRequest(
                api.portal.translate(
                    _(
                        "unknown_index_error",
                        default="Unkwnown taxonomy: ${index}",
                        mapping={"index": index},
                    )
                )
            )
        pc = api.portal.get_tool(name="portal_catalog")
        query = {}

        # add standard query filters
        for query_index in BASE_FILTERS:
            value_index = self.request.form.get(query_index, "")
            if value_index:
                query[query_index] = value_index

        # then filter by taxonomy
        all_values = pc.uniqueValuesFor(index)

        if value:
            query[index] = value
        else:
            # return all
            query[index] = all_values

        # and do search
        brains = api.content.find(**query)
        batch = HypermediaBatch(self.request, brains)
        results = {}
        results["@id"] = batch.canonical_url
        results["items_total"] = batch.items_total
        links = batch.links
        if links:
            results["batching"] = links

        results["items"] = []
        for brain in batch:
            result = getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()
            if result:
                results["items"].append(result)

        # add facets
        results["facets"] = self.get_facets(query={index: query[index]})
        results["infos"] = self.get_infos(index=index, value=value)
        return results

    def get_facets(self, query):
        """
        return search facets
        """
        portal_types = []
        for brain in api.content.find(**query):
            if brain.portal_type not in portal_types:
                portal_types.append(brain.portal_type)

        facets = {}

        factory = getUtility(
            IVocabularyFactory, "plone.app.vocabularies.ReallyUserFriendlyTypes"
        )
        vocabulary = factory(api.portal.get())
        portal_types_dict = []
        for ptype in portal_types:
            try:
                title = vocabulary.getTerm(ptype).title
            except LookupError:
                title = ptype
            portal_types_dict.append({"title": title, "token": ptype})
        facets["portal_types"] = sorted(portal_types_dict, key=lambda x: x["title"])
        return facets

    def get_infos(self, index, value):
        taxonomy = getUtility(ITaxonomy, name=f"collective.taxonomy.{index}")
        taxonomy_voc = taxonomy.makeVocabulary(self.request.get("LANGUAGE"))

        data = []
        if not isinstance(value, list):
            value = [value]
        for key in value:
            taxonomy_value = taxonomy_voc.inv_data.get(key, None)
            if not taxonomy_value:
                continue
            if taxonomy_value.startswith(PATH_SEPARATOR):
                taxonomy_value = taxonomy_value.replace(PATH_SEPARATOR, "", 1)

            data.append(
                {"title": taxonomy_value.split(PATH_SEPARATOR)[-1], "token": key}
            )
        return data

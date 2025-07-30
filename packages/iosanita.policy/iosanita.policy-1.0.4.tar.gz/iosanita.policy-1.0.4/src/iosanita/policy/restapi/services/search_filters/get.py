# -*- coding: utf-8 -*-
from AccessControl.unauthorized import Unauthorized
from collective.taxonomy import PATH_SEPARATOR
from collective.taxonomy.interfaces import ITaxonomy
from iosanita.policy.interfaces import IIoSanitaSettings
from plone import api
from plone.registry.interfaces import IRegistry
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from Products.CMFPlone.interfaces import ISearchSchema
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.i18n import translate

import json


class SearchFiltersGET(Service):
    def reply(self):
        return {
            "quick_search": self.get_data_from_registry(field_id="quick_search"),
            "sections": self.get_sections(),
            "portal_types": self.get_portal_types(),
            "a_chi_si_rivolge_tassonomia": self.get_taxonomy_data(
                name="a_chi_si_rivolge_tassonomia"
            ),
            "parliamo_di": self.get_taxonomy_data(name="parliamo_di"),
        }

    def get_data_from_registry(self, field_id):
        try:
            values = api.portal.get_registry_record(
                field_id, interface=IIoSanitaSettings, default="[]"
            )
        except KeyError:
            return []
        return json.loads(values or "[]")

    def get_sections(self):
        utils = api.portal.get_tool(name="plone_utils")

        sections = []
        for setting in self.get_data_from_registry(field_id="search_sections"):
            items = []
            for section_settings in setting.get("items") or []:
                expand = section_settings.get("expand", False)
                for link_item in section_settings.get("linkUrl") or []:
                    uid = ""
                    if isinstance(link_item, str):
                        uid = link_item
                    else:
                        uid = link_item.get("UID", "")
                    if not uid:
                        continue
                    try:
                        section = api.content.get(UID=uid)
                    except Unauthorized:
                        # private folder
                        continue
                    if not section:
                        continue
                    item_infos = getMultiAdapter(
                        (section, self.request),
                        ISerializeToJsonSummary,
                    )()
                    if expand:
                        children = section.listFolderContents(
                            contentFilter={"portal_type": utils.getUserFriendlyTypes()}
                        )
                        item_infos["items"] = [
                            getMultiAdapter(
                                (x, self.request),
                                ISerializeToJsonSummary,
                            )()
                            for x in children
                        ]
                    else:
                        # do not expand childrens, the only item is the section/container itself
                        item_infos["items"] = [
                            getMultiAdapter(
                                (section, self.request),
                                ISerializeToJsonSummary,
                            )()
                        ]
                    item_infos["title"] = section_settings.get("title", "")
                    items.append(item_infos)
            if items:
                sections.append(
                    {
                        "rootPath": setting.get("rootPath", ""),
                        "items": items,
                    }
                )
        return sections

    def get_portal_types(self):
        ttool = api.portal.get_tool("portal_types")
        ptool = api.portal.get_tool("plone_utils")
        registry = getUtility(IRegistry)
        search_settings = registry.forInterface(ISearchSchema, prefix="plone")
        types_not_searched = search_settings.types_not_searched
        types = [
            {
                "label": translate(ttool[t].Title(), context=self.request),
                "value": t,
            }
            for t in ptool.getUserFriendlyTypes()
            if t not in types_not_searched
        ]
        return sorted(types, key=lambda k: k["label"])

    def get_taxonomy_data(self, name):
        taxonomy = getUtility(ITaxonomy, name=f"collective.taxonomy.{name}")
        taxonomy_voc = taxonomy.makeVocabulary(self.request.get("LANGUAGE"))
        data = []
        for label, value in taxonomy_voc.iterEntries():
            if label.startswith(PATH_SEPARATOR):
                label = label.replace(PATH_SEPARATOR, "", 1)

                data.append({"label": label.split(PATH_SEPARATOR)[-1], "value": value})
        return data

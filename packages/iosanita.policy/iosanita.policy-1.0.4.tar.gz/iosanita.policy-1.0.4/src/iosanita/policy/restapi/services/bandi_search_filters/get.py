# -*- coding: utf-8 -*-
from plone import api
from plone.base.interfaces.siteroot import IPloneSiteRoot
from plone.restapi.services import Service
from redturtle.bandi.vocabularies import TipologiaBandoVocabularyFactory
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class BandiSearchFiltersGet(Service):
    def reply(self):
        """
        Return possible values based also on current user permissions
        """
        pc = api.portal.get_tool(name="portal_catalog")
        voc_tipologie = TipologiaBandoVocabularyFactory(self.context)

        tipologie = []
        subjects = []

        if IPloneSiteRoot.providedBy(self.context):
            for subject in pc.uniqueValuesFor("Subject_bando"):
                res = api.content.find(Subject_bando=subject)
                if res:
                    subjects.append({"UID": subject, "title": subject})

            for item in voc_tipologie.by_token:
                tipologie.append(
                    {"UID": item, "title": voc_tipologie.getTerm(item).title}
                )

        else:
            brains = api.content.find(context=self.context, portal_type="Bando")

            for brain in brains:
                bando = brain.getObject()
                if not bando.tipologia_bando:
                    continue
                found = [x for x in tipologie if x["UID"] == bando.tipologia_bando]
                if not found:
                    tipologie.append(
                        {
                            "UID": bando.tipologia_bando,
                            "title": voc_tipologie.getTerm(bando.tipologia_bando).title,
                        }
                    )
                for sub in bando.subject:
                    found = [x for x in subjects if x["UID"] == sub]
                    if not found:
                        subjects.append({"UID": sub, "title": sub})

        subjects.sort(key=lambda x: x["title"])
        tipologie.sort(key=lambda x: x["title"])
        return {"subjects": subjects, "tipologie": tipologie}

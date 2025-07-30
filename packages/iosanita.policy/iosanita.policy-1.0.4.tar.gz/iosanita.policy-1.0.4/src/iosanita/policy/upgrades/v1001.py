from . import logger
from collective.volto.blocksfield.field import BlocksField
from plone import api
from plone.dexterity.utils import iterSchemata
from uuid import uuid4
from zope.schema import getFields


def upgrade(setup_tool=None):
    """ """
    brains = api.content.find(block_types="accordion")
    tot = len(brains)
    i = 0
    for brain in brains:
        i += 1
        obj = brain.getObject()
        logger.info("Upgrading accordion %s of %s: %s" % (i, tot, obj.absolute_url()))

        blocks = getattr(obj, "blocks", {})
        if blocks:
            for uid, block in blocks.items():
                new_accordion_block = fix_accordion(block=block)
                if new_accordion_block:
                    blocks[uid] = new_accordion_block
            obj.blocks = blocks
        for schema in iterSchemata(obj):
            for name, field in getFields(schema).items():
                if not isinstance(field, BlocksField):
                    continue
                value = field.get(obj)
                if not value:
                    continue
                blocks = value.get("blocks", {})
                for uid, block in blocks.items():
                    new_accordion_block = fix_accordion(block=block)
                    if new_accordion_block:
                        blocks[uid] = new_accordion_block
                setattr(obj, name, value)


def fix_accordion(block):
    if block.get("@type", "") != "accordion":
        return None
    if "subblocks" not in block:
        # already new version
        return None
    new_block = {
        "@type": "accordion",
        "title": block.get("title", ""),
        "description": block.get("description", ""),
        "collapsed": True,
        "non_exclusive": False,
        "show_block_bg": True,
        "data": {"blocks": {}, "blocks_layout": {"items": []}},
    }
    for subblock in block["subblocks"]:
        accordion_uid = str(uuid4())
        accordion_block = {
            "blocks": {},
            "blocks_layout": {"items": []},
            "title": subblock.get("title", ""),
            "@type": "accordionPanel",
        }
        for text_block in subblock.get("text", []):
            text_uid = str(uuid4())
            accordion_block["blocks"][text_uid] = {
                "@type": "slate",
                "value": [text_block],
            }
            accordion_block["blocks_layout"]["items"].append(text_uid)
        new_block["data"]["blocks"][accordion_uid] = accordion_block
        new_block["data"]["blocks_layout"]["items"].append(accordion_uid)
    return new_block

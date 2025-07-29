# -*- coding: utf-8 -*-

from collective.exportimport.import_content import ImportContent
from enum import Enum
from plone import api
from zope.component.hooks import getSite

import json
import os


class ExistingContent(Enum):
    SKIP = 0
    REPLACE = 1
    UPDATE = 2
    IGNORE = 3


def get_configs():
    """Return the configs defined in `URBAN_SCHEDULE_CONFIGS` env variable"""
    configs = os.environ.get("URBAN_SCHEDULE_CONFIGS", "default,standard")
    return configs.split(",")


def remove_uid(data):
    new_data = []

    for item in data:
        if "UID" in item:
            del item["UID"]
        if "UID" in item["parent"]:
            del item["parent"]["UID"]
        new_data.append(item)

    return new_data


def remove_none(data):
    return [{k: v for k, v in item.items() if v is not None} for item in data]


def fix_id(id):
    path = id.split("portal_urban")[1]
    root_site = getSite()
    return os.path.normpath(
        os.path.join(
            "/".join(root_site.getPhysicalPath()), "portal_urban", path.lstrip("/")
        )
    )


def fix_all_ids(data):
    new_data = []

    for item in data:
        item["@id"] = fix_id(item["@id"])
        item["parent"]["@id"] = fix_id(item["parent"]["@id"])
        new_data.append(item)

    return new_data


def handle_update_keys(data, handle_existing_content, update_keys=None):
    if handle_existing_content is not ExistingContent.UPDATE:
        return data
    if update_keys is None:
        return data
    default_keep_keys = ["@id", "@type", "parent", "@relative_path", "UID", "id"]
    all_keep_keys = default_keep_keys + update_keys
    output_data = []
    for item in data:
        output_item = {}
        for key in all_keep_keys:
            if key not in item:
                continue
            output_item[key] = item[key]
        output_data.append(output_item)
    return output_data


def import_json_config(
    json_path, context, handle_existing_content=ExistingContent.SKIP, update_keys=None
):
    """
    This function is used to import a json file (exported with c.exportimport)

    :param json_path: Path to the json to be imported
    :type json_path: String
    :param context: Path to or object of the context where the json will be imported
    :type context: String or plone object
    :param handle_existing_content: Value dictate what to do if content already exist
    :type handle_existing_content: urban.schedule.utils.ExistingContent
    :param update_keys: List of key to update if ExistingContent.UPDATE is selected to handle_existing_content
    :type update_keys: List of string
    :raises ValueError: Raise if the json doesn't exist
    """
    if not os.path.isfile(json_path):
        raise ValueError("{} does not exist".format(json_path))

    with open(json_path, "r") as f:
        data = json.load(f)

    portal = api.portal.get()

    if isinstance(context, str):
        context = portal.restrictedTraverse(context)

    request = getattr(context, "REQUEST", None)

    if request is None:
        request = portal.REQUEST

    import_content = ImportContent(context, request)

    import_content.import_to_current_folder = False
    import_content.handle_existing_content = handle_existing_content.value
    import_content.limit = None
    import_content.commit = None
    import_content.import_old_revisions = False

    data = remove_uid(data)
    data = remove_none(data)
    data = fix_all_ids(data)
    data = handle_update_keys(data, handle_existing_content, update_keys)

    import_content.start()
    import_content.do_import(data)
    import_content.finish()


def import_all_config(
    base_json_path="./profiles/config",
    base_context_path="portal_urban",
    config_type="schedule",
    handle_existing_content=ExistingContent.SKIP,
    match_filename=None,
    update_keys=None,
):
    """
    Function used to import all json inside a folder

    :param base_json_path: Root folder whre to find json, defaults to "./profiles/config"
    :type base_json_path: String, optional
    :param base_context_path: Path to or object of the context where the json will be
                              imported, defaults to "portal_urban"
    :type base_context_path: String or plone object, optional
    :param config_type: config folder where to import, defaults to "schedule"
    :type config_type: String, optional
    :param handle_existing_content: Value dictate what to do if content already exist
    :type handle_existing_content: urban.schedule.utils.ExistingContent
    :param match_filename: a filename that will be use to restrict the imported configs,
                           defaults to "None"
    :type match_filename: String, optional
    :param update_keys: List of key to update if ExistingContent.UPDATE is selected to handle_existing_content
    :type update_keys: List of string
    :raises ValueError: Raise if the json doesn't exist
    """
    directory_path = os.path.dirname(os.path.realpath(__file__))

    licences_types = os.walk(
        os.path.normpath(os.path.join(directory_path, base_json_path))
    )

    root_site = getSite()

    for root, dirs, files in licences_types:
        if files == []:
            continue
        for file in files:
            if match_filename is not None and file != match_filename:
                continue
            if not file.endswith(".json"):
                continue
            json_path = os.path.join(root, file)
            licence_type = root.split("/")[-1]
            context_plone = os.path.normpath(
                os.path.join(
                    "/".join(root_site.getPhysicalPath()),
                    base_context_path,
                    licence_type,
                    config_type,
                )
            )
            import_json_config(
                json_path=json_path,
                context=context_plone,
                handle_existing_content=handle_existing_content,
                update_keys=update_keys,
            )

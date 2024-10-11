import json
from collections import defaultdict

from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import (
    global_preferences_registry,
)
from dynamic_preferences.serializers import BaseSerializer
from dynamic_preferences.types import (
    BooleanPreference,
    StringPreference,
    IntegerPreference,
    LongStringPreference,
    BasePreferenceType,
)
from dynamic_preferences.users.registries import user_preferences_registry
from .registries import book_preferences_registry


general = Section("general")
discussion = Section("discussion")
access = Section("access")
debugging = Section("debugging")
layout = Section("layout")


# We start with a global preference
@global_preferences_registry.register
class SiteTitle(StringPreference):
    section = general
    name = "title"
    default = "My site"
    required = False


@global_preferences_registry.register
class MaintenanceMode(BooleanPreference):
    name = "maintenance_mode"
    default = False


# now we declare a per-user preference
@user_preferences_registry.register
class CommentNotificationsEnabled(BooleanPreference):
    """Do you want to be notified on comment publication ?"""

    section = discussion
    name = "comment_notifications_enabled"
    default = True


@user_preferences_registry.register
class DebugLevel(IntegerPreference):
    """
    set the debugging level for the UI. 0 is no debugging, 1 is some debugging, 2 is full debugging and will add lots of UI flow breaking stuff
    """

    section = debugging
    name = "debug_level"
    default = 0


string_types = str
from django.template import defaultfilters


class GridstackLayoutPreferenceSerializer(BaseSerializer):
    @classmethod
    def to_db(cls, value, **kwargs):
        # print("calling to_db in serializer")
        if not isinstance(value, string_types):
            raise cls.exception(
                "Cannot serialize, value {0} is not a string".format(value)
            )
        # print(f"value is '{value}'")
        if value == "":
            return ""

        data = json.loads(value)
        filtered = {
            x["id"]: {
                k: v
                for (k, v) in x.items()
                if k
                in [
                    "w",
                    "h",
                    "x",
                    "y",
                    "minH",
                    "minW",
                ]
            }
            for x in data
            if x.get("id")
        }
        for foo in filtered:
            if not "w" in filtered[foo]:
                filtered[foo]["w"] = filtered[foo]["minW"]

        out = json.dumps(filtered, indent=2)

        # print("out is ", out)
        if kwargs.get("escape_html", False):
            return defaultfilters.force_escape(out)
        else:
            return out

    @classmethod
    def to_python(cls, value, **kwargs):
        # print("calling to_python in serializer ")
        # print(f"value is '{value}'")
        if not value:
            return defaultdict(dict)
        try:
            return json.loads(value)
        except:
            raise cls.exception("Cannot deserialize value {0} to json".format(value))


class GridstackLayoutPreference(LongStringPreference):
    section = layout
    name = "dashboard_layout_json"
    verbose_name = "GridStack Layout Configuration"
    serializer = GridstackLayoutPreferenceSerializer

    # def serialize(self, value):
    #     """Convert dict to JSON string for storage"""
    #     if isinstance(value, str):
    #         return value
    #     return json.dumps(value)
    #
    # def deserialize(self, value):
    #     """Convert stored JSON string back to dict"""
    #     try:
    #         return json.loads(value)
    #     except json.JSONDecodeError:
    #         return {}


@user_preferences_registry.register
class DashboardLayout(GridstackLayoutPreference):
    section = layout
    name = "dashboard_layout_json"
    default = ""
    required = False


@book_preferences_registry.register
class IsPublic(BooleanPreference):
    section = access
    name = "is_public"
    default = False


@book_preferences_registry.register
class MaintenanceMode(BooleanPreference):
    name = "maintenance_mode"
    default = False


# @book_preferences_registry.register
# class DashboardLayout(LongStringPreference):
#     name = "dashboard_layout_json"
#     default = ""
#     required = False

# class GridstackLayoutPreference(PerInstancePreferenceType):
#     """
#     Stores gridstack layout configuration as JSON string
#     """
#     section = dashboard
#     name = 'gridstack_layout'
#     verbose_name = 'Gridstack Layout Configuration'
#
#     default = '{}'  # Empty JSON object as default
#
#     def validate(self, value):
#         """Ensure the value is valid JSON"""
#         try:
#             json.loads(value)
#             return True
#         except json.JSONDecodeError:
#             return False
#
#     def serialize(self, value):
#         """Convert dict to JSON string for storage"""
#         if isinstance(value, str):
#             return value
#         return json.dumps(value)
#
#     def deserialize(self, value):
#         """Convert stored JSON string back to dict"""
#         try:
#             return json.loads(value)
#         except json.JSONDecodeError:
#             return {}

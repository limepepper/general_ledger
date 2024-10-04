from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import (
    global_preferences_registry,
)
from dynamic_preferences.types import BooleanPreference, StringPreference, IntegerPreference
from dynamic_preferences.users.registries import user_preferences_registry
from .registries import book_preferences_registry


general = Section("general")
discussion = Section("discussion")
access = Section("access")
debugging = Section("debugging")


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


@book_preferences_registry.register
class IsPublic(BooleanPreference):
    section = access
    name = "is_public"
    default = False


@book_preferences_registry.register
class MaintenanceMode(BooleanPreference):
    name = "maintenance_mode"
    default = False

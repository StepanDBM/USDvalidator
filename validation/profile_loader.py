# validation/profile_loader.py

import json
#from dataclasses import dataclass
from pathlib import Path

from .profiles import ValidationProfile

class ProfileRegistry:

    def __init__(self, profiles):
        self._profiles = {}

        for profile in profiles:
            if profile.name in self._profiles:
                raise ValueError(
                    f"Duplicate profile name: {profile.name}"
                )

            self._profiles[profile.name] = profile

    def get(self, name):
        return self._profiles[name]

    def all(self):
        return tuple(self._profiles.values())

    def names(self):
        return tuple(self._profiles.keys())


class ProfileLoader:

    CURRENT_PROFILE = "default"

    def __init__(self, profiles_path):
        self.profiles_path = Path(profiles_path)
        self.registry = self._load_profiles()

    def _load_profiles(self):
        with self.profiles_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        profiles = []

        for entry in data["profiles"]:
            profiles.append(
                ValidationProfile(
                    name=entry["name"],
                    description=entry.get("description", ""),
                    enabled_check_ids=frozenset(
                        entry.get("enabled_checks", [])
                    ),
                    disabled_check_ids=frozenset(
                        entry.get("disabled_checks", [])
                    ),
                )
            )

        return ProfileRegistry(profiles)

    def get_current_profile(self):
        return self.registry.get(self.CURRENT_PROFILE)

    def get_profile(self, name):
        return self.registry.get(name)

    def get_profiles(self):
        return self.registry.all()

    def get_profile_names(self):
        return self.registry.names()
import json
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

    # ------------------------------------------------------------------
    # Write side
    # ------------------------------------------------------------------

    def add_profile(self, profile):
        if profile.name in self.registry.names():
            raise ValueError(
                f"Profile already exists: {profile.name}"
            )

        profiles = list(self.registry.all())
        profiles.append(profile)

        self.registry = ProfileRegistry(profiles)

    def update_profile(self, profile):
        if profile.name not in self.registry.names():
            raise KeyError(
                f"Profile does not exist: {profile.name}"
            )

        profiles = [
            profile if existing.name == profile.name else existing
            for existing in self.registry.all()
        ]

        self.registry = ProfileRegistry(profiles)

    def delete_profile(self, name):
        if name not in self.registry.names():
            raise KeyError(
                f"Profile does not exist: {name}"
            )

        profiles = [
            profile
            for profile in self.registry.all()
            if profile.name != name
        ]

        if not profiles:
            raise ValueError(
                "Cannot delete the last validation profile."
            )

        self.registry = ProfileRegistry(profiles)

    def save(self):
        data = {
            "profiles": [
                {
                    "name": profile.name,
                    "description": profile.description,
                    "enabled_checks": sorted(
                        profile.enabled_check_ids
                    ),
                    "disabled_checks": sorted(
                        profile.disabled_check_ids
                    ),
                }
                for profile in self.registry.all()
            ]
        }

        with self.profiles_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=4,
            )
            file.write("\n")

    def replace_profile(self, old_name, profile):
        if old_name not in self.registry.names():
            raise KeyError(
                f"Profile does not exist: {old_name}"
            )

        if (
            profile.name != old_name
            and profile.name in self.registry.names()
        ):
            raise ValueError(
                f"Profile already exists: {profile.name}"
            )

        profiles = [
            profile if existing.name == old_name else existing
            for existing in self.registry.all()
        ]

        self.registry = ProfileRegistry(profiles)
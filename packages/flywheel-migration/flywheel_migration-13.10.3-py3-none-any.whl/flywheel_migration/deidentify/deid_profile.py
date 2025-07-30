"""Provides profile loading/saving for file de-identification."""

import copy

from . import factory
from .deid_log import DeIdLog
from .file_profile import FileProfile

NESTED_PROFILE_NAMES = ["zip"]


class DeIdProfile:
    """Represents steps to take to de-identify a file or set of files."""

    def __init__(self):
        # Multiple file profiles
        # Optional name / description
        self.name = None
        self.description = None

        self.map_subjects_url = None
        self.map_subjects = None

        # secret_key can be set globally or file-profile specific
        self.secret_key = None

        self.log = None

        self.file_profiles = []
        self.only_config_profiles = False

    def __bool__(self):
        return self.name != "none"

    def to_config(self):
        """Create configuration dictionary from this profile."""
        result = {}

        if self.name is not None:
            result["name"] = self.name

        if self.description is not None:
            result["description"] = self.description

        if self.map_subjects_url is not None:
            result["map-subjects"] = self.map_subjects_url

        if self.secret_key is not None:
            result["secret-key"] = self.secret_key

        if self.only_config_profiles:
            result["only-config-profiles"] = self.only_config_profiles

        if self.log is not None:
            result["deid-log"] = self.log.to_config_str()

        for profile in self.file_profiles:
            result[profile.name] = profile.to_config()

        return result

    def initialize(self):
        """Initialize the profile, prior to importing."""
        if self.log:
            self.log.initialize(self)

    def finalize(self):
        """Perform any necessary cleanup with profile."""
        if self.log:
            self.log.close()

    def validate(self, enhanced=False):
        """Validate the profile, returning any errors.

        Returns:
            list(str): A list of error messages, or an empty list
        """
        errors = []
        for file_profile in self.file_profiles:
            errors += file_profile.validate(enhanced=enhanced)
        return errors

    def load_config(self, config):
        """Initialize this profile from a config dictionary."""
        self.name = config.get("name")
        self.description = config.get("description")

        # Load subject map
        self.map_subjects_url = config.get("map-subjects")
        if self.map_subjects_url:
            self.map_subjects = factory.load_subject_map(self.map_subjects_url)

        self.secret_key = config.get("secret-key")

        # De-id logfile
        log_str = config.get("deid-log")
        if log_str:
            self.log = DeIdLog.factory(log_str)

        # Load file profiles
        nested_profiles = list()
        for name in FileProfile.profile_names():
            # We shouldn't load profiles that are not defined in the config
            # Left dicom alone since there's a test that expects it to load
            # and that may indicate that for dicom, it's expected functionality,
            # perhaps for reaper or CLI
            if name == "dicom" or name in config.keys():
                # If secret_key is defined globally and not at profile level,
                # we want to pass that through to each profile.
                profile_config = config.get(name)
                if self.secret_key and "secret-key" not in profile_config:
                    profile_config["secret-key"] = self.secret_key

                if name not in NESTED_PROFILE_NAMES:
                    self.file_profiles.append(
                        FileProfile.factory(name, config=profile_config, log=self.log)
                    )
                elif name in NESTED_PROFILE_NAMES:
                    nested_profile = FileProfile.factory(
                        name, config=config, log=self.log
                    )
                    # Merge related note - may need to adjust secret-key passing here
                    nested_profiles.append(nested_profile)
        self.file_profiles.extend(nested_profiles)
        self.initialize()

    def get_file_profile(self, name):
        """Get file profile for name, or None if not present."""
        for profile in self.file_profiles:
            if profile.name == name:
                profile.deid_name = self.name
                return profile
        return None

    def process_file(self, src_fs, src_file, dst_fs):
        """Process the given file, if it's handled by a file profile.

        Args:
            src_fs: The source filesystem
            src_file: The source file path
            dst_fs: The destination filesystem

        Returns:
            bool: True if the file was processed, false otherwise
        """

        def dst_callback(_, dst_path):
            return dst_path

        for profile in self.file_profiles:
            if profile.matches_file(src_file) or profile.matches_byte_sig(
                src_fs, src_file
            ):
                dst_path = profile.process_files(
                    src_fs, dst_fs, [src_file], callback=dst_callback
                )
                if dst_path:
                    if dst_fs.isfile(dst_path):
                        return True
        return False

    def process_packfile(self, packfile_type, src_fs, dst_fs, paths, callback=None):
        """Process the given packfile, if it's handled by a file profile.

        Args:
            packfile_type (str): The packfile type
            src_fs: The source filesystem
            dst_fs: The destination filesystem
            paths: The list of paths to process
            callback: Optional function to call after processing each file

        Returns:
            bool: True if the packfile was processed, false otherwise
        """
        for profile in self.file_profiles:
            if profile.matches_packfile(packfile_type):
                profile.process_files(src_fs, dst_fs, paths, callback=callback)
                return True
        return False

    def matches_file(self, filename):
        """
        Determine from filename whether any of the file_profiles match on the filename
        Args:
            filename: name of the file to match

        Returns:
            bool: True if a profile matches the filename, False if none match
        """
        return any(profile.matches_file(filename) for profile in self.file_profiles)

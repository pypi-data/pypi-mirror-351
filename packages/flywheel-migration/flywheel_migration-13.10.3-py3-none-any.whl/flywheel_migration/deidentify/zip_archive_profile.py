"""File profile for processing zip files"""

import logging
import os
import shutil
import tempfile
import zipfile
from collections import OrderedDict

from fs import copy as fs_copy
from fs.osfs import OSFS
from fs.tempfs import TempFS
from fs.zipfs import ZipFS

from flywheel_migration.util import hash_path

from .deid_field import DeIdField
from .deid_profile import NESTED_PROFILE_NAMES
from .file_profile import FileProfile

log = logging.getLogger(__name__)


class ZipArchiveRecord:
    """
    Record class for zip archives
    """

    def __init__(self, src_fs, path):
        self.src_path = path
        self.src_sys_path = self.get_zip_sys_path(src_fs, path)
        self.comment = None
        self.src_info = None
        self.zip_members = OrderedDict()
        self.src_info, self.comment = self.load_zip_info(src_fs, path)
        self.initialize_zip_members()
        self.processed_sys_path = None

    @staticmethod
    def get_zip_sys_path(src_fs, path):
        """
        Gets a system path for path within src_fs (if it exists). If src_fs has no syspath, a temporary directory will
        be instantiated and the zip at path within src_fs will be copied to the temporary directory

        Args:
            src_fs (fs.base.FS): the filesystem where zip is located at path
            path (str): path to a zip file on src_fs
        Returns:
            (None or str): a syspath for the zip
        """
        if not src_fs.exists(path):
            zip_sys_path = None

        elif src_fs.hassyspath(path):
            zip_sys_path = src_fs.getsyspath(path)
        else:
            temp_dir = tempfile.mkdtemp()
            temp_sys_fs = OSFS(temp_dir)
            dirname, filename = os.path.split(path)
            if dirname:
                temp_sys_fs.makedirs(dirname, recreate=True)
            fs_copy.copy_file(
                src_fs=src_fs, src_path=path, dst_fs=temp_sys_fs, dst_path=path
            )
            zip_sys_path = temp_sys_fs.getsyspath(path)
        return zip_sys_path

    @staticmethod
    def encode_comment(input_comment):
        """
        Will attempt to convert the input_comment to bytes for application to a zip archive as a comment. If not str or
        bytes, an empty byte string will be returned (b'')

        Args:
            input_comment(bytes or str): an input comment

        Returns:
            bytes: the encoded comment or an empty byte string
        """
        if isinstance(input_comment, str):
            output_comment = input_comment.encode()
        elif isinstance(input_comment, bytes):
            output_comment = input_comment
        else:
            log.warning(
                "Comment is not bytes or string. Comment will be set to empty bytestring."
            )
            output_comment = b""
        return output_comment

    @staticmethod
    def load_zip_info(input_fs, zip_path):
        """
        Returns the infolist and comment attributes of the zip at zip path
        Args:
            input_fs (fs.base.FS): an input file system containing a zip at path
            zip_path (str): path to a zip within input_fs

        Returns:
            tuple: a tuple of the infolist and comment attributes of the zip archive
        """
        if not input_fs.exists(zip_path):
            log.error("zip at %s does not exist!", zip_path)
            return None
        if not input_fs.isfile(zip_path):
            log.error("zip at %s does not exist!", zip_path)
            return None
        with input_fs.open(zip_path, "rb") as file_data:
            if not zipfile.is_zipfile(file_data):
                log.error("file at %s is not a zip!", zip_path)
                return None
            with zipfile.ZipFile(file_data, "r") as zip_file:
                zip_info = zip_file.infolist()
                zip_comment = zip_file.comment
        return zip_info, zip_comment

    def initialize_zip_members(self):
        """
        Initializes an ordered dictionary with key/value pairs for each member of the infolist at self.zip_members

        Returns:
            collections.OrderedDict: an ordered dictionary with key/value pairs of zip member info.filename,
                ZipArchiveMemberRecord for every item on the ZipArchiveRecord's infolist
        """
        for member in self.src_info:
            self.zip_members[member.filename] = ZipArchiveMemberRecord(member.filename)
        return self.zip_members

    def _process_zip_members(self, archive_profile, dst_fs, hash_subdir=False):
        """
        De-identifies zip members according to the archive_profile, outputting them to dst_fs

        Args:
            archive_profile(flywheel_migration.deidentify.ZipArchiveProfile): a de-identification template profile for
                zip archives
            dst_fs(fs.base.FS): the destination filesystem to which to export zip archive members
            hash_subdir(bool): whether to perform md5 hashing on zip archive subdirectories

        """
        with ZipFS(self.src_sys_path) as src_zip_fs:
            for member in self.zip_members.values():
                member.process_file(
                    archive_profile=archive_profile,
                    src_fs=src_zip_fs,
                    dst_fs=dst_fs,
                    hash_subdir=hash_subdir,
                )

    def process_zip(self, archive_profile, hash_subdir=False):
        """
        Processes the archive at self.src_sys_path and returns the absolute path to the de-identified zip

        Args:
            archive_profile(flywheel_migration.deidentify.ZipArchiveProfile): a de-identification template profile for
                zip archives
            hash_subdir(bool): whether to perform md5 hashing on zip archive subdirectories

        Returns:
            str: absolute path to the processed zip archive
        """
        # Create a tempfile
        fd, temp_zip_path = tempfile.mkstemp()

        # Process zip contents in order of info list
        with ZipFS(temp_zip_path, write=True) as dst_zip_fs:
            self._process_zip_members(
                archive_profile=archive_profile,
                dst_fs=dst_zip_fs,
                hash_subdir=hash_subdir,
            )
        # Copy comment
        with zipfile.ZipFile(temp_zip_path, "a") as zipa:
            zipa.comment = self.encode_comment(self.comment)

        self.processed_sys_path = temp_zip_path
        os.close(fd)
        return temp_zip_path

    def get_missing(self):
        """
        Determine which zip_members are missing dst_path, if any

        Returns:
            list: src_paths of zip_members missing dst_path

        """
        missing = list()
        for src_path, member in self.zip_members.items():
            if not member.processed:
                missing.append(src_path)
        if missing:
            log.error(
                "Failed to process %s zip members\n %s",
                len(missing),
                "\n".join([f"\t{item}" for item in missing]),
            )
        return missing

    def save_as(self, dst_fs, path):
        """Saving zip archive

        Args:
            dst_fs(fs.base.FS): the filesystem to which to save the de-identified archive
            path(str): the path within dst_fs to which to save the de-identified archive
        """

        if not self.processed_sys_path:
            log.error(
                "%s has not been processed. process_zip method must first be executed to save_as",
                self.src_path,
            )
        else:
            dirname, zipname = os.path.split(self.processed_sys_path)
            with OSFS(dirname) as src_fs:
                fs_copy.copy_file(
                    src_fs=src_fs, src_path=zipname, dst_fs=dst_fs, dst_path=path
                )
                src_fs.remove(zipname)

    def __del__(self):
        """Remove temporary dir/files at processed_sys_path and src_sys_path"""
        if self.processed_sys_path and os.path.isfile(self.processed_sys_path):
            os.remove(self.processed_sys_path)  # only delete file
        if self.src_sys_path:
            dirname = os.path.dirname(self.src_sys_path)
            if os.path.isdir(dirname) and not os.environ.get("TMPDIR"):
                shutil.rmtree(dirname)


class ZipArchiveMemberRecord:
    """
    Record class for zip archive members
    """

    def __init__(self, src_path):
        self.src_path = src_path
        self.src_filename = None
        self.src_subdir = None
        self.dst_subdir = None
        self.dst_filename = None
        self.is_dir = None
        self.dst_path = None
        self.processed = False
        self.parse_path()
        self.dst_record = None

    def parse_path(self):
        """
        Parses self.src_subdir and self.src_filename from self.src_path. Also determines whether ZipArchiveMemberRecord
            is a subdirectory (for bypassing process_file)

        """
        dirname, basename = os.path.split(self.src_path)
        if self.src_path.endswith(os.path.sep):
            self.is_dir = True
            self.src_filename = None
            self.src_subdir = dirname
        else:
            self.is_dir = False
            if not dirname:
                self.src_subdir = None
            else:
                self.src_subdir = dirname
            self.src_filename = basename.lstrip(os.path.sep)

    def get_callback(self, subdir=None, callback=None):
        """
        Returns a callback function that wraps the input callback function. Importantly, this function can be passed
            to a FileProfile's process_files method to allow for setting self.dst_path asynchronously
        Args:
            subdir(str or None): the subdirectory within the parent zip that contains the ZipArchiveMemberRecord
                (set by self.set_dst_subdir method)
            callback (function or None): a callback function to wrap
        Returns:
            (function): a callback function to pass to a FileProfile's process_files method
        """

        def callback_output(dst_fs, dst_path):
            self.dst_filename = dst_path
            if subdir:
                dst_path = os.path.join(subdir, dst_path.lstrip(os.path.sep))
            self.dst_path = dst_path

            if callable(callback):
                callback(dst_fs, dst_path)

        return callback_output

    def get_path_dict(self):
        """
        Get a dictionary of the src_path and dst_path attribute values for the ZipArchiveMemberRecord

        Returns:
            (dict): a dictionary with src_path and dst_path keys with values of their respective ZipArchiveMemberRecord
                attributes
        """
        path_dict = {"src_path": self.src_path, "dst_path": self.dst_path}
        return path_dict

    def set_dst_subdir(self, hash_subdir=False, profile=None):
        """
        Set/return the dst_subdir attribute (the subdirectory within the parent ZipArchive, md5 hashed as specified)
        Args:
            hash_subdir(bool): whether to hash the src_subdir, if False (default), will simply use the src_subdir value
            profile (ZipArchiveProfile): the profile from which to select matching file_profiles

        Returns:
            dst_subdir(str): subdirectory path in which to place the ZipArchiveMember

        """

        dst_subdir = self.src_subdir
        if dst_subdir and hash_subdir:
            if not profile:
                raise ValueError("profile cannot be None when hash_subdir=True")

            def hash_func(inp_value):
                # pylint: disable=protected-access
                ret_val = DeIdField._hash(profile=profile, value=inp_value)
                return ret_val

            dst_subdir = hash_path(dst_subdir, hash_func)
        self.dst_subdir = dst_subdir
        return self.dst_subdir

    def process_subdir(self, dst_fs, callback=None):
        """
        Add a subdirectory to the dst_fs filesystem if it doesn't already exist and set the dst_path attribute to the
            same value as the dst_subdir attribute

        Args:
            dst_fs(fs.base.FS): the filesystem in which to save the subdirectory
            callback: a callback function to which to pass dst_fs and self.dest_path
        """
        if self.is_dir and self.dst_subdir:
            if not dst_fs.isdir(self.dst_subdir):
                dst_fs.makedirs(self.dst_subdir)
        if dst_fs.exists(self.dst_subdir):
            self.dst_path = self.dst_subdir
            self.processed = True
            if callable(callback):
                callback(dst_fs, self.dst_path)

    def get_profile_list(self, archive_profile, src_fs):
        """
        Return a list of the file profiles that match the ZipMemberFileRecord (according to the evaluation of
            profile.matches_file(self.src_filename)

        Args:
            archive_profile(ZipArchiveProfile): the profile from which to select matching file_profiles

        Returns:
            list: a list of FileProfiles that match the ZipMemberFileRecord

        """
        profile_list = list()
        if archive_profile.matches_file(
            self.src_filename
        ) or archive_profile.matches_byte_sig(src_fs, self.src_filename):
            profile_list.append(archive_profile)
        for profile in archive_profile.file_profiles:
            if profile.matches_file(self.src_filename) or profile.matches_byte_sig(
                src_fs, self.src_path
            ):
                profile_list.append(profile)
        return profile_list

    def process_file(self, src_fs, dst_fs, archive_profile, hash_subdir=False):
        """
        Processes the zip member file (or directory) according to the de-identification template provided

        Args:
            src_fs(fs.zipfs.ZipFS): the source ZipFS
            dst_fs(fs.zipfs.ZipFS): the destination ZipFS
            archive_profile(ZipArchiveProfile): the profile to apply
            hash_subdir(bool): whether to hash the subdirectory containing the file (if applicable)

        Returns:
            (bool): whether the zip member file (or directory) was successfully processed
        """

        # Can't process if it doesn't exist
        if not src_fs.exists(self.src_path):
            log.error(
                "File %s does not exist in source zip and will not be exported!",
                self.src_path,
            )
            return False

        # Get and set dst subdir
        dst_subdir = self.set_dst_subdir(
            hash_subdir=hash_subdir, profile=archive_profile
        )
        if self.processed:
            log.warning(
                "file %s has already been processed as %s. Cannot process again.",
                self.src_path,
                self.dst_path,
            )
            return True

        # Handle subdirectory specifically
        if self.is_dir:
            self.process_subdir(dst_fs, callback=self.get_callback())

        # Process files
        else:
            callback_func = self.get_callback(subdir=dst_subdir)
            profile_list = self.get_profile_list(archive_profile, src_fs)
            if not profile_list:
                return False
            # temp fs to avoid lock-related issues
            with TempFS() as src_temp_fs:
                with TempFS() as dst_temp_fs:
                    fs_copy.copy_file(
                        src_fs=src_fs,
                        src_path=self.src_path,
                        dst_fs=src_temp_fs,
                        dst_path=self.src_filename,
                    )

                    for profile in profile_list:
                        profile.process_files(
                            src_fs=src_temp_fs,
                            dst_fs=dst_temp_fs,
                            files=[self.src_filename],
                            callback=callback_func,
                        )

                        if self.dst_path:
                            if dst_fs.exists(self.dst_path):
                                log.warning(
                                    "path %s already exists in zip. Please profile filenames output values"
                                    " are unique for each file.",
                                    self.dst_path,
                                )
                                return False
                            if dst_subdir:
                                if not dst_fs.isdir(dst_subdir):
                                    dst_fs.makedirs(dst_subdir, recreate=True)
                            fs_copy.copy_file(
                                src_fs=dst_temp_fs,
                                src_path=self.dst_filename,
                                dst_fs=dst_fs,
                                dst_path=self.dst_path,
                            )
                            self.processed = True
                            return self.processed

                        continue

        return self.processed


class ZipArchiveProfile(FileProfile):
    """This profile subclass allows for processing of zip archives and their members"""

    default_file_filter = ["*.zip", "*.ZIP"]
    name = "zip"
    hash_digits = 16
    file_signatures = [
        (0, b"\x50\x4b\x03\x04"),
        (0, b"\x50\x4b\x05\x06"),
        (0, b"\x50\x4b\x07\x08"),
    ]

    def __init__(self, file_filter=None):
        file_filter = file_filter or self.default_file_filter
        super(ZipArchiveProfile, self).__init__(
            packfile_type="zip", file_filter=file_filter
        )
        self.hash_subdirectories = False
        self.file_profiles = list()
        self.validate_zip_members = False

    def _load_file_profile_config(self, file_profiles):
        """
        loads the file profiles to be used to process member files

        Args:
            file_profiles(list): list of dicts with key value pairs of profile name/ profile.to_config()

        Returns:
            list: list of FileProfiles to be added to ZipArchiveProfile.file_profiles
        """
        file_profile_list = list()
        flat_profile_name_list = [
            name
            for name in FileProfile.profile_names()
            if name not in NESTED_PROFILE_NAMES
        ]
        for pconf_dict in file_profiles:
            for pname, name_config in pconf_dict.items():
                if pname in flat_profile_name_list:
                    file_profile_list.append(
                        FileProfile.factory(pname, config=name_config, log=self.log)
                    )
        return file_profile_list

    def load_config(self, config):
        """
        Read configuration from a dictionary representation of the ZipArchiveProfile

        Args:
            config(dict): dictionary from which to read a config ("zip" namespace in the de-id template file)

        """
        zip_config = config.get(self.name)
        super(ZipArchiveProfile, self).load_config(zip_config)

        if zip_config.get("hash-subdirectories"):
            self.hash_subdirectories = True

        if zip_config.get("validate-zip-members"):
            self.validate_zip_members = zip_config.get("validate-zip-members")

        for profile_name, profile_config in config.items():
            if (
                profile_name in FileProfile.profile_names()
                and profile_name != self.name
            ):
                self.file_profiles.append(
                    FileProfile.factory(profile_name, profile_config, log=self.log)
                )

    def to_config(self):
        """
        Output ZipFileProfile to a configuration dictionary

        Returns:
            dict: dict representation of the ZipArchiveProfile
        """
        result = super(ZipArchiveProfile, self).to_config()
        result["hash-subdirectories"] = self.hash_subdirectories
        result["validate-zip-members"] = self.validate_zip_members
        return result

    def load_record(self, state, src_fs, path):
        """Load the record(file) at path, return None to ignore this file"""
        modified = False
        record = ZipArchiveRecord(src_fs=src_fs, path=path)
        record.initialize_zip_members()
        if record.zip_members:
            modified = True
        return record, modified

    def save_record(self, state, record, dst_fs, path):
        """
        Save the ZipArchiveRecord to the destination path on the dst_fs filesystem
        Args:
            state: arbitrary value (not used by the ZipArchiveProfile subclass)
            record(ZipArchiveRecord): the record to save to path
            dst_fs(fs.base.FS): the filesystem to which to save the ZipArchiveRecord at path
            path(str): the path to which to save the record within dest_fs

        """
        super(ZipArchiveProfile, self).save_record(self, record, dst_fs, path)
        record.save_as(dst_fs, path)

    def read_field(self, state, record, fieldname):
        """
        Read the fieldname attribute of a ZipArchiveRecord
        Args:
            state: arbitrary value (not used by the ZipArchiveProfile subclass)
            record (ZipArchiveRecord): the record from which to read the fieldname attribute
            fieldname(str): the name of the attribute to read from ZipArchiveRecord

        Returns:
            the value of the fieldname attribute of the provided record. None if the record does not have the attr
        """
        field_value = getattr(record, fieldname, None)
        if not field_value:
            for f_profile in self.file_profiles:
                if getattr(f_profile, "record", None):
                    f_p_record_value = f_profile.read_field(
                        None, f_profile.record, fieldname
                    )
                    if f_p_record_value is not None:
                        field_value = f_p_record_value
                        return field_value
        return field_value

    def remove_field(self, state, record, fieldname):
        """
        Remove the fieldname attribute from a ZipArchiveRecord record (set it to None)

        Args:
            state: arbitrary value (not used by the ZipArchiveProfile subclass)
            record(ZipArchiveRecord): the record from which to remove the fieldname attribute
            fieldname(str): the name of the attribute to read from ZipArchiveRecord
        """
        setattr(record, fieldname, None)

    def replace_field(self, state, record, fieldname, value):
        """
        Replace the fieldname attribute from a ZipArchiveRecord record with value

        Args:
            state: arbitrary value (not used by the ZipArchiveProfile subclass)
            record(ZipArchiveRecord): the record from which to remove the fieldname attribute
            fieldname(str): the name of the attribute to read from ZipArchiveRecord
            value: the value to which to set the fieldname attribute of the record
        """
        setattr(record, fieldname, value)

    def process_files(self, src_fs, dst_fs, files, callback=None):
        """Process all files in the file list, performing de-identification steps

        Args:
            src_fs: The source filesystem (Provides open function)
            dst_fs: The destination filesystem
            files: The set of files in src_fs to process
            callback: Function to call after writing each file
        """
        state = self.create_file_state()

        for path in files:
            record, modified = self.load_record(state, src_fs, path)

            # Record could be None if it should be skipped
            if not record:
                continue
            # Set filenames attributes on record
            self.set_filenames_attributes(record, path)

            if modified or self.fields:
                if self.log:
                    self.write_log_entry(path, "before", state, record)

                # De-identify
                for field in self.fields:
                    field.deidentify(self, state, record)

                # Create after entry, if log is provided
                if self.log:
                    self.write_log_entry(path, "after", state, record)

                # Process zip member files
                record.process_zip(
                    archive_profile=self, hash_subdir=self.hash_subdirectories
                )

                # Get destination path
                dst_path = self.get_dest_path(state, record, path)

                # Destination could be None if it should be skipped
                if not dst_path:
                    continue

                if not self.record:
                    self.record = record

                if self.validate_zip_members and record.get_missing():
                    log.error(
                        "Failed to process zip members in %s. Skipping archive", path
                    )
                    continue

                # Save to dst_fs if we modified the record
                self.save_record(state, record, dst_fs, dst_path)

            else:
                # Get destination path
                dst_path = self.get_dest_path(state, record, path)
                # Destination could be None if it should be skipped
                if not dst_path:
                    continue

                # No fields to de-identify, just copy to dst
                with src_fs.open(path, "rb") as src_file:
                    dst_fs.upload(dst_path, src_file)

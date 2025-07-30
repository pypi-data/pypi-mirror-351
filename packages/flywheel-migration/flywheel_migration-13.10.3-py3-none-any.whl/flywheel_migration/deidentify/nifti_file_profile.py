import logging
from io import BytesIO

import nibabel as nib
from fs.errors import NoSysPath

from flywheel_migration.deidentify.file_profile import FileProfile

log = logging.getLogger(__name__)


class NiftiRecord:
    """A record for dealing with nifti file."""

    types = [nib.nifti1.Nifti1Image, nib.nifti2.Nifti2Image]

    def __init__(self, path, mode="r"):  # rw to allow for saving in place
        self.image = nib.load(path)
        self._metadata = None
        self.validate()

    @property
    def metadata(self):
        """Load NIfTI metadata."""
        # if self._metadata is None:
        #     self._metadata = self.image.header
        # return self._metadata
        return self.image.header

    def validate(self):
        """Validate image against expecting type."""
        if type(self.image) not in self.types:
            raise TypeError(
                f"Expected Nifti1Image or Nifti2Image, found {type(self.image)}."
            )

    def save_as(self, path, file_type="NIfTI"):
        """Save deid image.

        Args:
            path: A file path
            file_type: Image format to save as
        """
        nib.save(self.image, path)


class NiftiFileProfile(FileProfile):
    """NIfTI implementation of load/save and remove/replace fields."""

    name = "nifti"
    default_file_filter = ["*.nii", "*.nii.gz"]
    allowed_fields = set(
        list(nib.Nifti1Header().keys()) + list(nib.Nifti2Header().keys())
    )

    def __init__(self, file_filter=None):
        file_filter = file_filter if file_filter else self.default_file_filter
        super(NiftiFileProfile, self).__init__(
            packfile_type=self.name, file_filter=file_filter
        )

    def load_record(self, state, src_fs, path):
        """Load the record(file) at path, return None to ignore this file."""
        modified = False
        try:
            sys_path = src_fs.getsyspath(path)
            record = NiftiRecord(sys_path)
        except NoSysPath:
            log.error("IGNORING %s - cannot get system path!", path)
            return None, False
        except TypeError:
            log.warning("IGNORING %s - it is not a NIfTI file!", path)
            return None, False
        return record, modified

    def save_record(self, state, record, dst_fs, path):
        """Save the record to the destination path."""
        sys_path = dst_fs.getsyspath(path)
        record.save_as(sys_path)

    def read_field(self, state, record, fieldname):
        """Read the named field as a string. Return None if field cannot be read."""
        if not (metadata := getattr(record, "metadata", None)):
            return None
        return metadata.get(fieldname, None)

    def remove_field(self, state, record, fieldname):
        """Blank the named field from the record. Removal not supported."""
        if self.read_field(state, record, fieldname):
            if isinstance(record.metadata[fieldname].item(), (str, bytes)):
                record.metadata[fieldname] = ""
            elif isinstance(record.metadata[fieldname].item(), (int, float)):
                record.metadata[fieldname] = 0

    def replace_field(self, state, record, fieldname, value):
        """Replace the named field with value in the record."""
        if self.read_field(state, record, fieldname):
            try:
                record.metadata[fieldname] = value
            except (TypeError, ValueError):
                log.error(
                    "Incorrect type: Cannot replace field %s with value %s",
                    fieldname,
                    value,
                )

    def validate(self, enhanced=False):
        """Validate the profile, returning any errors.

        Args:
            enhanced (bool): If True, test profile execution on a set of test files

        Returns:
            list(str): A list of error messages, or an empty list
        """
        errors = super(NiftiFileProfile, self).validate(enhanced=enhanced)

        for field in self.fields:
            lc_field = field.fieldname.lower()
            if lc_field not in NiftiFileProfile.allowed_fields:
                errors.append(f"Not in NIFTI header: {field.fieldname}")

        return errors

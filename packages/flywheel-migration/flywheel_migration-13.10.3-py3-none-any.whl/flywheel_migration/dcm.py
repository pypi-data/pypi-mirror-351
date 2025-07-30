"""DICOM file wrapper."""

import collections
import datetime
import logging
import pathlib
import warnings
from io import BufferedIOBase
from typing import BinaryIO

import pydicom
import pydicom.datadict
import pydicom.filereader
import six
from pydicom import values
from pydicom.datadict import dictionary_VR
from pydicom.hooks import hooks, raw_element_value
from pydicom.tag import Tag

from . import util

log = logging.getLogger(__name__)

FILETYPE = "dicom"
GEMS_TYPE_SCREENSHOT = ["DERIVED", "SECONDARY", "SCREEN SAVE"]
GEMS_TYPE_VXTL = ["DERIVED", "SECONDARY", "VXTL STATE"]


class DicomFileError(pydicom.errors.InvalidDicomError):
    """DicomFileError class."""

    def __str__(self):
        """Return the wrapped exception's `str()`."""
        return str(self.args[0])  # pylint: disable=unsubscriptable-object


class DicomFile:
    """DicomFile class."""

    # pylint: disable=too-few-public-methods
    # pylint: disable=too-many-arguments, too-many-branches, too-many-statements
    def __init__(
        self,
        file,
        map_key=None,
        subj_key=None,
        session_label_key=None,
        parse=False,
        de_identify=False,
        update_in_place=True,
        timezone=None,
        decode=True,
        stop_when=None,
        stop_before_pixels=False,
        **kwargs,
    ):
        file_is_object = False
        if isinstance(file, (str, pathlib.Path)):
            fp = open(file, "rb")
        elif isinstance(file, (BufferedIOBase, BinaryIO)):
            fp = file
            file_is_object = True
        else:
            raise TypeError(
                "DicomFile: Expected a file to be a string file path, pathlib.Path, or readable "
                f"buffer, but got {type(file).__name__}"
            )
        map_key = (
            map_key.split("_", 1)[1]
            if map_key and map_key.startswith("RETIRED_")
            else map_key
        )
        subj_key = (
            subj_key.split("_", 1)[1]
            if subj_key and subj_key.startswith("RETIRED_")
            else subj_key
        )
        timezone = util.DEFAULT_TZ if timezone is None else timezone
        if stop_when and stop_before_pixels:
            raise ValueError("stop_when and stop_before_pixels are mutually exclusive")
        if stop_before_pixels and de_identify:
            warnings.warn(
                "DicomFile: Conflicting de_identify and stop_before_pixels parameters provided. "
                "Deidentification requires DicomFile to read all DICOM tags, therefore overriding "
                "stop_before_pixels to False.",
                UserWarning,
            )
            stop_before_pixels = False
        if stop_when and not callable(stop_when):
            stop_when = stop_at_tag(stop_when)
        if stop_before_pixels:
            stop_when = _pixel_data
        try:
            self.raw = dcm = pydicom.filereader.read_partial(
                fp, stop_when=stop_when, **kwargs
            )
            if decode:
                reset_config = set_vr_mismatch_callback()
                dcm.decode()
                reset_config()
        except (pydicom.errors.InvalidDicomError, ValueError) as ex:
            raise DicomFileError(ex)
        finally:
            if not file_is_object:
                fp.close()

        sort_info = dcm.get(map_key, "") if map_key else ""

        # acq_datetime
        if self.get_manufacturer().startswith("SIEMENS"):
            acq_datetime = self.timestamp(
                dcm.get("SeriesDate"), dcm.get("SeriesTime"), timezone
            )
        else:
            acq_datetime = self.timestamp(
                dcm.get("AcquisitionDate"), dcm.get("AcquisitionTime"), timezone
            )

        # acq_no
        if self.get_manufacturer().startswith(("SIEMENS", "BRUKER")):
            self.acq_no = None
        else:
            acq_no = dcm.get("AcquisitionNumber")
            self.acq_no = str(acq_no) if acq_no else None

        if parse or de_identify:
            self.series_uid = series_uid = dcm.get("SeriesInstanceUID")
            if self._is_screenshot(dcm.get("ImageType")):
                front, back = series_uid.rsplit(".", 1)
                series_uid = front + "." + str(int(back) - 1)
            study_datetime = self.timestamp(
                dcm.get("StudyDate"), dcm.get("StudyTime"), timezone
            )
            self.session_uid = dcm.get("StudyInstanceUID")
            self.session_label = (
                dcm.get(session_label_key) if session_label_key else None
            )
            self.session_timestamp = study_datetime
            self.session_operator = dcm.get("OperatorsName")
            self.subject_firstname, self.subject_lastname = self._parse_patient_name(
                dcm.get("PatientName", "")
            )
            (
                self.subject_label,
                self.group__id,
                self.project_label,
            ) = util.parse_sort_info(sort_info, "ex" + str(dcm.get("StudyID", "")))
            if subj_key:
                self.subject_label = dcm.get(subj_key, "")
            self.acquisition_uid = series_uid + (
                "_" + str(self.acq_no)
                if self.acq_no is not None and int(self.acq_no) > 1
                else ""
            )
            self.acquisition_timestamp = acq_datetime or study_datetime
            self.acquisition_label = dcm.get("SeriesDescription")
            self.file_type = FILETYPE

        if de_identify:
            self.subject_firstname = self.subject_lastname = None
            if dcm.get("PatientBirthDate"):
                dob = self._parse_patient_dob(dcm.PatientBirthDate)
                if dob and study_datetime:
                    months = (
                        12 * (study_datetime.year - dob.year)
                        + (study_datetime.month - dob.month)
                        - (study_datetime.day < dob.day)
                    )
                    dcm.PatientAge = (
                        "%03dM" % months if months < 960 else "%03dY" % (months / 12)
                    )
            del dcm.PatientBirthDate
            del dcm.PatientName
            del dcm.PatientID
            if update_in_place:
                if not file_is_object:
                    dcm.save_as(file)
                else:
                    warnings.warn(
                        "DicomFile: Cannot update file in place when file is a file object.",
                        UserWarning,
                    )

    @property
    def subject_code(self):
        """Backward-compatibility #FLYW-3539."""
        warnings.warn(
            "'code' attribute is deprecated now. Use 'label'", DeprecationWarning
        )
        return self.subject_label

    @subject_code.setter
    def subject_code(self, code):
        """Backward-compatibility #FLYW-3539."""
        warnings.warn(
            "'code' attribute is deprecated now. Use 'label'", DeprecationWarning
        )
        self.subject_label = code

    def save(self, dst_file):
        """Save the dicom file as dst_file."""
        self.raw.save_as(dst_file)

    def get(self, key, default=None):
        """Helper to get value from raw (or default)."""
        return self.raw.get(key, default)

    def get_tag(self, tag_name, default=None):
        # pylint: disable=missing-docstring
        if tag_name:
            if tag_name.startswith("[") and tag_name.endswith("]"):
                tag = next(
                    (elem.tag for elem in self.raw if elem.name == tag_name), None
                )
                value = self.raw.get(tag).value if tag else None
            else:
                value = self.raw.get(tag_name)
            if value:
                return str(value).strip("\x00")
        return default

    def get_manufacturer(self):
        """Safely get the manufacturer, all uppercase (could be multi-value)."""
        value = self.raw.get("Manufacturer")

        if not value:
            value = ""
        elif not isinstance(value, six.string_types):
            if isinstance(value, collections.Sequence):
                value = str(value[0])
            else:  # Unknown value, just convert to string
                value = str(value)

        return value.upper()

    @staticmethod
    def _is_screenshot(image_type):
        # pylint: disable=missing-docstring
        if image_type in [GEMS_TYPE_SCREENSHOT, GEMS_TYPE_VXTL]:
            return True
        return False

    @staticmethod
    def timestamp(date, time, timezone):
        # pylint: disable=missing-docstring
        if date and time and timezone:
            try:
                return util.localize_timestamp(
                    datetime.datetime.strptime(date + time[:6], "%Y%m%d%H%M%S"),
                    timezone,
                )
            except ValueError:
                return None
        return None

    @staticmethod
    def _parse_patient_name(name):
        """Parse patient name.

        expects "lastname" + "delimiter" + "firstname".

        Parameters
        ----------
        name : str
            string of subject first and last name, delimited by a '^' or ' '

        Returns
        -------
        firstname : str
            first name parsed from name
        lastname : str
            last name parsed from name

        """
        name = str(name)
        if "^" in name:
            lastname, _, firstname = name.partition("^")
        else:
            firstname, _, lastname = name.rpartition(" ")
        return firstname.strip().title(), lastname.strip().title()

    @staticmethod
    def _parse_patient_dob(dob):
        """Parse date string and sanity check.

        expects date string in YYYYMMDD format

        Parameters
        ----------
        dob : str
            dob as string YYYYMMDD

        Returns
        -------
        dob : datetime object

        """
        try:
            dob = datetime.datetime.strptime(dob, "%Y%m%d")
            if dob < datetime.datetime(1900, 1, 1):
                raise ValueError
        except (ValueError, TypeError):
            dob = None
        return dob


def global_ignore_unknown_tags():
    """Pass-through for function now handled directly in pydicom.

    See https://github.com/pydicom/pydicom/blob/3.0.X/src/pydicom/hooks.py#L181
    When this function was initially written, pydicom raised a KeyError if
    raw.tag.element != 0, but in newer versions of pydicom, a KeyError is
    only raised when config.settings.reading_validation_mode == config.RAISE,
    and otherwise sets VR to "UN" (which is what we want).
    """

    def reset():
        pass

    return reset


def set_vr_mismatch_callback():
    """Configure pydicom to handle raw elements where raw data element value
    cannot be translated with the raw data element's VR.
    """

    def handle_vr_mismatch(raw, data, **kwargs):
        # pylint: disable=unused-argument
        """Handle reading RawDataElements are translatable with their provided VRs.
        If not, re-attempt translation using some other translators.
        """
        vr = data["VR"]
        original_rvm = pydicom.config.settings.reading_validation_mode
        pydicom.config.settings.reading_validation_mode = 2
        if not raw.tag.is_private and pydicom.datadict.dictionary_has_tag(raw.tag):
            try:
                values.convert_value(vr, raw)
            except (TypeError, ValueError):
                raw = raw._replace(VR=dictionary_VR(raw.tag))
                data["VR"] = raw.VR
        pydicom.config.settings.reading_validation_mode = original_rvm

        raw_element_value(raw, data, **kwargs)

    _original_data_element_callback = hooks.raw_element_value

    def reset():
        """Reset the data_element_callback to the original value."""
        hooks.raw_element_value = _original_data_element_callback

    # Register as the data element callback
    hooks.register_callback("raw_element_value", handle_vr_mismatch)

    return reset


def stop_at_tag(tag):
    """Return stop_when function for given tag."""
    stop_tag = Tag(tag)  # type: ignore

    def stop_when(current_tag, VR, length):
        """Return True if the current tag equals the stop_tag."""
        return current_tag == stop_tag

    return stop_when


def _pixel_data(tag, VR, length):
    """Return True if the tag matches those usually containing pixel stream."""
    return tag in {
        0x7FE00008,
        0x7FE00009,
        0x7FE00010,
        0x00671018,
    }

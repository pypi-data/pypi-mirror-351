"""Send dicom and add tag."""

import logging
import sys
import typing as t
import warnings
from pathlib import Path

import backoff
from fw_file.dicom import DICOM, DICOMCollection
from pynetdicom.association import Association

from .dicom import get_association
from .parser import AEConfig

log = logging.getLogger(__name__)

# Pynetdicom logs normal c_store events as info, we only need warnings and
# errors
logging.getLogger("pynetdicom.events").setLevel(logging.WARNING)


class OutOfResources(Exception):
    """Exception to represent AE out of resources response."""

    pass  # pylint: disable=unnecessary-pass


def handle_warnings(
    warning_list: t.List[warnings.WarningMessage],
) -> t.Dict[t.Union[Warning, str], int]:
    """Find unique warnings and their counts from a list of warnings.

    Returns:
        Dictionary of warnings/str as key and int counts as value
    """
    warnings_dict: t.Dict[t.Union[Warning, str], int] = {}
    for warning in warning_list:
        msg = str(warning.message)
        _, _, msg_split = msg.partition("-")
        if msg_split:
            msg = msg_split
        if msg in warnings_dict:
            warnings_dict[msg] += 1
        else:
            warnings_dict[msg] = 1
    return warnings_dict


def run(  # pylint: disable=too-many-locals
    dcms: DICOMCollection,
    ae_config: AEConfig,
    group: str,
    identifier: str,
    tag_value: str,
) -> t.Tuple[int, int]:
    """Run tag and transmit for each DICOM file in the working directory.

    Args:
        ae_config(AEConfig): AE configuration object.
        group (str): The DICOM tag group to use when applying tag to DICOM file.
        identifier (str): The private tag creator name to use as identification.
        tag_value (str): The value to associate the private tag with.

    Returns:
        Tuple:
            - int: The number of DICOM files present
            - int: The number of DICOM files sent.

    """
    dicoms_sent = 0
    dicoms_present = 0
    try:
        association = get_association(ae_config, dcms)
    except RuntimeError as e:
        log.error(f"Cannot export dicoms, skipping {e.args}")
        log.debug("", exc_info=True)
        return len(dcms), dicoms_sent
    # Catch warnings during transmission and print summary instead of each as
    # it comes up.
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        for dcm in dcms:
            # If DICOM file, then proceed, otherwise, continue to next item in directory
            dicoms_present += 1
            dcm_path = Path(dcm.localpath)

            # Tag the DICOM file so it is not re-reaped
            add_private_tag(dcm, group, identifier, tag_value)
            dcm.save()

            # Check if the SOPClassUID is recognized
            sop_class_uid = dcm.get("SOPClassUID")
            sop_instance_uid = dcm.get("SOPInstanceUID")
            transfer_syntax = dcm.get("TransferSyntaxUID")
            msg = (
                f"Transmission of DICOM file {dcm_path.name} not attempted. "
                "Missing required tag(s): "
            )
            missing_tags = []
            if not sop_class_uid:
                missing_tags.append("SOPClassUID")
            if not sop_instance_uid:
                missing_tags.append("SOPInstanceUID")
            if not transfer_syntax:
                missing_tags.append("TransferSyntaxUID")
            if len(missing_tags) > 0:
                warnings.warn(f"{msg} {', '.join(missing_tags)}.")
                continue
            try:
                sent = transmit_dicom_file(dcm, association)
                dicoms_sent += int(sent)
            except (OutOfResources, ConnectionError, RuntimeError):
                log.error(
                    f"{dcm_path} Unable to transmit dicom due to a resources or connection error. "
                )
    unique_warnings = handle_warnings(w)
    for msg, count in unique_warnings.items():  # type: ignore
        log.error(f"{count} errors across dicoms: {msg}")
    return dicoms_present, dicoms_sent


@backoff.on_exception(
    backoff.expo, (OutOfResources, RuntimeError, ConnectionError), max_time=60
)
def transmit_dicom_file(  # pylint: disable=too-many-branches,too-many-return-statements
    dcm: DICOM,
    association: Association,
) -> bool:
    """Transmit DICOM file to an AE.

    Args:
        dicom (DICOM): Dicom file to be transmitted.
        ae (AE): Associated pynetdicom Application Entity

    Returns:
        (bool): Whether the DICOM file was transmitted successfully.

    Raises:
        TemporaryFailure: When there is a temporary failure.
            To be retried with backoff
    """
    f_name = dcm.filepath
    try:
        res = association.send_c_store(dcm.dataset.raw)
    except ValueError as e:
        log.error(e.args[0])
        return False
    if (0x0000, 0x0900) not in res:
        raise ConnectionError(f"{f_name}: Invalid response from server")
    status = int(res[(0x0000, 0x0900)].value)
    # Successes
    if status == 0x0000:
        log.debug(f"{f_name}: success")
        return True
    if status == 0xB000:
        log.warning(f"{f_name}: Coercion of data elements")
        return True
    if status == 0xB006:
        log.warning(f"{f_name}: Element discarded")
        return True
    if status == 0xB007:
        log.warning(f"{f_name}: Data set does not match SOP class")
        return True
    # failures
    if 0xA700 <= status <= 0xA7FF:
        # Temporary out of resources
        raise OutOfResources()
    err_msg = f"{f_name}: "
    if status == 0x0117:
        err_msg += "Invalid SOP instance"
    elif status == 0x0122:
        err_msg += "SOP class not supported"
    elif status == 0x0124:
        err_msg += "Not authorized"
    elif status == 0x0210:
        err_msg += "Duplicate invocation"
    elif status == 0x0211:
        err_msg += "Unrecognized operation"
    elif status == 0x0212:
        err_msg += "Mistyped argument"
    elif 0xA900 <= status <= 0xA9FF:
        err_msg += "Data set does not match SOP class"
    elif 0xC000 <= status <= 0xCFFF:
        err_msg += "Cannot understand"
    else:
        err_msg += "Unknown response code: {status}"
    log.error(err_msg)
    return False


def add_private_tag(
    dcm: DICOM,
    group_raw: t.Union[str, int] = "0x0021",
    identifier: str = "Flywheel",
    tag_value: str = "DICOM Send",
):
    """Add a private tag to a DICOM file.

    Args:
        dcm (DICOM): An fw-file DICOM object
        group_raw (str or int): The DICOM tag group to use when applying tag to
            DICOM file.
        identifier (str): The private tag creator name to use as identification.
        tag_value (str): The value to associate the private tag with.
    """
    private_tag = None
    if isinstance(group_raw, int):
        group = group_raw
    else:
        group = int(group_raw, 16)

    # Get private block with Private creator of given identifier in given group
    # Creating if not already exists.
    try:
        private_block = dcm.dataset.raw.private_block(group, identifier, create=True)
    except StopIteration:
        # Only raises when there are no more valid creator tags to be used in
        # this group.
        log.error(f"No free element in group '0x{group:04x}' to tag the DICOM file")
        sys.exit(1)
    assert private_block
    # Find first free
    for offset in range(0x00, 0xFF):
        private_tag = private_block.get_tag(offset)
        if not dcm.get(private_tag):
            # Found an element
            private_block.add_new(offset, "LO", tag_value)
            log.debug(f"Tag: {tag_value} added to DICOM file at {private_tag}")
            return
        if dcm.get(private_tag) == tag_value:
            warnings.warn(f"DICOM already tagged at {private_tag}, not duplicating")
            return

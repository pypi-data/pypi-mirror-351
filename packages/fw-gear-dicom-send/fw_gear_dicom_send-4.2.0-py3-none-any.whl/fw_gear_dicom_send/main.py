"""Functions to run dicom-send."""

import logging
import os
import shutil
import sys
import tarfile
import tempfile
import typing as t
import zipfile
from pathlib import Path

import backoff
from fw_core_client import CoreClient, ServerError
from fw_file.dicom import DICOM, DICOMCollection
from pydicom.datadict import tag_for_keyword
from pydicom.tag import Tag

from . import sender
from .dicom import release_association
from .parser import AEConfig

log = logging.getLogger(__name__)


# Tested in dicom-fixer
# TODO: This callback should go into fw-file and be imported.
def is_dcm(dcm: DICOM) -> bool:  # pragma: no cover
    """Look at a potential dicom and see whether it actually is a dicom.

    Args:
        dcm (DICOM): DICOM

    Returns:
        bool: True if it probably is a dicom, False if not
    """
    num_pub_tags = 0
    keys = dcm.dir()
    for key in keys:
        try:
            if Tag(tag_for_keyword(key)).group > 2:  # type: ignore
                num_pub_tags += 1
        except (AttributeError, TypeError):
            continue
    # Require two public tags outside the file_meta group.
    if num_pub_tags > 1:
        return True
    log.debug(f"Removing: {dcm}. Not a DICOM")
    return False


def get_dicom_collection(infile) -> DICOMCollection:
    """Get DICOMCollection from input file.

        The input can be a zip archive (.zip), a compressed tar archive (.tgz), or a
        single DICOM file.

    Args:
        infile (pathlib.PosixPath): The absolute path to the input file.

    Returns:
        DICOMCollection: The DICOMCollection object.
    """
    work_dir = Path(tempfile.mkdtemp())
    if zipfile.is_zipfile(infile):
        log.debug(f"Found input zipfile {infile}, unzipping")
        try:
            with zipfile.ZipFile(infile, "r") as zip_obj:
                size = sum([zipinfo.file_size for zipinfo in zip_obj.filelist])
                if size == 0:
                    log.error(f"Input zip {infile} is empty. Exiting.")
                    sys.exit(1)
                zip_obj.extractall(work_dir)
        except zipfile.BadZipFile:
            log.exception("Input looks like a zip but is not valid")
            sys.exit(1)
    elif tarfile.is_tarfile(infile):
        log.debug(f"Found input tarfile {infile}, untarring")
        try:
            with tarfile.open(infile, "r") as tar_obj:
                size = sum([tarinfo.size for tarinfo in tar_obj.getmembers()])
                if size == 0:
                    log.error(f"Input tar {infile} is empty. Exiting.")
                    sys.exit(1)
                tar_obj.extractall(work_dir)
        except tarfile.ReadError:
            log.exception("Input looks like a tar but is not valid")
            sys.exit(1)
    else:
        log.debug(f"Establishing input as single DICOM file: {infile}")
        # If this doesn't exist, will raise FileNotFound exception anyway
        shutil.move(infile, work_dir / infile.name)
    dcms = DICOMCollection.from_dir(work_dir, filter_fn=is_dcm, force=True)
    # Needed to trigger cleanup of temp `work_dir` on __del__
    dcms.is_tmp = True
    return dcms


def get_retry_time() -> int:  # pragma: no cover
    """Helper function to return retry time from env."""
    return int(os.getenv("FW_DOWNLOAD_RETRY_TIME", "60"))


@backoff.on_exception(backoff.expo, ServerError, max_time=get_retry_time)
def download_file(fw: CoreClient, acq_id: str, file_name: str, dest: Path):
    """Download file from acquisition with retry on ServerError."""
    resp = fw.get(f"/acquisitions/{acq_id}/files/{file_name}", stream=True)
    with open(dest, "wb") as fp:
        fp.write(resp.content)


# pylint: disable=protected-access,too-many-arguments,too-many-locals
def dicom_send_container(
    client: CoreClient,
    container_type: str,
    container_id: str,
    ae_config: AEConfig,
    group="0x0021",
    identifier="Flywheel",
    tag_value="DICOM Send",
) -> t.Tuple[t.List[dict], int, int]:
    """Download files in the session where the file type is DICOM.

    Args:
        client (CoreClient): API client
        container_type (str): The container type from a Flywheel instance from which to
            download files.
        container_id (str): The container ID from a Flywheel instance from which to
            download files.
        ae_config (AEConfig): AE configuration object.
        group (str): The DICOM tag group to use when applying tag to DICOM file.
        identifier (str): The private tag creator name to use as identification.
        tag_value (str): The value to associate the private tag with.

    Returns:
        tuple:
            entries (List[dict]): List of dictionary entries for report on each
                file.
            dcms_present (int): The number of DICOM files for which
                transmission was attempted.
            dcms_sent (int): The number of DICOM files senderted.

    """
    log.info(f"Downloading DICOM files from {container_type} ({container_id}).")
    dcms_sent = 0
    dcms_present = 0
    sub = None
    ses = None

    features = client.headers.get("X-Accept-Feature", "").split(",")
    # For subject/session we don't need attached files so we can also exclude files.
    no_files = {"X-Accept-Feature": ",".join([*features, "Exclude-Files"])}

    if container_type == "subject":
        sessions = client.get(
            f"/api/subjects/{container_id}/sessions", headers=no_files
        )
        acquisitions = []
        for sess in sessions:
            log.debug(f"Downloading dicoms from session {sess._id}")
            acqs = client.get(f"/api/sessions/{sess._id}/acquisitions")
            acquisitions.extend(acqs)
        sub = client.get(f"/api/subjects/{container_id}", headers=no_files)
    elif container_type == "session":
        acquisitions = client.get(f"/api/sessions/{container_id}/acquisitions")
        ses = client.get(f"/api/sessions/{container_id}", headers=no_files)
        sub = client.get(f"/api/subjects/{ses.parents.subject}", headers=no_files)
    elif container_type == "acquisition":
        acquisitions = [client.get(f"/api/acquisitions/{container_id}")]
        ses = client.get(
            f"/api/sessions/{acquisitions[0].parents.session}", headers=no_files
        )
        sub = client.get(f"/api/subjects/{ses.parents.subject}", headers=no_files)
    proj = client.get(f"/api/projects/{sub.parents.project}", headers=no_files)
    fw_group = sub.parents.group

    num_acqs = len(acquisitions)
    log.info(f"Found {num_acqs} acquisitions.")
    entries: t.List[dict] = []

    for acq in acquisitions:
        sub = (
            sub
            if sub
            else client.get(f"/api/subjects/{acq.parents.subject}", headers=no_files)
        )
        ses = (
            ses
            if ses
            else client.get(f"/api/sessions/{acq.parents.session}", headers=no_files)
        )
        fw_path = f"{fw_group}/{proj.label}/{sub.label}/{ses.label}"

        files = [file_ for file_ in acq.get("files") if file_.type == "dicom"]
        log.info(f"{'-'*5} Acquisition: {acq.label} ({len(files)} files) {'-'*5}")
        for file in files:
            with tempfile.TemporaryDirectory() as tmpdir:
                file_path = Path(f"{tmpdir}/{file.name}")
                download_file(client, acq._id, file.name, file_path)
                dcms = get_dicom_collection(file_path)
                log.info(f"{file_path.name}: Sending {len(dcms)} dicoms.")
                present, sent = dicom_send(
                    dcms,
                    ae_config,
                    group,
                    identifier,
                    tag_value,
                )
                entries.append(
                    {
                        "path": f"{fw_path}/{acq.label}/{file_path.name}",
                        "acq_id": acq._id,
                        "file_name": file_path.name,
                        "present": present,
                        "sent": sent,
                    }
                )
                dcms_sent += sent
                dcms_present += present
                log.info(f"{file_path.name}: {sent}/{present} dicoms sent.")

    release_association()
    return entries, dcms_present, dcms_sent


# pylint: enable=protected-access,too-many-arguments,too-many-locals


def dicom_send_file(  # pylint: disable=too-many-arguments,too-many-locals
    client: CoreClient,
    infile: Path,
    ae_config: AEConfig,
    parent_acq: str,
    group="0x0021",
    identifier="Flywheel",
    tag_value="DICOM Send",
) -> t.Tuple[t.List[dict], int, int]:
    """Send a singular dicom file from input.

    Args:
        client (CoreClient): API client
        infile (Path): Input file.
        ae_config (AEConfig): AE configuration object.
        group (str): The DICOM tag group to use when applying tag to DICOM file.
        identifier (str): The private tag creator name to use as identification.
        tag_value (str): The value to associate the private tag with.

    Returns:
        tuple:
            entries (List[dict]): List of dictionary entries for report on each
                file.
            dcms_present (int): The number of DICOM files for which
                transmission was attempted.
            dcms_sent (int): The number of DICOM files senderted.

    """
    dcms = get_dicom_collection(infile)
    log.info(f"{infile.name}: Sending {len(dcms)} dicoms.")
    present, sent = dicom_send(
        dcms,
        ae_config,
        group,
        identifier,
        tag_value,
    )
    log.info(f"{infile.name}: {sent}/{present} dicoms sent.")
    acq = client.get(f"/api/acquisitions/{parent_acq}")
    ses = client.get(f"/api/sessions/{acq.parents.session}")
    sub = client.get(f"/api/subjects/{acq.parents.subject}")
    proj = client.get(f"/api/projects/{acq.parents.project}")
    fw_group = acq.parents.group

    fw_path = (
        f"{fw_group}/{proj.label}/{sub.label}/{ses.label}/{acq.label}/{infile.name}"
    )
    log.info("Flywheel Path\n")
    log.info(fw_path)
    entries = [
        {
            "path": fw_path,
            "acq_id": parent_acq,
            "file_name": infile.name,
            "present": present,
            "sent": sent,
        }
    ]
    release_association()
    return entries, present, sent


def dicom_send(  # pylint: disable=too-many-arguments
    dcms: DICOMCollection,
    ae_config: AEConfig,
    group="0x0021",
    identifier="Flywheel",
    tag_value="DICOM Send",
) -> t.Tuple[int, int]:
    """Run dicom-send, including tagging each DICOM file and sending.

    Args:
        dcms (DICOMCollection): DICOMs to send.
        ae_config (AEConfig): AE configuration object.
        group (str): The DICOM tag group to use when applying tag to DICOM file.
        identifier (str): The private tag creator name to use as identification.
        tag_value (str): The value to associate the private tag with.

    Returns:
        tuple:
            dcms_present (int): The number of DICOM files for which
                transmission was attempted.
            dcms_sent (int): The number of DICOM files sent.

    """
    dcms_present, dcms_sent = sender.run(
        dcms,
        ae_config,
        group=group,
        identifier=identifier,
        tag_value=tag_value,
    )
    return dcms_present, dcms_sent

import json
import logging
import re
import typing as t
from csv import DictWriter, reader
from datetime import datetime
from pathlib import Path

from fw_core_client import ClientError, CoreClient, ServerError
from fw_utils import pluralize
from pathvalidate import sanitize_filename

log = logging.getLogger(__name__)


def print_report(report_file: Path):
    """Print the current report to the log.

    Args:
        report_file (Path): the .csv file to print
    """

    # This gets the lengths of each element in each row/col.  These lengths are then
    # used to format the printed output so that it's human readable.
    with open(report_file, "r", newline="", encoding="utf-8") as read_obj:
        csv_f = reader(read_obj)
        lens = [[len(i) for i in row] for row in csv_f]

    max_lens = [max(idx) for idx in zip(*lens)]
    # 4 spaces are added between columns (1/2 a standard tab)
    format_string_grps = ["{:<" + str(ml + 4) + "}" for ml in max_lens]
    format_string = " ".join(format_string_grps) + "\n"

    with open(report_file, "r", newline="", encoding="utf-8") as read_obj:
        csv_f = reader(read_obj)
        print_string = "REPORT_SUMMARY:\n"
        for row in csv_f:
            print_string += format_string.format(*row)

        log.info(print_string)


def get_sanitized_filename(filepath: Path) -> Path:
    """Clean filename.

    Remove characters that are not alphanumeric, '.', '-', or '_' from an input
    string. Asterisk following "t2" + optional space/underscore  will be replaced
    with "star"
    """
    filename = str(filepath)
    filename = re.sub(r"(t2 ?_?)\*", r"\1star", filename, flags=re.IGNORECASE)
    sanitized_filename = sanitize_filename(filename)
    if filename != sanitized_filename:
        log.info(f"Renaming {filename} to {sanitized_filename}")

    return Path(sanitized_filename)


def upload_report(  # pylint: disable=too-many-locals,too-many-arguments
    client: CoreClient,
    entries: t.List[dict],
    directory: Path,
    cont_type: str,
    cont_id: str,
    acq_id: t.Optional[str] = None,
) -> bool:
    """Upload a report from the given entries.

    Names the report file based on the session and date.  If a single acquisition was
    specified for export, the acquisition label is included too.

    Args:
        client (CoreClient): Flywheel CoreClient
        entries (List[dict]): List of dictionary entries for each file
        directory (Path): Directory to work with
        cont_type (str): the type of the parent container of the target file
        cont_id (str): the flywheel ID of the parent container of the target file
        acq_id (str): the flywheel ID of the parent acquisition of the target file
    """
    cont = client.get(f"/api/{pluralize(cont_type)}/{cont_id}")
    new_name = cont.label

    if cont_type != "acquisition" and acq_id:
        acq = client.get(f"/api/acquisitions/{acq_id}")
        new_name = f"{new_name}_{acq.label}"

    timestamp = datetime.now()

    new_name = (
        f"dicom-send_report-{new_name}_{timestamp.strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    )
    fieldnames = ["path", "acq_id", "file_name", "present", "sent"]
    safe_name = get_sanitized_filename(new_name)
    report = directory / safe_name
    with open(report, "w", encoding="utf-8") as fp:
        writer = DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        for entry in entries:
            writer.writerow(entry)

    signed_url = client.api_config.get("signed_url", False)  # type: ignore
    endpoint = f"/api/{pluralize(cont_type)}/{cont_id}/files"
    try:
        with open(report, "rb") as file:
            if signed_url:
                payload = {"filenames": [report.name], "metadata": {}}
                upload = json.loads(
                    client.post(
                        endpoint, params={"ticket": ""}, json=payload, stream=True
                    ).content
                )
                headers = {"Authorization": None, **upload.get("headers", {})}
                client.put(upload["urls"][report.name], headers=headers, data=file)
                _ = client.post(endpoint, params={"ticket": upload["ticket"]})
            else:
                client.post(endpoint, files=[("file", (report.name, file))])
        log.info(f"Report file {safe_name} uploaded to {cont_type} {cont.label}")
        print_report(report)
        return True
    except (ClientError, ServerError):
        log.error("Could not upload report", exc_info=True)
        return False

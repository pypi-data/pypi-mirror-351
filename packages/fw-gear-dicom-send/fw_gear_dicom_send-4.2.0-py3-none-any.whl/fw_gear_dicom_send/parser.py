"""Function to parse gear config into gear args."""

import dataclasses
import logging
import os
import ssl
import sys
import typing as t
from pathlib import Path

from flywheel_gear_toolkit import GearToolkitContext
from fw_core_client import ClientError, CoreClient

from . import __version__, pkg_name

log = logging.getLogger(__name__)


def get_client(key: str) -> CoreClient:  # pragma: no cover
    """Get CoreClient."""
    # NOTE: Not exposing timeouts/retries as config options, these seem
    # to be better default values.
    client = CoreClient(
        api_key=key,
        client_name=pkg_name,
        client_version=__version__,
        read_timeout=60,
        connect_timeout=15,
        retry_total=10,
    )

    # Exclude pulling analyses
    features = client.headers.get("X-Accept-Feature", "").split(",")
    if "Slim-Containers" not in features:
        features.append("Slim-Containers")
    client.headers["X-Accept-Feature"] = ",".join(features)
    return client


@dataclasses.dataclass
class TLSOpt:
    """TLS options needed for SSLContext."""

    enabled: bool = False
    key: t.Optional[Path] = None
    cert: t.Optional[Path] = None
    add_cert_file: t.Optional[Path] = None
    require_peer_cert: bool = True

    def get_ssl_context(self) -> ssl.SSLContext:
        """Create the SSLContext for client auth."""
        # NOTE: "Server Auth" means the purpose is to authenticate a server (as
        # a client) whereas "Client Auth" means the purpose is to authenticat
        # clients (as a server)
        ssl_ctx = ssl.create_default_context(
            ssl.Purpose.SERVER_AUTH, cafile=self.add_cert_file
        )
        ssl_ctx.verify_mode = (
            ssl.CERT_REQUIRED if self.require_peer_cert else ssl.CERT_OPTIONAL
        )
        # TODO: expose as config option
        ssl_ctx.check_hostname = False
        assert self.cert
        assert self.key
        ssl_ctx.load_cert_chain(certfile=self.cert, keyfile=self.key)
        return ssl_ctx

    def validate(self):
        """Validate TLS options."""
        if self.enabled:
            if not (
                (self.key and (self.key.exists() and self.key.is_file()))
                and (self.cert and (self.cert.exists() and self.cert.is_file()))
            ):
                raise ValueError("Need both a keyfile and certfile to enable TLS")


def parse_tls_opts(gear_context: GearToolkitContext) -> TLSOpt:
    """Parse TLS options from the GearToolkitContext."""
    opts = TLSOpt()
    cfg = gear_context.config
    for key in vars(opts).keys():
        key_name = f"tls_{key}"
        if key_name in cfg:
            val = cfg[key_name]
            setattr(opts, key, val)
    key = gear_context.get_input_path("key")
    cert = gear_context.get_input_path("cert")
    add_cert = gear_context.get_input_path("add_cert_file")
    if key:
        opts.key = Path(key)
    if cert:
        opts.cert = Path(cert)
    if add_cert:
        opts.add_cert_file = Path(add_cert)
    opts.validate()
    return opts


@dataclasses.dataclass
class AEConfig:
    """AE configuration."""

    called_ae: str
    port: int
    calling_ae: str
    destination: str
    tls: t.Optional[TLSOpt] = None


def parse_args(
    gear_context: GearToolkitContext,
) -> t.Tuple[CoreClient, AEConfig, dict, str, str, t.Optional[Path], t.Optional[str]]:
    """Generate gear arguments."""
    log.info("Preparing arguments for dicom-send gear.")
    ae_config = AEConfig(
        **{
            "called_ae": gear_context.config["called_ae"],
            "port": gear_context.config["port"],
            "calling_ae": gear_context.config["calling_ae"],
            "destination": gear_context.config["destination"],
        }
    )
    tag_kwargs = {
        "group": gear_context.config["group"],
        "identifier": gear_context.config["identifier"],
        "tag_value": gear_context.config["tag_value"],
    }
    os.environ["FW_DOWNLOAD_RETRY_TIME"] = str(
        int(gear_context.config.get("file_download_retry_time", 60))
    )
    report = gear_context.config.get("report", True)
    api_key = t.cast(str, gear_context.get_input("api-key")["key"])
    fw = get_client(api_key)
    container_id = ""
    container_type = ""
    parent_acq: t.Optional[str] = None
    infile = (
        Path(gear_context.get_input_path("file"))
        if gear_context.get_input_path("file")
        else None
    )
    # Input is a tgz or zip DICOM archive, or a single DICOM file
    if infile and (infile.exists() and infile.is_file()):
        log.info(
            f"Using input file {gear_context.get_input('file')['location']['name']}"
        )
        parent_acq = gear_context.get_input("file")["hierarchy"].get("id")
        # When a file is provided as input, destination ID is the acquisition ID
        try:
            container_id = fw.get(f"/api/acquisitions/{parent_acq}").parents.session
            container_type = "session"
        except ClientError:
            log.error(
                f"Parent acquisition ({parent_acq}) not found, "
                "can only run on acquisition file."
            )
    else:
        log.info(
            "No input provided. Will use files of type DICOM from parent container."
        )
        # Alternatively, if no input is provided, all DICOM files in the session are
        # downloaded and used as input
        # In this case the destination ID is the session ID.
        container_type = gear_context.destination["type"]
        container_id = gear_context.destination["id"]
        if container_type not in ["subject", "session", "acquisition"]:
            log.error(
                f"Unsupported container type {container_type}. "
                "Can only run on subject, session or acquisition."
            )
            sys.exit(1)
    try:
        tls_opts = parse_tls_opts(gear_context)
        ae_config.tls = tls_opts
    except ValueError as e:
        log.error(f"Could not parse TLS options: {e.args[0]}")
        log.debug("", exc_info=True)
        sys.exit(1)
    return (
        fw,
        ae_config,
        tag_kwargs,
        container_type,
        container_id,
        infile,
        parent_acq,
        report,
    )

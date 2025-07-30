"""DICOM protocol functions."""

# pylint: disable=global-statement
from __future__ import annotations
import logging
import typing as t
from pathlib import Path

from pydicom import Dataset

from fw_file.dicom import DICOMCollection
from pydicom.uid import ImplicitVRLittleEndian
from pynetdicom.ae import ApplicationEntity
from pynetdicom.association import Association
from pynetdicom.presentation import PresentationContext
import pynetdicom.events as evts

# pylint: disable=no-name-in-module
from pynetdicom.sop_class import Verification  # type: ignore

from .parser import AEConfig

# pylint: enable=no-name-in-module

log = logging.getLogger(__name__)
# Supress association messages
logging.getLogger("pynetdicom.assoc").setLevel(logging.WARNING)

# Global association object
glob_association: t.Optional[Association | RobustAssociation] = None


def get_application_entity(
    ae_config: AEConfig,
) -> ApplicationEntity:
    """Get the ApplicationEntity.

    Args:
        ae_config (AEConfig): ApplicationEntity configuration.

    Returns:
        ApplicationEntity: pynetdicom ApplicationEntity
    """

    # NOTE: ApplicationEntity does not accept timeouts in the constructor,
    # must add afterwards like here.
    entity = ApplicationEntity(ae_title=ae_config.calling_ae)
    # Default 60s, no need to expose as config option IMO,
    #  anything longer than 1 minute could timeout from any intermediate
    #  gateways, as 1 minute seems to be a common timeout.
    entity.acse_timeout = 60
    entity.dimse_timeout = 60
    entity.network_timeout = 60
    return entity


def get_presentation_contexts(
    dcms: DICOMCollection, verification: bool
) -> t.List[PresentationContext]:
    """Get PresentationContexts from a DICOMCollection.

    Args:
        dcms (DICOMCollection): DICOMS
        verification (bool): If true, add Verification presentation context.

    Returns:
        t.List[PresentationContext]: PresentationContexts
    """
    # PresentationContext sometimes add ImplicitVRLittleEndian as a transfer
    # since that is the default, but doesn't always seem to, so we'll make sure
    # it is explicitely added here.
    transfer_syntaxes = list(
        set([*dcms.bulk_get("TransferSyntaxUID"), ImplicitVRLittleEndian])
    )
    sop_classes = list(set(dcms.bulk_get("SOPClassUID")))
    if verification:
        sop_classes.append(Verification)
    if len(sop_classes) > 128:
        raise RuntimeError("Too many presentation contexts.")
    presentation_contexts: t.List[PresentationContext] = []
    for sop_class in sop_classes:
        pres = PresentationContext()
        pres.abstract_syntax = sop_class
        pres.transfer_syntax = transfer_syntaxes
        presentation_contexts.append(pres)
    return presentation_contexts


def get_association(
    ae_config: AEConfig,
    dcms: DICOMCollection,
) -> RobustAssociation:
    """Get association given AE and a collection of dicoms.

    Args:
        ae_config (AEConfig): ApplicationEntity configuration.
        dcms (DICOMCollection): Collection of dicoms to send.
            Needed to get correct presentation context.


    Raises:
        RuntimeError:
            - If too many presentation contexts.
            - If association fails.

    Returns:
        RobustAssociation: _description_
    """
    entity = get_application_entity(ae_config)
    presentation_contexts = get_presentation_contexts(
        dcms, verification=(ae_config.tls.enabled if ae_config.tls else False)
    )
    entity.requested_contexts = presentation_contexts

    if ae_config.tls and ae_config.tls.enabled:
        ctx = ae_config.tls.get_ssl_context()
        association = RobustAssociation(
            entity.associate(
                ae_config.destination,
                ae_config.port,
                ae_title=ae_config.called_ae,
                tls_args=(ctx, ae_config.destination),
            )
        )
    else:
        association = RobustAssociation(
            entity.associate(
                ae_config.destination, ae_config.port, ae_title=ae_config.called_ae
            )
        )
    if not association.is_established:
        raise RuntimeError("Failed to establish AE association.")
    log.info("Successfully associated AE")
    # Release existing association, and populate global association
    global glob_association
    if glob_association:
        glob_association.release()
    glob_association = association
    return association


def release_association() -> None:
    """Release association."""
    global glob_association
    if glob_association:
        glob_association.release()
        glob_association = None


class RobustAssociation:
    """Wrapper for pynetdicom Association that handles disconnections gracefully."""

    def __init__(self, association: Association) -> None:
        """Initialize with an association and bind disconnect event handlers."""
        self._assoc = association
        self._assoc.bind(evts.EVT_CONN_CLOSE, self._handle_disconnect)

    def release(self) -> None:
        """Release the association."""
        return self._assoc.release()

    def send_c_store(
        self,
        dataset: t.Union[str, Path, Dataset],
        msg_id: int = 1,
        priority: int = 2,
        originator_aet: t.Optional[str] = None,
        originator_id: t.Optional[int] = None,
    ):
        """Send C-STORE request, attempting reconnection if needed."""
        if not self.is_established:
            self.attempt_reconnect()

        return self._assoc.send_c_store(
            dataset,
            msg_id=msg_id,
            priority=priority,
            originator_aet=originator_aet,
            originator_id=originator_id,
        )

    def attempt_reconnect(self) -> None:
        """Attempt to reconnect if the association is not established."""
        if self.is_established:
            return

        log.info("Attempting to re-establish association")
        self._assoc.release()

        ae = self._assoc.ae
        assoc = ae.associate(
            self._assoc.acceptor.address,
            self._assoc.acceptor.port,
            ae_title=self._assoc.acceptor.ae_title,
        )

        if assoc.is_established:
            log.info("Successfully re-established the association")
            self._assoc = assoc
        else:
            log.error("Failed to re-establish the association")

    @property
    def is_established(self) -> bool:
        """Check if the underlying association is established."""
        return self._assoc.is_established

    def __getattr__(self, name: str) -> t.Any:
        """Delegate undefined attrs/methods to the underlying Association."""
        return getattr(self._assoc, name)

    def _handle_disconnect(self, event: evts.Event) -> None:
        """Callback for the event handler."""
        self.attempt_reconnect()

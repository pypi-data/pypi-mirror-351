# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information
"""Module dedicated to the handlers of COAR Notifications."""

from importlib.metadata import version
import json
from typing import Callable

from django.conf import settings

from swh.model.model import (
    MetadataAuthority,
    MetadataAuthorityType,
    MetadataFetcher,
    Origin,
    RawExtrinsicMetadata,
)
from swh.storage import get_storage

from .models import InboundNotification, Statuses
from .utils import create_accept_cn, reject, send_cn, to_sorted_tuple, unprocessable

CNHandler = Callable[[InboundNotification], None]


def get_handler(notification: InboundNotification) -> CNHandler | None:
    """Get a CN handler from its type.

    The list of handlers by type is defined in the ``handlers`` dict.

    Args:
        notification: an inbound CN

    Raises:
        UnprocessableException: no handler available for cn

    Returns:
        A COAR Notification handler if one matches
    """
    type_ = to_sorted_tuple(notification.payload["type"])
    try:
        return handlers[type_]
    except KeyError:
        error_message = f"Unable to process {', '.join(type_)} COAR Notifications"
        unprocessable(notification, error_message)
        return None


def mention(notification: InboundNotification) -> None:
    """Handle a mention COAR Notification.

    Validates the payload, sends the CN to the Raw Extrinsic Metadata storage and
    send an Accept CN.

    Args:
        cn: an inbound CN
    """

    # validate the payload and extract data or reject
    context_data = notification.payload["context"]  # describe the paper
    object_data = notification.payload["object"]  # describe the relationship

    paper_url = context_data["id"]
    if paper_url != object_data["as:subject"]:
        error_message = (
            f"Context id {paper_url} does not match "
            f"object as:subject {object_data['as:subject']}"
        )
        reject(notification, error_message)
        return

    context_type = to_sorted_tuple(context_data["type"])
    if "sorg:AboutPage" not in context_type:
        error_message = "Context type does not contain sorg:AboutPage"
        reject(notification, error_message)
        return

    origin_url = object_data["as:object"]

    # Store the CN in the Raw Extrinsic Metadata storage
    storage = get_storage(**settings.SWH_CONF["storage"])
    metadata_fetcher = MetadataFetcher(
        name="swh-coarnotify", version=version("swh-coarnotify")
    )
    origin = Origin(origin_url)
    swhid = origin.swhid()
    metadata_authority = MetadataAuthority(
        type=MetadataAuthorityType.REGISTRY,
        url=notification.payload["origin"]["id"],
    )

    metadata_object = RawExtrinsicMetadata(
        target=swhid,
        discovery_date=notification.created_at,
        authority=metadata_authority,
        fetcher=metadata_fetcher,
        format="coarnotify-mention-v1",
        metadata=json.dumps(notification.payload).encode(),
    )

    storage.metadata_authority_add([metadata_authority])
    storage.metadata_fetcher_add([metadata_fetcher])
    storage.raw_extrinsic_metadata_add([metadata_object])

    # update cn and send a reply
    notification.status = Statuses.ACCEPTED
    notification.save()
    accepted_cn = create_accept_cn(notification, summary=f"Stored mention for {swhid}")
    send_cn(accepted_cn)


handlers = {
    ("Announce", "RelationshipAction"): mention,
}

# Copyright (C) 2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU Affero General Public License version 3, or any later version
# See top-level LICENSE file for more information
import json

from swh.coarnotify.server.handlers import get_handler, mention
from swh.coarnotify.server.models import Statuses
from swh.model.model import MetadataAuthority, MetadataAuthorityType, Origin


def test_get_handler_unknown(inbound_notification):
    inbound_notification.payload["type"] = ["Unhandled"]
    assert get_handler(inbound_notification) is None
    assert inbound_notification.status == Statuses.UNPROCESSABLE


def test_get_handler_mention(inbound_notification):
    assert get_handler(inbound_notification) == mention


def test_mention_origin_url_context_data_id(inbound_notification):
    inbound_notification.payload["context"]["id"] = "https://wrong.url"
    assert (
        inbound_notification.payload["context"]["id"]
        != inbound_notification.payload["object"]["as:subject"]
    )

    mention(inbound_notification)

    assert inbound_notification.status == Statuses.REJECTED
    assert "does not match object as:subject" in inbound_notification.error_message


def test_mention_context_type(inbound_notification):
    inbound_notification.payload["context"]["type"] = ["sorg:Drawing"]

    mention(inbound_notification)

    assert inbound_notification.status == Statuses.REJECTED
    assert "does not contain sorg:AboutPage" in inbound_notification.error_message


def test_mention_storage(storage, inbound_notification, mocker):
    with mocker.patch(
        "swh.coarnotify.server.handlers.get_storage", return_value=storage
    ):
        mention(inbound_notification)

    origin = Origin(inbound_notification.payload["object"]["as:object"])
    swhid = origin.swhid()
    metadata_authority = MetadataAuthority(
        type=MetadataAuthorityType.REGISTRY,
        url=inbound_notification.payload["origin"]["id"],
    )
    extrinsic_metadata = storage.raw_extrinsic_metadata_get(
        target=swhid, authority=metadata_authority
    )
    assert len(extrinsic_metadata.results) == 1
    payload = extrinsic_metadata.results[0].metadata.decode()
    assert json.loads(payload) == inbound_notification.payload


def test_mention_reply(inbound_notification):
    mention(inbound_notification)

    assert inbound_notification.status == Statuses.ACCEPTED
    outbound_notification = inbound_notification.replied_by.first()
    origin = Origin(inbound_notification.payload["object"]["as:object"])
    swhid = origin.swhid()
    assert outbound_notification.payload["summary"] == f"Stored mention for {swhid}"

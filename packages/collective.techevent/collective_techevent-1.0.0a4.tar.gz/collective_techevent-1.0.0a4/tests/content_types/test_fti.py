from plone.dexterity.fti import DexterityFTI
from plone.dexterity.utils import resolveDottedName
from zope.component import createObject

import pytest


_BEHAVIORS_BY_CT = (
    (
        "Venue",
        [
            "plone.basic",
            "plone.namefromtitle",
            "plone.excludefromnavigation",
            "volto.preview_image_link",
            "plone.shortname",
            "volto.navtitle",
            "volto.blocks",
        ],
    ),
    (
        "Room",
        [
            "plone.basic",
            "plone.namefromtitle",
            "plone.excludefromnavigation",
            "volto.preview_image_link",
            "plone.shortname",
            "volto.navtitle",
            "volto.blocks",
        ],
    ),
    (
        "Presenter",
        [
            "plonegovbr.socialmedia.links",
            "plone.namefromtitle",
            "plone.categorization",
            "plone.excludefromnavigation",
            "plone.leadimage",
            "plone.shortname",
            "plone.richtext",
        ],
    ),
    (
        "Schedule",
        [
            "plone.basic",
            "volto.preview_image_link",
            "volto.navtitle",
            "volto.blocks",
            "plone.namefromtitle",
            "plone.excludefromnavigation",
            "plone.shortname",
        ],
    ),
    (
        "Break",
        [
            "plone.namefromtitle",
            "plone.categorization",
            "plone.excludefromnavigation",
            "collective.techevent.schedule",
            "plone.shortname",
            "volto.preview_image_link",
            "plone.basic",
        ],
    ),
    (
        "Keynote",
        [
            "plone.namefromtitle",
            "plone.categorization",
            "plone.excludefromnavigation",
            "collective.techevent.session",
            "collective.techevent.schedule",
            "volto.preview_image_link",
            "plone.shortname",
        ],
    ),
    (
        "Talk",
        [
            "plone.namefromtitle",
            "plone.categorization",
            "plone.excludefromnavigation",
            "collective.techevent.session",
            "collective.techevent.schedule",
            "volto.preview_image_link",
            "plone.shortname",
        ],
    ),
    (
        "Training",
        [
            "plone.namefromtitle",
            "plone.categorization",
            "plone.excludefromnavigation",
            "collective.techevent.session",
            "collective.techevent.schedule",
            "volto.preview_image_link",
            "plone.shortname",
        ],
    ),
    (
        "Slot",
        [
            "plone.namefromtitle",
            "plone.categorization",
            "plone.excludefromnavigation",
            "collective.techevent.schedule",
            "volto.preview_image_link",
            "plone.shortname",
        ],
    ),
    (
        "LightningTalks",
        [
            "plone.namefromtitle",
            "plone.categorization",
            "plone.excludefromnavigation",
            "collective.techevent.schedule",
            "volto.preview_image_link",
            "plone.shortname",
        ],
    ),
    (
        "OpenSpace",
        [
            "plone.namefromtitle",
            "plone.categorization",
            "plone.excludefromnavigation",
            "collective.techevent.schedule",
            "volto.preview_image_link",
            "plone.shortname",
        ],
    ),
    (
        "Meeting",
        [
            "plone.namefromtitle",
            "plone.categorization",
            "plone.excludefromnavigation",
            "collective.techevent.schedule",
            "volto.preview_image_link",
            "plone.shortname",
        ],
    ),
    (
        "SponsorsDB",
        [
            "plone.basic",
            "volto.preview_image_link",
            "volto.navtitle",
            "volto.blocks",
            "plone.namefromtitle",
            "plone.excludefromnavigation",
            "plone.shortname",
        ],
    ),
    (
        "SponsorLevel",
        [
            "plone.basic",
            "volto.preview_image_link",
            "volto.navtitle",
            "volto.blocks",
            "plone.namefromtitle",
            "plone.excludefromnavigation",
            "plone.shortname",
        ],
    ),
    (
        "Sponsor",
        [
            "plonegovbr.socialmedia.links",
            "plone.leadimage",
            "plone.namefromtitle",
            "plone.excludefromnavigation",
            "plone.shortname",
        ],
    ),
)


def behaviors_parameters() -> tuple[tuple[str, str], ...]:
    parameters = []
    for ct, behaviors in _BEHAVIORS_BY_CT:
        for behavior in behaviors:
            parameters.append((ct, behavior))
    return tuple(parameters)


@pytest.fixture(scope="class")
def portal(portal_class):
    yield portal_class


class TestContentTypeFTI:
    @pytest.fixture(autouse=True)
    def _setup(self, portal):
        self.portal = portal

    @pytest.mark.parametrize(
        "portal_type,attr,expected",
        [
            ("Venue", "title", "Venue"),
            ("Venue", "global_allow", True),
            ("Venue", "filter_content_types", True),
            ("Venue", "allowed_content_types", ("Document", "File", "Image", "Room")),
            ("Room", "title", "Room"),
            ("Room", "global_allow", False),
            ("Room", "filter_content_types", True),
            ("Room", "allowed_content_types", ("Document", "File", "Image")),
            ("Presenter", "title", "Presenter"),
            ("Presenter", "global_allow", True),
            ("Presenter", "filter_content_types", True),
            ("Presenter", "allowed_content_types", ("File", "Image")),
            ("Schedule", "title", "Schedule"),
            ("Schedule", "global_allow", True),
            ("Schedule", "filter_content_types", True),
            (
                "Schedule",
                "allowed_content_types",
                (
                    "Document",
                    "File",
                    "Image",
                    "Break",
                    "Keynote",
                    "LightningTalks",
                    "Meeting",
                    "OpenSpace",
                    "Slot",
                    "Talk",
                    "Training",
                ),
            ),
            ("Break", "title", "Break"),
            ("Break", "global_allow", False),
            ("Break", "filter_content_types", True),
            ("Break", "allowed_content_types", ()),
            ("Keynote", "title", "Keynote"),
            ("Keynote", "global_allow", False),
            ("Keynote", "filter_content_types", True),
            ("Keynote", "allowed_content_types", ("File", "Image")),
            ("LightningTalks", "title", "Lightning Talks"),
            ("LightningTalks", "global_allow", False),
            ("LightningTalks", "filter_content_types", True),
            ("LightningTalks", "allowed_content_types", ("File", "Image")),
            ("Meeting", "title", "Meeting"),
            ("Meeting", "global_allow", False),
            ("Meeting", "filter_content_types", True),
            ("Meeting", "allowed_content_types", ("File", "Image")),
            ("OpenSpace", "title", "Open Space"),
            ("OpenSpace", "global_allow", False),
            ("OpenSpace", "filter_content_types", True),
            ("OpenSpace", "allowed_content_types", ("File", "Image")),
            ("Slot", "title", "Slot"),
            ("Slot", "global_allow", False),
            ("Slot", "filter_content_types", True),
            ("Slot", "allowed_content_types", ()),
            ("Talk", "title", "Talk"),
            ("Talk", "global_allow", False),
            ("Talk", "filter_content_types", True),
            ("Talk", "allowed_content_types", ("File", "Image")),
            ("Training", "title", "Training"),
            ("Training", "global_allow", False),
            ("Training", "filter_content_types", True),
            ("Training", "allowed_content_types", ("File", "Image")),
            ("SponsorsDB", "title", "Sponsors Database"),
            ("SponsorsDB", "global_allow", True),
            ("SponsorsDB", "filter_content_types", True),
            (
                "SponsorsDB",
                "allowed_content_types",
                ("Document", "File", "Image", "SponsorLevel"),
            ),
            ("SponsorLevel", "title", "Sponsorship Level"),
            ("SponsorLevel", "global_allow", False),
            ("SponsorLevel", "filter_content_types", True),
            ("SponsorLevel", "allowed_content_types", ("File", "Image", "Sponsor")),
            ("Sponsor", "title", "Sponsor"),
            ("Sponsor", "global_allow", False),
            ("Sponsor", "filter_content_types", True),
            ("Sponsor", "allowed_content_types", ()),
        ],
    )
    def test_fti(self, get_fti, portal_type: str, attr: str, expected):
        """Test FTI values."""
        fti: DexterityFTI = get_fti(portal_type)

        assert isinstance(fti, DexterityFTI)
        assert getattr(fti, attr) == expected

    @pytest.mark.parametrize(
        "portal_type",
        [
            "Break",
            "Keynote",
            "LightningTalks",
            "Meeting",
            "OpenSpace",
            "Presenter",
            "Room",
            "Schedule",
            "Slot",
            "Sponsor",
            "SponsorLevel",
            "SponsorsDB",
            "Talk",
            "Tech Event",
            "Training",
            "Venue",
        ],
    )
    def test_factory(self, get_fti, portal_type: str):
        fti = get_fti(portal_type)
        factory = fti.factory
        klass = resolveDottedName(fti.klass)
        obj = createObject(factory)
        assert obj is not None
        assert isinstance(obj, klass)
        assert obj.portal_type == portal_type

    @pytest.mark.parametrize(
        "portal_type,behavior",
        behaviors_parameters(),
    )
    def test_behavior_present(self, get_fti, portal_type: str, behavior: str):
        behaviors = get_fti(portal_type).behaviors
        assert behavior in behaviors

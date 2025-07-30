import pytest

from pptxlib.app import App, is_powerpoint_available
from pptxlib.presentation import Presentations

pytestmark = pytest.mark.skipif(
    not is_powerpoint_available(),
    reason="PowerPoint is not available",
)


def test_repr(app: App):
    assert repr(app) == "<App>"


def test_presentations(app: App):
    presentations = app.presentations
    assert isinstance(presentations, Presentations)

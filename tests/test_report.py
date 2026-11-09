from __future__ import annotations

from core.report import NOCHK_WARNING, build_html_report


def test_report_html_escapes_markup_and_has_nochk_warning() -> None:
    html = build_html_report("<script>unsafe</script>\n" + NOCHK_WARNING)
    assert "&lt;script&gt;" in html
    assert NOCHK_WARNING in html

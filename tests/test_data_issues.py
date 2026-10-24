import re

from playwright.sync_api import Page, expect

START_URL = "http://localhost:8080/index.html"


def open_data_issues(page: Page):
    """Start at the assessment entry page and open the Data Issues grid."""
    page.goto(START_URL)
    page.get_by_role("button", name="Got it").click()

    container = page.frame_locator("#outerFrame")
    expect(container.locator("#spinnerOverlay")).to_have_class(re.compile(r"\bhidden\b"))

    app = container.frame_locator("#appFrame")
    app.get_by_role("button", name="Review & Fix Issues").click()
    cards = app.locator("#issueCardsContainer .issue-card")
    expect(cards).to_have_count(10)
    return app, cards


def original_row_cells(card):
    return [
        text.strip()
        for text in card.locator('tr[data-row-type="original"] td').all_inner_texts()
    ]


def sfid_from_original_row(card):
    headers = [text.strip() for text in card.locator("thead th").all_inner_texts()]
    cells = original_row_cells(card)
    sfid_index = next(
        (
            index
            for index, header in enumerate(headers)
            if header.split("\n", 1)[0].strip().lower() == "sfid"
        ),
        None,
    )
    if sfid_index is None:
        raise AssertionError(f"sfid column not found in headers: {headers}")
    return cells, cells[sfid_index]


def test_navigate_to_data_issues_grid(page: Page):
    _, cards = open_data_issues(page)
    expect(cards).to_have_count(10)


def test_original_rows_have_non_empty_sfid(page: Page):
    _, cards = open_data_issues(page)
    extracted = [sfid_from_original_row(card) for card in cards.all()]

    assert len(extracted) == 10
    for index, (cells, sfid) in enumerate(extracted, start=1):
        assert sfid, f"card {index} original row has an empty sfid: {cells}"


def test_seventh_card_original_value_updates_final_row(page: Page):
    _, cards = open_data_issues(page)
    card = cards.nth(6)
    original = card.locator(
        'tr[data-row-type="original"] .cell-radio span'
    ).inner_text().strip()

    card.locator('tr[data-row-type="original"] input[type="radio"]').check()

    final_value = card.locator('tr[data-row-type="final"] .cell-editable span')
    expect(final_value).to_have_text(original)


def test_edit_final_row_for_known_sfid(page: Page):
    app, _ = open_data_issues(page)
    card = app.locator('[data-record-id="00Qak00000RHtuzEAD"]')
    cell = card.locator('tr[data-row-type="final"] .cell-editable')
    cell.click()

    editor = cell.locator("input")
    expect(editor).to_be_visible()
    editor.fill("")
    editor.press_sequentially("123 Test Street")
    editor.press("Enter")

    expect(cell.locator("span")).to_have_text("123 Test Street")


def test_checkbox_selection_counter(page: Page):
    app, cards = open_data_issues(page)
    for position in (0, 2, 4):
        cards.nth(position).locator(".issue-checkbox").check()

    counter = app.locator("#confirmBar")
    expect(counter).to_contain_text("3 issue(s) selected")

    app.locator("#selectAll").check()
    expect(counter).to_contain_text("10 issue(s) selected")

    app.locator("#selectAll").uncheck()
    expect(counter).to_be_hidden()

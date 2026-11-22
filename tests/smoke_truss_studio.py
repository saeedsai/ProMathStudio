"""Backwards-compatible truss studio: original SI reference values, CSV export and UI.
The upgraded page uses an editable table UI but retains the prior solver interface."""
from pathlib import Path
import csv
import io
import json
import math
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'tools' / 'truss-studio.html').read_text(encoding='utf-8')
HTML = HTML.replace('<script defer src="truss-fem.js"></script>', '')
HTML = HTML.replace('<script defer src="truss-fem-ui.js"></script>', '')
HTML = HTML.replace('</body>', '<script>' + (ROOT / 'tools' / 'truss-fem.js').read_text(encoding='utf-8') + '</script>'
                    + '<script>' + (ROOT / 'tools' / 'truss-fem-ui.js').read_text(encoding='utf-8') + '</script></body>')



def assert_section_preview_metadata(page, selector, width_mm, height_mm, area_mm2,
                                    centroid_x_mm, centroid_y_mm, centroidal_axes=True,
                                    dimension_labels=('B', 'H')):
    svg = page.locator('#section-sketch')
    outline = svg.locator(selector)
    assert outline.count() == 1, selector
    expected = {
        'data-section-width-mm': width_mm,
        'data-section-height-mm': height_mm,
        'data-section-area-mm2': area_mm2,
        'data-section-centroid-x-mm': centroid_x_mm,
        'data-section-centroid-y-mm': centroid_y_mm,
    }
    for attribute, value in expected.items():
        actual = outline.get_attribute(attribute)
        assert actual is not None, (selector, attribute)
        assert math.isclose(float(actual), value, rel_tol=1e-10, abs_tol=1e-8), (selector, attribute, actual, value)
    marker = svg.locator('circle[data-centroid]')
    assert marker.count() == 1
    for attribute, value in (('data-centroid-x-mm', centroid_x_mm), ('data-centroid-y-mm', centroid_y_mm)):
        actual = marker.get_attribute(attribute)
        assert actual is not None
        assert math.isclose(float(actual), value, rel_tol=1e-10, abs_tol=1e-8), (attribute, actual, value)
    axis_selector = 'line[data-centroid-axis]' if centroidal_axes else 'line[data-principal-axis]'
    axes = svg.locator(axis_selector).evaluate_all(
        "(nodes) => nodes.map(node => ({x:Number(node.getAttribute('data-centroid-x-mm')), y:Number(node.getAttribute('data-centroid-y-mm'))}))"
    )
    assert len(axes) == 2, (selector, axes)
    for axis in axes:
        assert math.isclose(axis['x'], centroid_x_mm, rel_tol=1e-10, abs_tol=1e-8), (selector, axis)
        assert math.isclose(axis['y'], centroid_y_mm, rel_tol=1e-10, abs_tol=1e-8), (selector, axis)
    assert svg.locator('title').text_content()
    assert svg.locator('desc').text_content()
    caption = page.locator('#section-sketch-caption').inner_text()
    assert caption and svg.get_attribute('aria-label') == caption
    dimensions = svg.locator('text[data-dimension-label]').evaluate_all(
        "(nodes) => nodes.map(node => ({name:node.getAttribute('data-dimension-label'), text:node.textContent, accessible:node.getAttribute('aria-label'), role:node.getAttribute('role')}))"
    )
    assert len(dimensions) == len(dimension_labels), (selector, dimensions, dimension_labels)
    assert {item['name'] for item in dimensions} == set(dimension_labels), (selector, dimensions, dimension_labels)
    for item in dimensions:
        assert item['role'] == 'text', (selector, item)
        assert item['text'].startswith(item['name'] + '='), (selector, item)
        value_text = item['text'].split('=', 1)[1]
        assert value_text.endswith(' mm'), (selector, item)
        assert item['accessible'] == f"Section dimension {item['name']}: {value_text[:-3]} millimetres", (selector, item)
    if centroidal_axes:
        for visible, accessible in (
            ('Ixx', 'Horizontal centroidal axis Ixx'),
            ('Iyy', 'Vertical centroidal axis Iyy'),
        ):
            label = svg.locator(f'text[aria-label="{accessible}"]')
            assert label.count() == 1
            assert label.text_content() == visible
            assert label.get_attribute('role') == 'text'
    assert page.evaluate("() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1")


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 390, 'height': 844})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.set_content(HTML, wait_until='load')
        assert 'Analysis complete' in page.locator('#status').inner_text()
        # Preview valid geometry without solving, including a model that is structurally unstable.
        assert page.locator('#preview-summary').get_attribute('aria-live') == 'polite'
        page.locator('#member-material-details > summary').click()
        support_y = page.locator('#nodes tr').nth(1).locator('input[data-field="fixY"]')
        support_y.focus()
        page.keyboard.press('Space')
        preview = page.locator('#preview-summary').inner_text()
        for expected in ('3 joints', '3 members', '1 connected component', '0 isolated joints',
                         'total member length 11.21 m', 'axial member volume Σ(L·A) 0.01345 m³',
                         'bounds 4 × 3 m', 'applied load', 'ΣFy -20 kN', 'not a stability check'):
            assert expected in preview, (expected, preview)
        member_rows = page.locator('#member-metrics tr')
        assert member_rows.count() == 3
        assert [member_rows.nth(0).locator('td').nth(i).inner_text() for i in range(6)] == ['AB','A','B','4','1200','0.0048']
        assert [member_rows.nth(1).locator('td').nth(i).inner_text() for i in range(6)] == ['AC','A','C','3.606','1200','0.004327']
        assert [member_rows.nth(2).locator('td').nth(i).inner_text() for i in range(6)] == ['BC','B','C','3.606','1200','0.004327']
        assert page.locator('#plot line[data-member-id]').count() == 3
        assert page.locator('#plot circle[data-node-id]').count() == 3
        assert 'Preview ready' in page.locator('#status').inner_text()
        assert page.locator('#status.error').count() == 0
        # Section helpers calculate solid-section area and centroidal I for the selected member only.
        assert page.locator('#section-member option').count() == 3
        page.locator('#section-member').select_option('AB')
        page.locator('#section-shape').select_option('rectangle')
        page.locator('#section-width').fill('40')
        page.locator('#section-height').fill('60')
        assert_section_preview_metadata(page, 'path[data-section-outline="rectangle"]', 40, 60, 2400, 20, 30, dimension_labels=('B', 'H'))
        page.locator('#section-properties-apply').click()
        ab_area = page.locator('#members tr').nth(0).locator('input[data-field="area"]')
        ab_i = page.locator('#members tr').nth(0).locator('input[data-field="I"]')
        assert ab_area.input_value() == '2400'
        assert ab_i.input_value() == '720000'
        section_text = page.locator('#section-result').inner_text()
        for expected in ('Sx 24000 mm³', 'Sy 16000 mm³', 'rx 17.321 mm', 'ry 11.547 mm', 'cX 30 mm', 'cY 20 mm'):
            assert expected in section_text, (expected, section_text)
        assert page.locator('#member-metrics tr').nth(0).locator('td').nth(4).inner_text() == '2400'
        assert page.locator('#member-metrics tr').nth(0).locator('td').nth(10).inner_text() == '720000'
        assert 'Preview ready' in page.locator('#status').inner_text()
        assert page.locator('#member-metrics tr').nth(0).locator('td').nth(12).inner_text() == '—'
        # A solid circle uses its centroidal diameter axis and does not change another member.
        page.locator('#section-member').select_option('AC')
        page.locator('#section-shape').select_option('solid-circle')
        assert page.locator('#section-diameter-control').is_visible()
        page.locator('#section-diameter').fill('40')
        assert_section_preview_metadata(page, 'circle[data-section-outline="solid-circle"]', 40, 40, 400 * math.pi, 20, 20, dimension_labels=('D',))
        # Solid-circle preview reuses the canonical centroid and shows both perpendicular diameter axes.
        assert page.locator('#section-sketch-control').is_visible()
        assert page.locator('#section-sketch circle[data-section-outline="solid-circle"]').count() == 1
        assert page.locator('#section-sketch circle[data-centroid]').count() == 1
        assert page.locator('#section-sketch line[data-centroid-axis="horizontal"]').count() == 1
        assert page.locator('#section-sketch line[data-centroid-axis="vertical"]').count() == 1
        for expected in ('D=40 mm', 'Ixx', 'Iyy'):
            assert expected in page.locator('#section-sketch').text_content(), expected
        circle_caption = page.locator('#section-sketch-caption').inner_text()
        assert 'centroid x 20 mm, y 20 mm' in circle_caption, circle_caption
        assert page.locator('#section-sketch').get_attribute('aria-label') == circle_caption
        page.locator('#section-diameter').fill('60')
        assert 'D=60 mm' in page.locator('#section-sketch-caption').inner_text()
        assert 'centroid x 30 mm, y 30 mm' in page.locator('#section-sketch-caption').inner_text()
        page.locator('#section-diameter').fill('0')
        assert page.locator('#section-sketch circle[data-section-outline="solid-circle"]').count() == 0
        circle_invalid = page.locator('#section-sketch-caption').inner_text()
        assert circle_invalid.startswith('Preview unavailable: enter a positive finite outer diameter D')
        assert page.locator('#section-sketch').get_attribute('aria-label') == circle_invalid
        page.locator('#section-diameter').fill('40')
        assert page.locator('#section-sketch circle[data-section-outline="solid-circle"]').count() == 1
        page.locator('#section-properties-apply').click()
        ac_area = page.locator('#members tr').nth(1).locator('input[data-field="area"]')
        ac_i = page.locator('#members tr').nth(1).locator('input[data-field="I"]')
        assert abs(float(ac_area.input_value()) - 400 * math.pi) < 1e-9
        assert abs(float(ac_i.input_value()) - 40000 * math.pi) < 1e-8
        section_text = page.locator('#section-result').inner_text()
        for expected in ('Sx 6283.2 mm³', 'Sy 6283.2 mm³', 'rx 10 mm', 'ry 10 mm'):
            assert expected in section_text, (expected, section_text)
        assert page.locator('#members tr').nth(2).locator('input[data-field="area"]').input_value() == '1200'
        # A centered hollow rectangle reports both centroidal principal moments and applies the selected axis.
        page.locator('#section-member').select_option('AB')
        page.locator('#section-shape').select_option('hollow-rectangle')
        assert page.locator('#section-inner-width-control').is_visible()
        assert page.locator('#section-inner-height-control').is_visible()
        assert page.locator('#section-axis-control').is_visible()
        page.locator('#section-width').fill('100')
        page.locator('#section-height').fill('80')
        page.locator('#section-inner-width').fill('80')
        page.locator('#section-inner-height').fill('60')
        assert_section_preview_metadata(page, 'path[data-section-outline="hollow-rectangle-outer"]', 100, 80, 3200, 50, 40, dimension_labels=('B', 'H', 'bi', 'hi'))
        page.locator('#section-axis').select_option('depth')
        # Hollow-rectangle preview uses the canonical centered void and exposes all four dimensions.
        assert page.locator('#section-sketch-control').is_visible()
        assert page.locator('#section-sketch path[data-section-outline="hollow-rectangle-outer"]').count() == 1
        assert page.locator('#section-sketch path[data-section-outline="hollow-rectangle-inner"]').count() == 1
        assert page.locator('#section-sketch circle[data-centroid]').count() == 1
        assert page.locator('#section-sketch line[data-centroid-axis="horizontal"]').count() == 1
        assert page.locator('#section-sketch line[data-centroid-axis="vertical"]').count() == 1
        for expected in ('B=100 mm', 'H=80 mm', 'bi=80 mm', 'hi=60 mm', 'Ixx', 'Iyy'):
            assert expected in page.locator('#section-sketch').text_content(), expected
        hollow_rectangle_caption = page.locator('#section-sketch-caption').inner_text()
        assert 'centroid x 50 mm, y 40 mm' in hollow_rectangle_caption, hollow_rectangle_caption
        assert page.locator('#section-sketch').get_attribute('aria-label') == hollow_rectangle_caption
        inner_outline = page.locator('#section-sketch path[data-section-outline="hollow-rectangle-inner"]')
        assert inner_outline.get_attribute('data-inner-width-mm') == '80'
        assert inner_outline.get_attribute('data-inner-height-mm') == '60'
        assert inner_outline.get_attribute('fill') == 'rgba(127,127,127,.05)'
        assert page.locator('#section-sketch line[data-dimension="bi"]').count() == 1
        assert page.locator('#section-sketch line[data-dimension="hi"]').count() == 1
        page.locator('#section-inner-width').fill('70')
        assert 'bi=70 mm' in page.locator('#section-sketch-caption').inner_text()
        page.locator('#section-inner-width').fill('80')
        page.locator('#section-inner-height').fill('50')
        assert 'hi=50 mm' in page.locator('#section-sketch-caption').inner_text()
        page.locator('#section-inner-height').fill('60')
        page.locator('#section-inner-width').fill('100')
        assert page.locator('#section-sketch path[data-section-outline^="hollow-rectangle-"]').count() == 0
        invalid_hollow_rectangle = page.locator('#section-sketch-caption').inner_text()
        assert invalid_hollow_rectangle.startswith('Preview unavailable: inner width bi and inner depth hi')
        assert page.locator('#section-sketch').get_attribute('aria-label') == invalid_hollow_rectangle
        page.locator('#section-inner-width').fill('80')
        assert page.locator('#section-sketch path[data-section-outline^="hollow-rectangle-"]').count() == 2
        page.locator('#section-inner-height').fill('80')
        assert page.locator('#section-sketch path[data-section-outline^="hollow-rectangle-"]').count() == 0
        invalid_hollow_rectangle = page.locator('#section-sketch-caption').inner_text()
        assert invalid_hollow_rectangle.startswith('Preview unavailable: inner width bi and inner depth hi')
        assert page.locator('#section-sketch').get_attribute('aria-label') == invalid_hollow_rectangle
        page.locator('#section-inner-height').fill('60')
        assert page.locator('#section-sketch path[data-section-outline^="hollow-rectangle-"]').count() == 2
        sketch_width = page.locator('#section-sketch').evaluate('(svg) => svg.getBoundingClientRect().width')
        assert sketch_width <= 390, sketch_width
        page.locator('#section-properties-apply').click()
        assert abs(float(ab_area.input_value()) - 3200) < 1e-9
        assert abs(float(ab_i.input_value()) - 4106666.666666667) < 1e-7
        assert 'Ixx' in page.locator('#section-result').inner_text()
        assert 'Iyy' in page.locator('#section-result').inner_text()
        section_text = page.locator('#section-result').inner_text()
        assert 'applied Iyy' in section_text
        for expected in ('Sx 70667 mm³', 'Sy 82133 mm³', 'rx 29.721 mm', 'ry 35.824 mm', 'cX 40 mm', 'cY 50 mm'):
            assert expected in section_text, (expected, section_text)
        # A hollow circular tube has equal centroidal I in both directions.
        page.locator('#section-member').select_option('AC')
        page.locator('#section-shape').select_option('hollow-circle')
        assert page.locator('#section-diameter-control').is_visible()
        assert page.locator('#section-inner-diameter-control').is_visible()
        assert page.locator('#section-axis-control').is_hidden()
        page.locator('#section-diameter').fill('100')
        page.locator('#section-inner-diameter').fill('80')
        assert_section_preview_metadata(page, 'circle[data-section-outline="hollow-circle-outer"]', 100, 100, 900 * math.pi, 50, 50, dimension_labels=('Do', 'Di'))
        # Hollow-circle preview uses canonical properties, concentric inner/outer outlines and both diameter axes.
        assert page.locator('#section-sketch-control').is_visible()
        assert page.locator('#section-sketch circle[data-section-outline="hollow-circle-outer"]').count() == 1
        assert page.locator('#section-sketch circle[data-section-outline="hollow-circle-inner"]').count() == 1
        assert page.locator('#section-sketch circle[data-centroid]').count() == 1
        assert page.locator('#section-sketch line[data-centroid-axis="horizontal"]').count() == 1
        assert page.locator('#section-sketch line[data-centroid-axis="vertical"]').count() == 1
        for expected in ('Do=100 mm', 'Di=80 mm', 'Ixx', 'Iyy'):
            assert expected in page.locator('#section-sketch').text_content(), expected
        hollow_circle_caption = page.locator('#section-sketch-caption').inner_text()
        assert 'centroid x 50 mm, y 50 mm' in hollow_circle_caption, hollow_circle_caption
        assert page.locator('#section-sketch').get_attribute('aria-label') == hollow_circle_caption
        outer_radius = float(page.locator('#section-sketch circle[data-section-outline="hollow-circle-outer"]').get_attribute('r'))
        inner_radius = float(page.locator('#section-sketch circle[data-section-outline="hollow-circle-inner"]').get_attribute('r'))
        assert abs(inner_radius / outer_radius - 0.8) < 1e-9
        page.locator('#section-inner-diameter').fill('60')
        assert 'Di=60 mm' in page.locator('#section-sketch-caption').inner_text()
        inner_radius = float(page.locator('#section-sketch circle[data-section-outline="hollow-circle-inner"]').get_attribute('r'))
        assert abs(inner_radius / outer_radius - 0.6) < 1e-9
        # Equal/zero inner diameters and overflowing outer dimensions must clear stale geometry.
        page.locator('#section-inner-diameter').fill('100')
        assert page.locator('#section-sketch circle[data-section-outline^="hollow-circle-"]').count() == 0
        invalid_hole = page.locator('#section-sketch-caption').inner_text()
        assert invalid_hole.startswith('Preview unavailable: inner diameter Di must be positive and smaller than outer diameter Do')
        assert page.locator('#section-sketch').get_attribute('aria-label') == invalid_hole
        page.locator('#section-inner-diameter').fill('0')
        assert page.locator('#section-sketch circle[data-section-outline^="hollow-circle-"]').count() == 0
        page.locator('#section-inner-diameter').fill('80')
        page.locator('#section-diameter').fill('1e308')
        assert page.locator('#section-sketch circle[data-section-outline^="hollow-circle-"]').count() == 0
        assert page.locator('#section-sketch-caption').inner_text().startswith('Preview unavailable:')
        page.locator('#section-diameter').fill('100')
        assert page.locator('#section-sketch circle[data-section-outline^="hollow-circle-"]').count() == 2
        page.locator('#section-properties-apply').click()
        assert abs(float(ac_area.input_value()) - 900 * math.pi) < 1e-8
        assert abs(float(ac_i.input_value()) - 922500 * math.pi) < 1e-7
        section_text = page.locator('#section-result').inner_text()
        for expected in ('Sx 57962 mm³', 'Sy 57962 mm³', 'rx 32.016 mm', 'ry 32.016 mm'):
            assert expected in section_text, (expected, section_text)
        assert page.locator('#members tr').nth(2).locator('input[data-field="area"]').input_value() == '1200'
        # Invalid wall thickness must not partially overwrite the last valid hollow rectangle.
        page.locator('#section-member').select_option('AB')
        page.locator('#section-shape').select_option('hollow-rectangle')
        page.locator('#section-inner-width').fill('100')
        page.locator('#section-properties-apply').click()
        assert 'Not applied' in page.locator('#section-result').inner_text()
        assert abs(float(ab_area.input_value()) - 3200) < 1e-9
        assert abs(float(ab_i.input_value()) - 4106666.666666667) < 1e-7
        # Invalid solid geometry must preserve the last successfully applied hollow section.
        page.locator('#section-member').select_option('AB')
        page.locator('#section-shape').select_option('rectangle')
        page.locator('#section-width').fill('-1')
        page.locator('#section-properties-apply').click()
        assert 'Not applied' in page.locator('#section-result').inner_text()
        assert abs(float(ab_area.input_value()) - 3200) < 1e-9
        assert abs(float(ab_i.input_value()) - 4106666.666666667) < 1e-7
        # A solid rectangle preview shows its outline, centroid and both centroidal axes.
        page.locator('#section-width').fill('100')
        page.locator('#section-height').fill('80')
        assert page.locator('#section-sketch-control').is_visible()
        assert page.locator('#section-sketch path[data-section-outline="rectangle"]').count() == 1
        assert page.locator('#section-sketch circle[data-centroid]').count() == 1
        assert page.locator('#section-sketch line[data-centroid-axis="horizontal"]').count() == 1
        assert page.locator('#section-sketch line[data-centroid-axis="vertical"]').count() == 1
        for expected in ('B=100 mm', 'H=80 mm', 'Ixx', 'Iyy'):
            assert expected in page.locator('#section-sketch').text_content(), expected
        rectangle_caption = page.locator('#section-sketch-caption').inner_text()
        assert 'centroid x 50 mm, y 40 mm' in rectangle_caption, rectangle_caption
        assert page.locator('#section-sketch').get_attribute('aria-label') == rectangle_caption
        # Dimension edits are live, and invalid geometry removes the previous outline.
        page.locator('#section-width').fill('120')
        assert 'B=120 mm' in page.locator('#section-sketch-caption').inner_text()
        assert 'centroid x 60 mm' in page.locator('#section-sketch-caption').inner_text()
        page.locator('#section-height').fill('0')
        assert page.locator('#section-sketch path[data-section-outline="rectangle"]').count() == 0
        rectangle_invalid = page.locator('#section-sketch-caption').inner_text()
        assert rectangle_invalid.startswith('Preview unavailable: enter positive finite B and H')
        assert page.locator('#section-sketch').get_attribute('aria-label') == rectangle_invalid
        page.locator('#section-height').fill('80')
        assert page.locator('#section-sketch path[data-section-outline="rectangle"]').count() == 1
        assert 'B=120 mm' in page.locator('#section-sketch-caption').inner_text()
        page.locator('#section-width').fill('100')
        # An I-section uses three non-overlapping rectangles and reports its centroid.
        page.locator('#section-shape').select_option('i-section')
        assert page.locator('#section-web-thickness-control').is_visible()
        assert page.locator('#section-flange-thickness-control').is_visible()
        page.locator('#section-width').fill('100')
        page.locator('#section-height').fill('80')
        page.locator('#section-web-thickness').fill('10')
        page.locator('#section-flange-thickness').fill('8')
        assert_section_preview_metadata(page, 'path[data-section-outline="i-section"]', 100, 80, 2240, 50, 40, dimension_labels=('B', 'H', 'tw', 'tf'))
        # I-section preview must show a centered web and equal full-width flanges.
        assert page.locator('#section-sketch-control').is_visible()
        i_outline = page.locator('#section-sketch path[data-section-outline="i-section"]')
        assert i_outline.count() == 1
        assert i_outline.get_attribute('data-web-thickness-mm') == '10'
        assert i_outline.get_attribute('data-flange-thickness-mm') == '8'
        i_path = i_outline.get_attribute('d')
        assert i_path.startswith('M 86 24 H 276 V 39.2 H 190.5 V 160.8 H 276 V 176 H 86 V 160.8 H 171.5 V 39.2 H 86 Z'), i_path
        assert page.locator('#section-sketch circle[data-centroid]').count() == 1
        assert page.locator('#section-sketch line[data-centroid-axis="horizontal"]').count() == 1
        assert page.locator('#section-sketch line[data-centroid-axis="vertical"]').count() == 1
        assert page.locator('#section-sketch line[data-dimension="tw"]').count() == 1
        assert page.locator('#section-sketch line[data-dimension="tf"]').count() == 1
        for expected in ('B=100 mm', 'H=80 mm', 'tw=10 mm', 'tf=8 mm', 'Ixx', 'Iyy'):
            assert expected in page.locator('#section-sketch').text_content(), expected
        i_caption = page.locator('#section-sketch-caption').inner_text()
        assert 'centroid x 50 mm, y 40 mm' in i_caption, i_caption
        assert 'centered web and equal-width flanges' in i_caption
        assert page.locator('#section-sketch').get_attribute('aria-label') == i_caption
        page.locator('#section-web-thickness').fill('12')
        assert i_outline.get_attribute('data-web-thickness-mm') == '12'
        assert 'tw=12 mm' in page.locator('#section-sketch-caption').inner_text()
        page.locator('#section-web-thickness').fill('10')
        page.locator('#section-flange-thickness').fill('10')
        assert i_outline.get_attribute('data-flange-thickness-mm') == '10'
        assert 'tf=10 mm' in page.locator('#section-sketch-caption').inner_text()
        page.locator('#section-flange-thickness').fill('8')
        page.locator('#section-web-thickness').fill('100')
        assert page.locator('#section-sketch path[data-section-outline="i-section"]').count() == 0
        invalid_i = page.locator('#section-sketch-caption').inner_text()
        assert invalid_i.startswith('Preview unavailable: I-section web thickness tw')
        assert page.locator('#section-sketch').get_attribute('aria-label') == invalid_i
        page.locator('#section-web-thickness').fill('10')
        assert i_outline.count() == 1
        page.locator('#section-flange-thickness').fill('40')
        assert page.locator('#section-sketch path[data-section-outline="i-section"]').count() == 0
        invalid_i = page.locator('#section-sketch-caption').inner_text()
        assert invalid_i.startswith('Preview unavailable: I-section web thickness tw')
        assert page.locator('#section-sketch').get_attribute('aria-label') == invalid_i
        page.locator('#section-flange-thickness').fill('8')
        assert i_outline.count() == 1
        i_sketch_width = page.locator('#section-sketch').evaluate('(svg) => svg.getBoundingClientRect().width')
        assert i_sketch_width <= 390, i_sketch_width
        page.locator('#section-axis').select_option('width')
        page.locator('#section-properties-apply').click()
        assert abs(float(ab_area.input_value()) - 2240) < 1e-9
        assert abs(float(ab_i.input_value()) - 2300586.6666666665) < 1e-7
        section_text = page.locator('#section-result').inner_text()
        assert 'centroid x 50 mm' in section_text
        for expected in ('Sx 57515 mm³', 'Sy 26773 mm³', 'rx 32.048 mm', 'ry 24.446 mm', 'cX 40 mm', 'cY 50 mm'):
            assert expected in section_text, (expected, section_text)
        # An open channel has an offset centroid; applying Iyy targets only the selected member.
        page.locator('#section-member').select_option('AC')
        page.locator('#section-shape').select_option('channel')
        page.locator('#section-width').fill('100')
        page.locator('#section-height').fill('80')
        page.locator('#section-web-thickness').fill('10')
        page.locator('#section-flange-thickness').fill('8')
        assert_section_preview_metadata(page, 'path[data-section-outline="channel"]', 100, 80, 2240, 37.142857142857146, 40, dimension_labels=('B', 'H', 'tw', 'tf'))
        # Open-channel preview uses the canonical offset centroid and web-left/flanges-right geometry.
        assert page.locator('#section-sketch-control').is_visible()
        channel_outline = page.locator('#section-sketch path[data-section-outline="channel"]')
        assert channel_outline.count() == 1
        assert channel_outline.get_attribute('data-channel-opening') == 'right'
        assert channel_outline.get_attribute('data-web-thickness-mm') == '10'
        assert channel_outline.get_attribute('data-flange-thickness-mm') == '8'
        channel_path = channel_outline.get_attribute('d')
        assert channel_path.startswith('M 86 24 H 276 V 39.2 H 105 V 160.8 H 276'), channel_path
        assert page.locator('#section-sketch circle[data-centroid]').count() == 1
        assert page.locator('#section-sketch line[data-centroid-axis="horizontal"]').count() == 1
        assert page.locator('#section-sketch line[data-centroid-axis="vertical"]').count() == 1
        assert page.locator('#section-sketch line[data-dimension="tw"]').count() == 1
        assert page.locator('#section-sketch line[data-dimension="tf"]').count() == 1
        for expected in ('B=100 mm', 'H=80 mm', 'tw=10 mm', 'tf=8 mm', 'Ixx', 'Iyy'):
            assert expected in page.locator('#section-sketch').text_content(), expected
        channel_caption = page.locator('#section-sketch-caption').inner_text()
        assert 'centroid x 37.143 mm, y 40 mm' in channel_caption, channel_caption
        assert 'web on left, flanges extend right' in channel_caption
        assert page.locator('#section-sketch').get_attribute('aria-label') == channel_caption
        page.locator('#section-web-thickness').fill('12')
        assert 'tw=12 mm' in page.locator('#section-sketch-caption').inner_text()
        assert channel_outline.get_attribute('data-web-thickness-mm') == '12'
        page.locator('#section-web-thickness').fill('10')
        page.locator('#section-flange-thickness').fill('10')
        assert 'tf=10 mm' in page.locator('#section-sketch-caption').inner_text()
        assert channel_outline.get_attribute('data-flange-thickness-mm') == '10'
        page.locator('#section-flange-thickness').fill('8')
        page.locator('#section-web-thickness').fill('100')
        assert page.locator('#section-sketch path[data-section-outline="channel"]').count() == 0
        invalid_channel = page.locator('#section-sketch-caption').inner_text()
        assert invalid_channel.startswith('Preview unavailable: channel web thickness tw')
        assert page.locator('#section-sketch').get_attribute('aria-label') == invalid_channel
        page.locator('#section-web-thickness').fill('10')
        assert page.locator('#section-sketch path[data-section-outline="channel"]').count() == 1
        page.locator('#section-flange-thickness').fill('40')
        assert page.locator('#section-sketch path[data-section-outline="channel"]').count() == 0
        invalid_channel = page.locator('#section-sketch-caption').inner_text()
        assert invalid_channel.startswith('Preview unavailable: channel web thickness tw')
        assert page.locator('#section-sketch').get_attribute('aria-label') == invalid_channel
        page.locator('#section-flange-thickness').fill('8')
        assert page.locator('#section-sketch path[data-section-outline="channel"]').count() == 1
        channel_sketch_width = page.locator('#section-sketch').evaluate('(svg) => svg.getBoundingClientRect().width')
        assert channel_sketch_width <= 390, channel_sketch_width
        page.locator('#section-axis').select_option('depth')
        page.locator('#section-properties-apply').click()
        assert abs(float(ac_area.input_value()) - 2240) < 1e-9
        assert abs(float(ac_i.input_value()) - 2264380.9523809524) < 1e-7
        section_text = page.locator('#section-result').inner_text()
        assert 'centroid x 37.143 mm' in section_text
        for expected in ('Sx 57515 mm³', 'Sy 36024 mm³', 'rx 32.048 mm', 'ry 31.794 mm', 'cX 40 mm', 'cY 62.857 mm'):
            assert expected in section_text, (expected, section_text)
        assert page.locator('#members tr').nth(2).locator('input[data-field="area"]').input_value() == '1200'
        # Invalid flange thickness must roll back without partially changing the channel member.
        page.locator('#section-flange-thickness').fill('40')
        page.locator('#section-properties-apply').click()
        assert 'Not applied' in page.locator('#section-result').inner_text()
        assert abs(float(ac_area.input_value()) - 2240) < 1e-9
        assert abs(float(ac_i.input_value()) - 2264380.9523809524) < 1e-7
        # L-angle uses two non-overlapping rectangles; verify principal axes and member isolation.
        page.locator('#section-member').select_option('AB')
        page.locator('#section-shape').select_option('l-angle')
        assert page.locator('#section-angle-thickness-control').is_visible()
        assert page.locator('#section-web-thickness-control').is_hidden()
        assert page.locator('#section-flange-thickness-control').is_hidden()
        major_axis_option = page.locator('#section-axis option[value="principal-major"]')
        assert not major_axis_option.evaluate('(option) => option.hidden')
        page.locator('#section-width').fill('100')
        page.locator('#section-height').fill('80')
        page.locator('#section-angle-thickness').fill('10')
        assert_section_preview_metadata(page, 'path[data-section-outline="l-angle"]', 100, 80, 1700, 31.470588235294116, 21.470588235294116, centroidal_axes=False, dimension_labels=('B', 'H', 't'))
        assert page.locator('#section-sketch-control').is_visible()
        assert page.locator('#section-sketch path[data-section-outline="l-angle"]').count() == 1
        assert page.locator('#section-sketch circle[data-centroid]').count() == 1
        major_principal_axis = page.locator('#section-sketch line[data-principal-axis="major"]')
        minor_principal_axis = page.locator('#section-sketch line[data-principal-axis="minor"]')
        assert major_principal_axis.count() == 1
        assert minor_principal_axis.count() == 1
        major_angle = float(major_principal_axis.get_attribute('data-axis-angle-deg'))
        minor_angle = float(minor_principal_axis.get_attribute('data-axis-angle-deg'))
        assert abs(minor_angle - major_angle - 90) < 1e-9
        centroid = page.locator('#section-sketch circle[data-centroid]').evaluate(
            '(node) => ({x:Number(node.getAttribute("cx")),y:Number(node.getAttribute("cy"))})')
        for axis in (major_principal_axis, minor_principal_axis):
            endpoints = axis.evaluate('(node) => ({x1:Number(node.getAttribute("x1")),y1:Number(node.getAttribute("y1")),x2:Number(node.getAttribute("x2")),y2:Number(node.getAttribute("y2"))})')
            assert abs((endpoints['x1'] + endpoints['x2']) / 2 - centroid['x']) < 1e-6
            assert abs((endpoints['y1'] + endpoints['y2']) / 2 - centroid['y']) < 1e-6
            assert abs(float(axis.get_attribute('data-centroid-x-mm')) - 31.470588235294116) < 1e-9
            assert abs(float(axis.get_attribute('data-centroid-y-mm')) - 21.470588235294116) < 1e-9
        major_axis_label = page.locator('#section-sketch text[data-principal-axis-label="major"]')
        minor_axis_label = page.locator('#section-sketch text[data-principal-axis-label="minor"]')
        # SVG <text> is not an HTMLElement: use text_content(), and verify each accessible name.
        assert major_axis_label.text_content() == 'I₁'
        assert minor_axis_label.text_content() == 'I₂'
        assert major_axis_label.get_attribute('aria-label') == 'Major principal axis I1'
        assert minor_axis_label.get_attribute('aria-label') == 'Minor principal axis I2'
        assert abs(float(major_axis_label.get_attribute('data-axis-angle-deg')) - major_angle) < 1e-9
        assert abs(float(minor_axis_label.get_attribute('data-axis-angle-deg')) - minor_angle) < 1e-9
        for expected in ('B=100 mm', 'H=80 mm', 't=10 mm',
                         'major principal axis 57.953°', 'minor principal axis 147.953°'):
            assert expected in page.locator('#section-sketch-caption').inner_text()
        # Second asymmetric reference: canonical outline, centroid and principal axes.
        page.locator('#section-width').fill('120')
        page.locator('#section-height').fill('70')
        page.locator('#section-angle-thickness').fill('12')
        asymmetric_outline = page.locator('#section-sketch path[data-section-outline="l-angle"]')
        assert asymmetric_outline.count() == 1
        for attribute, expected in (
            ('data-section-width-mm', 120), ('data-section-height-mm', 70),
            ('data-section-thickness-mm', 12), ('data-section-area-mm2', 2136),
            ('data-section-centroid-x-mm', 42.40449438202247),
            ('data-section-centroid-y-mm', 17.40449438202247)
        ):
            assert abs(float(asymmetric_outline.get_attribute(attribute)) - expected) < 1e-9
        asymmetric_major = page.locator('#section-sketch line[data-principal-axis="major"]')
        asymmetric_minor = page.locator('#section-sketch line[data-principal-axis="minor"]')
        assert asymmetric_major.count() == asymmetric_minor.count() == 1
        assert abs(float(asymmetric_major.get_attribute('data-axis-angle-deg')) - 71.2856436104474) < 1e-9
        assert abs(float(asymmetric_minor.get_attribute('data-axis-angle-deg')) - 161.2856436104474) < 1e-9
        assert abs(float(asymmetric_minor.get_attribute('data-axis-angle-deg')) - float(asymmetric_major.get_attribute('data-axis-angle-deg')) - 90) < 1e-9
        for axis in (asymmetric_major, asymmetric_minor):
            assert abs(float(axis.get_attribute('data-centroid-x-mm')) - 42.40449438202247) < 1e-9
            assert abs(float(axis.get_attribute('data-centroid-y-mm')) - 17.40449438202247) < 1e-9
        for expected in ('B=120 mm', 'H=70 mm', 't=12 mm', 'major principal axis 71.286°', 'minor principal axis 161.286°'):
            assert expected in page.locator('#section-sketch-caption').inner_text()
        assert page.locator('#section-sketch').get_attribute('aria-label') == page.locator('#section-sketch-caption').inner_text()

        # A 69.9 mm leg is valid for H=70 mm; exactly 70 mm is invalid.
        page.locator('#section-angle-thickness').fill('69.9')
        near_limit_outline = page.locator('#section-sketch path[data-section-outline="l-angle"]')
        assert near_limit_outline.count() == 1
        assert abs(float(near_limit_outline.get_attribute('data-section-area-mm2')) - 8394.99) < 1e-8
        assert abs(float(near_limit_outline.get_attribute('data-section-centroid-x-mm')) - 59.97914238134888) < 1e-9
        assert abs(float(near_limit_outline.get_attribute('data-section-centroid-y-mm')) - 34.97914238134888) < 1e-9
        near_major = page.locator('#section-sketch line[data-principal-axis="major"]')
        near_minor = page.locator('#section-sketch line[data-principal-axis="minor"]')
        assert near_major.count() == near_minor.count() == 1
        assert abs(float(near_major.get_attribute('data-axis-angle-deg')) - 89.94723327653608) < 1e-8
        assert abs(float(near_minor.get_attribute('data-axis-angle-deg')) - 179.94723327653608) < 1e-8
        assert abs(float(near_minor.get_attribute('data-axis-angle-deg')) - float(near_major.get_attribute('data-axis-angle-deg')) - 90) < 1e-9
        assert page.evaluate("() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1")
        page.locator('#section-angle-thickness').fill('70')
        assert page.locator('#section-sketch path[data-section-outline="l-angle"]').count() == 0
        assert page.locator('#section-sketch line[data-principal-axis]').count() == 0
        assert page.locator('#section-sketch-caption').inner_text().startswith('Preview unavailable: enter positive B, H and t')

        page.locator('#section-width').fill('100')
        page.locator('#section-height').fill('80')
        page.locator('#section-angle-thickness').fill('10')
        assert page.locator('#section-sketch path[data-section-outline="l-angle"]').count() == 1
        assert page.locator('#section-sketch line[data-principal-axis]').count() == 2
        page.locator('#section-axis').select_option('principal-major')
        assert page.locator('#section-axis').input_value() == 'principal-major'
        page.locator('#section-properties-apply').click()
        assert abs(float(ab_area.input_value())-1700) < 1e-9
        assert abs(float(ab_i.input_value())-2136969.904902401) < 1e-7
        section_text = page.locator('#section-result').inner_text()
        for expected in ('centroid x 31.471 mm, y 21.471 mm','Ixy','principal I1','principal I2',
                         'I1 axis 57.953° counter-clockwise from +x'):
            assert expected in section_text, (expected, section_text)
        assert abs(float(ac_area.input_value())-2240) < 1e-9
        page.locator('#section-axis').select_option('principal-minor')
        page.locator('#section-properties-apply').click()
        assert abs(float(ab_i.input_value())-489010.48725446186) < 1e-7
        page.locator('#section-angle-thickness').fill('80')
        assert page.locator('#section-sketch path[data-section-outline="l-angle"]').count() == 0
        invalid_caption = page.locator('#section-sketch-caption').inner_text()
        assert invalid_caption.startswith('Preview unavailable: enter positive B, H and t')
        assert page.locator('#section-sketch').get_attribute('aria-label') == invalid_caption
        assert page.locator('#section-sketch line[data-principal-axis]').count() == 0
        page.locator('#section-angle-thickness').fill('10')
        assert page.locator('#section-sketch path[data-section-outline="l-angle"]').count() == 1
        assert page.locator('#section-sketch line[data-principal-axis]').count() == 2
        page.locator('#section-angle-thickness').fill('80')
        assert page.locator('#section-sketch path[data-section-outline="l-angle"]').count() == 0
        page.locator('#section-properties-apply').click()
        assert 'Not applied' in page.locator('#section-result').inner_text()
        assert abs(float(ab_area.input_value())-1700) < 1e-9
        assert abs(float(ab_i.input_value())-489010.48725446186) < 1e-7
        # Restore the example values before solver and export regressions below.
        ab_area.fill('1200')
        ab_i.fill('')
        ac_area.fill('1200')
        ac_i.fill('')
        assert page.evaluate("() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1")
        # The solver rejects this released support, but the non-solving preview remains visible.
        page.locator('#solve').click()
        assert page.locator('#status.error').count() == 1
        assert 'Unstable or under-constrained truss' in page.locator('#status').inner_text()
        assert page.locator('#plot line[data-member-id]').count() == 3
        # Invalid geometry removes stale preview; correcting the field restores it.
        node_b_x = page.locator('#nodes tr').nth(1).locator('input[data-field="x"]')
        node_b_x.fill('')
        assert 'Preview unavailable' in page.locator('#preview-summary').inner_text()
        assert page.locator('#plot line[data-member-id]').count() == 0
        assert 'Correct model inputs' in page.locator('#member-metrics').inner_text()
        node_b_x.fill('4')
        assert '3 joints' in page.locator('#preview-summary').inner_text()
        assert page.locator('#member-metrics tr').count() == 3
        page.locator('#reset').click()
        assert 'Analysis complete' in page.locator('#status').inner_text()
        # Material metrics use the same SI contract for the simple analytical bar and triangle.
        page.locator('#example').select_option('bar')
        page.locator('#load-example').click()
        bar_preview = page.locator('#preview-summary').inner_text()
        assert 'total member length 2 m' in bar_preview, bar_preview
        assert 'axial member volume Σ(L·A) 0.002 m³' in bar_preview, bar_preview
        bar_row = page.locator('#member-metrics tr').first.locator('td')
        assert [bar_row.nth(i).inner_text() for i in range(6)] == ['AB','A','B','2','1000','0.002']
        page.locator('#example').select_option('triangle')
        page.locator('#load-example').click()
        triangle_preview = page.locator('#preview-summary').inner_text()
        assert 'total member length 11.21 m' in triangle_preview, triangle_preview
        assert 'axial member volume Σ(L·A) 0.01345 m³' in triangle_preview, triangle_preview
        assert page.evaluate("() => { const e=document.querySelector('#preview-summary'); return e.scrollWidth <= e.clientWidth + 1; }")
        assert page.evaluate("() => document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1")
        result = page.evaluate('() => TrussStudio.solve(TrussStudio.example)')
        assert result['residual'] < 1e-9
        forces = {m['id']: m['force'] for m in result['members']}
        assert abs(forces['AC'] + 10000 / 2**0.5) < 1e-7, forces
        assert abs(forces['BC'] + 10000 / 2**0.5) < 1e-7, forces
        assert abs(forces['AB'] - 5000) < 1e-7, forces
        reactions = {n['id']: n for n in result['nodes']}
        assert abs(reactions['A']['ry'] - 5000) < 1e-7
        assert abs(reactions['B']['ry'] - 5000) < 1e-7
        assert abs(reactions['A']['rx']) < 1e-7
        assert result['maxDisplacement'] > 0
        assert page.locator('#member-results tr').count() == 3
        assert page.locator('#joint-results tr').count() == 3
        assert page.locator('#plot line').count() >= 6
        # Import a model produced by the old SI-only JSON editor: retain N, Pa, m² semantics.
        prior = page.evaluate('TrussStudio.example')
        # Two overlapping imports must be ordered by selection, not by File.text() completion.
        triangle_json = page.evaluate("() => ProMathTrussFEM.exportJSON(ProMathTrussFEM.examples.triangle)")
        page.evaluate("""() => {
            const read = Blob.prototype.arrayBuffer;
            window.__importReads = [];
            File.prototype.arrayBuffer = function() {
                const name = this.name;
                const delay = name === 'slow-invalid.json' ? 120 : 0;
                return new Promise(resolve => setTimeout(resolve, delay))
                    .then(() => read.call(this))
                    .then(value => { window.__importReads.push(name); return value; });
            };
        }""")
        page.locator('#import-model').set_input_files({'name':'slow-invalid.json','mimeType':'application/json',
                                                       'buffer':b'{bad'})
        page.locator('#import-model').set_input_files({'name':'fast-valid.json','mimeType':'application/json',
                                                       'buffer':triangle_json.encode('utf-8')})
        page.wait_for_function("""() => {
            const status = document.querySelector('#status');
            return window.__importReads?.length === 2 &&
                   status?.textContent.startsWith('Analysis complete') &&
                   status.getAttribute('aria-busy') === 'false';
        }""")
        assert page.evaluate('window.__importReads') == ['fast-valid.json','slow-invalid.json']
        assert 'total member length 11.21 m' in page.locator('#preview-summary').inner_text()
        assert page.locator('#member-metrics tr').count() == 3
        # Prepend actual UTF-8 BOM bytes; the canonical importer strips the decoded BOM.
        page.evaluate("""() => {
            const read = Blob.prototype.arrayBuffer;
            File.prototype.arrayBuffer = function() {
                return read.call(this).then(value => {
                    const source = new Uint8Array(value);
                    const prefixed = new Uint8Array(source.length + 3);
                    prefixed.set([0xEF, 0xBB, 0xBF]);
                    prefixed.set(source, 3);
                    return prefixed.buffer;
                });
            };
        }""")
        page.locator('#import-model').set_input_files({'name':'legacy.json','mimeType':'application/json',
                                                      'buffer':json.dumps(prior).encode('utf-8')})
        page.wait_for_function("""() => {
            const status = document.querySelector('#status');
            return status?.textContent.includes('Analysis complete') &&
                   status.getAttribute('aria-busy') === 'false';
        }""")
        assert 'Analysis complete' in page.locator('#status').inner_text()
        assert page.locator('#status').get_attribute('aria-busy') == 'false'
        # Normalized user controls now show kN/GPa/mm² rather than SI base units.
        assert page.locator('#nodes tr').nth(2).locator('input[data-field="fy"]').input_value() == '-10'
        assert page.locator('#members tr').nth(0).locator('input[data-field="E"]').input_value() == '200'
        assert page.locator('#members tr').nth(0).locator('input[data-field="area"]').input_value() == '1000.0000000000001' or abs(float(page.locator('#members tr').nth(0).locator('input[data-field="area"]').input_value())-1000)<1e-9
        legacy_preview = page.locator('#preview-summary').inner_text()
        assert 'total member length 4.828 m' in legacy_preview, legacy_preview
        assert 'axial member volume Σ(L·A) 0.004828 m³' in legacy_preview, legacy_preview
        assert 'bounds 2 × 1 m' in legacy_preview, legacy_preview
        legacy_rows = page.locator('#member-metrics tr')
        assert legacy_rows.count() == 3
        legacy_first = legacy_rows.first.locator('td')
        assert [legacy_first.nth(i).inner_text() for i in range(8)] == ['AB','A','B','2','1000','0.002','200','100']
        # Capture Blob downloads without navigating away from the standalone tool.
        page.evaluate('''() => { window.__exports=[]; const orig=URL.createObjectURL.bind(URL);
            URL.createObjectURL = blob => {window.__exports.push({blob});return orig(blob);};
            HTMLAnchorElement.prototype.click = function(){window.__exports.at(-1).name=this.download;}; }''')
        page.locator('#export-model').click()
        model_export = page.evaluate('''async () => ({name:window.__exports[0].name,body:await window.__exports[0].blob.text()})''')
        assert model_export['name'].endswith('.json')
        exported_model = json.loads(model_export['body'])
        assert abs(float(exported_model['members'][0]['area']) - 1000) < 1e-9
        # Invalid edits must not produce a JSON file that cannot be imported again.
        page.locator('#nodes tr').nth(1).locator('input[data-field="fx"]').fill('')
        page.locator('#export-model').click()
        assert page.locator('#status.error').count() == 1
        assert len(page.evaluate('window.__exports')) == 1, 'Invalid model must not be exported'
        page.locator('#export-material-csv').click()
        assert len(page.evaluate('window.__exports')) == 1, 'Invalid model must not produce a material schedule'
        assert 'Material schedule export failed' in page.locator('#status').inner_text()
        # Restore a valid model but do not solve: material scheduling is a pre-solve workflow.
        page.locator('#nodes tr').nth(1).locator('input[data-field="fx"]').fill('0')
        page.locator('#export-material-csv').focus()
        page.keyboard.press('Enter')
        material_export = page.evaluate('''async () => ({name:window.__exports[1].name,body:await window.__exports[1].blob.text()})''')
        assert material_export['name'] == 'promath-truss-material-schedule.csv'
        material_rows = list(csv.reader(io.StringIO(material_export['body'])))
        assert material_rows[0] == ['Member ID','Start joint ID','End joint ID','Centreline length (m)','Cross-sectional area (m²)','Axial material volume (m³)','Elastic modulus (GPa)','Axial stiffness EA/L (kN/mm)','Density (kg/m³)','Member mass (kg)','Second moment of area I (mm⁴)','Effective length factor K (-)','Euler critical load Pcr (kN)']
        assert material_rows[1] == ['AB','A','B','2','0.001','0.002','200','100','','','','','']
        assert material_export['body'].endswith(chr(13) + chr(10))
        assert 'Validated member material schedule exported.' in page.locator('#status').inner_text()
        page.locator('#solve').click()
        assert 'Analysis complete' in page.locator('#status').inner_text()
        # A malformed import must preserve the currently edited model.
        # Hold the byte read open to verify pending status before validation settles.
        page.evaluate('''() => {
            const read = Blob.prototype.arrayBuffer;
            let release;
            const gate = new Promise(resolve => { release = resolve; });
            window.__releaseInvalidImport = release;
            File.prototype.arrayBuffer = function() {
                const pending = read.call(this);
                return this.name === 'invalid.json' ? gate.then(() => pending) : pending;
            };
        }''')
        page.locator('#import-model').set_input_files({'name':'invalid.json','mimeType':'application/json',
                                                      'buffer':b'{bad'})
        assert page.locator('#status').inner_text() == 'Importing model…'
        assert page.locator('#status').get_attribute('aria-busy') == 'true'
        page.evaluate('window.__releaseInvalidImport()')
        page.wait_for_function("""() => {
            const status = document.querySelector('#status');
            return status.classList.contains('error') && status.getAttribute('aria-busy') === 'false';
        }""")
        assert page.locator('#status.error').count() == 1
        assert page.locator('#nodes tr').count() == 3
        assert page.locator('#nodes tr').nth(2).locator('input[data-field="fy"]').input_value() == '-10'
        # File.text() replaces malformed UTF-8; reject bytes that would silently corrupt IDs.
        invalid_utf8 = json.dumps(prior).encode('utf-8').replace(b'"AB"', b'"A\xff"', 1)
        assert b'\xff' in invalid_utf8
        page.locator('#import-model').set_input_files({'name':'invalid-utf8.json','mimeType':'application/json',
                                                      'buffer':invalid_utf8})
        page.wait_for_function("""() => {
            const status = document.querySelector('#status');
            return status.classList.contains('error') && status.getAttribute('aria-busy') === 'false';
        }""")
        assert 'valid UTF-8' in page.locator('#status').inner_text()
        assert page.locator('#nodes tr').count() == 3
        assert page.locator('#nodes tr').nth(2).locator('input[data-field="fy"]').input_value() == '-10'
        assert page.locator('#members tr').first.locator('input[data-field="id"]').input_value() == 'AB'
        page.evaluate('''() => { File.prototype.arrayBuffer = Blob.prototype.arrayBuffer; }''')
        # The 1 MiB boundary is measured in UTF-8 bytes, including multibyte text.
        byte_limit = 1024 * 1024
        exact_text = json.dumps({**prior, 'note': 'é' * 100}, ensure_ascii=False)
        exact_text += ' ' * (byte_limit - len(exact_text.encode('utf-8')))
        exact_payload = exact_text.encode('utf-8')
        assert len(exact_payload) == byte_limit and len(exact_text) < byte_limit
        page.locator('#import-model').set_input_files({'name':'exact-1mib.json','mimeType':'application/json',
                                                       'buffer':exact_payload})
        page.wait_for_function("""() => {
            const status = document.querySelector('#status');
            return status?.textContent.startsWith('Analysis complete') &&
                   status.getAttribute('aria-busy') === 'false';
        }""")
        assert page.locator('#nodes tr').count() == 3
        assert page.locator('#members tr').count() == 3
        assert page.locator('#members tr').first.locator('input[data-field="id"]').input_value() == 'AB'

        # Files above the limit must be rejected before arrayBuffer allocates/reads them.
        page.evaluate('''() => {
            const read = Blob.prototype.arrayBuffer;
            window.__sizeGuardReads = 0;
            File.prototype.arrayBuffer = function() {
                window.__sizeGuardReads++;
                return read.call(this);
            };
        }''')
        triangle_bytes = triangle_json.encode('utf-8')
        oversized_ascii = triangle_bytes + b' ' * (byte_limit + 1 - len(triangle_bytes))
        assert len(oversized_ascii) == byte_limit + 1
        page.locator('#import-model').set_input_files({'name':'oversized-ascii.json','mimeType':'application/json',
                                                       'buffer':oversized_ascii})
        page.wait_for_function("""() => {
            const status = document.querySelector('#status');
            return status.classList.contains('error') && status.getAttribute('aria-busy') === 'false';
        }""")
        assert 'exceeds 1 MiB' in page.locator('#status').inner_text()
        assert page.evaluate('window.__sizeGuardReads') == 0
        assert page.locator('#nodes tr').count() == 3
        assert page.locator('#members tr').first.locator('input[data-field="id"]').input_value() == 'AB'

        multibyte_text = json.dumps({**prior, 'note': 'é' * 530000}, ensure_ascii=False)
        multibyte_payload = multibyte_text.encode('utf-8')
        assert len(multibyte_text) < byte_limit
        assert len(multibyte_payload) > byte_limit
        page.locator('#import-model').set_input_files({'name':'oversized-multibyte.json','mimeType':'application/json',
                                                       'buffer':multibyte_payload})
        page.wait_for_function("""() => {
            const status = document.querySelector('#status');
            return status.classList.contains('error') && status.getAttribute('aria-busy') === 'false';
        }""")
        assert 'exceeds 1 MiB' in page.locator('#status').inner_text()
        assert page.evaluate('window.__sizeGuardReads') == 0
        assert page.locator('#nodes tr').count() == 3
        assert page.locator('#members tr').count() == 3

        # Even inconsistent File.size metadata cannot bypass the actual byte-length guard.
        page.evaluate('''() => {
            const originalSize = Object.getOwnPropertyDescriptor(File.prototype, 'size');
            Object.defineProperty(File.prototype, 'size', {configurable:true, get:() => 1});
            window.__restoreFileSize = () => {
                if (originalSize) Object.defineProperty(File.prototype, 'size', originalSize);
                else delete File.prototype.size;
            };
            const read = Blob.prototype.arrayBuffer;
            window.__actualByteGuardReads = 0;
            File.prototype.arrayBuffer = function() {
                window.__actualByteGuardReads++;
                return read.call(this);
            };
        }''')
        page.locator('#import-model').set_input_files({'name':'underreported-size.json','mimeType':'application/json',
                                                       'buffer':oversized_ascii})
        page.wait_for_function("""() => {
            const status = document.querySelector('#status');
            return status.classList.contains('error') && status.getAttribute('aria-busy') === 'false';
        }""")
        assert 'exceeds 1 MiB' in page.locator('#status').inner_text()
        assert page.evaluate('window.__actualByteGuardReads') == 1
        assert page.locator('#nodes tr').count() == 3
        assert page.locator('#members tr').first.locator('input[data-field="id"]').input_value() == 'AB'
        page.evaluate('''() => {
            File.prototype.arrayBuffer = Blob.prototype.arrayBuffer;
            window.__restoreFileSize();
        }''')
        page.locator('#solve').click()
        assert 'Analysis complete' in page.locator('#status').inner_text()
        page.locator('#export-csv').click()
        exported = page.evaluate('''async () => ({name:window.__exports[2].name,body:await window.__exports[2].blob.text()})''')
        assert exported['name'].endswith('.csv') and 'Axial force (kN)' in exported['body']
        page.locator('#nodes tr').nth(1).locator('input[data-field="fixY"]').uncheck()
        page.locator('#solve').click()
        assert page.locator('#status.error').count() == 1
        page.locator('#export-csv').click()
        assert len(page.evaluate('window.__exports')) == 3, 'Failed analysis must not export stale results'
        page.locator('#reset').click()
        assert 'Analysis complete' in page.locator('#status').inner_text()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2')
        # Optional density stays unknown until supplied; mass is volume × density in SI.
        page.locator('#example').select_option('bar')
        page.locator('#load-example').click()
        density_input = page.locator('#members tr').first.locator('input[data-field="density"]')
        assert density_input.input_value() == ''
        metric_cells = page.locator('#member-metrics tr').first.locator('td')
        assert metric_cells.count() == 13
        assert metric_cells.nth(8).inner_text() == '—' and metric_cells.nth(9).inner_text() == '—'
        assert [metric_cells.nth(i).inner_text() for i in (10,11,12)] == ['—','—','—']
        density_input.fill('7850')
        metric_cells = page.locator('#member-metrics tr').first.locator('td')
        assert metric_cells.nth(8).inner_text() == '7850'
        assert metric_cells.nth(9).inner_text() == '15.7'
        export_index = page.evaluate('window.__exports.length')
        page.locator('#export-material-csv').click()
        density_export = page.evaluate('''async index => ({name:window.__exports[index].name,body:await window.__exports[index].blob.text()})''', export_index)
        density_rows = list(csv.reader(io.StringIO(density_export['body'])))
        assert density_rows[0][8:10] == ['Density (kg/m³)','Member mass (kg)']
        assert density_rows[1][8:10] == ['7850','15.7']
        density_input.fill('')
        metric_cells = page.locator('#member-metrics tr').first.locator('td')
        assert metric_cells.nth(8).inner_text() == '—' and metric_cells.nth(9).inner_text() == '—'
        # Euler Pcr is available only when both optional I and K are supplied.
        i_input = page.locator('#members tr').first.locator('input[data-field="I"]')
        k_input = page.locator('#members tr').first.locator('input[data-field="K"]')
        i_input.fill('1000000')
        assert 'Model overview' in page.locator('#preview-summary').inner_text()
        assert 'Euler estimate requires both I and K' in page.locator('#status').inner_text()
        metric_cells = page.locator('#member-metrics tr').first.locator('td')
        assert metric_cells.count() == 13
        assert [metric_cells.nth(i).inner_text() for i in (10,11,12)] == ['1000000','—','—']
        # K-only is also a valid partial member property; the preview stays available without Pcr.
        i_input.fill('')
        k_input.fill('1')
        assert 'Model overview' in page.locator('#preview-summary').inner_text()
        assert 'Euler estimate requires both I and K' in page.locator('#status').inner_text()
        metric_cells = page.locator('#member-metrics tr').first.locator('td')
        assert [metric_cells.nth(i).inner_text() for i in (10,11,12)] == ['—','1','—']
        # Supplying the missing I restores the Euler estimate without invalidating the preview.
        i_input.fill('1000000')
        assert 'Preview ready' in page.locator('#status').inner_text()
        assert 'Euler estimate requires both I and K' not in page.locator('#status').inner_text()
        metric_cells = page.locator('#member-metrics tr').first.locator('td')
        assert metric_cells.nth(10).inner_text() == '1000000'
        # Whole-number section properties stay readable; fractional values retain compact precision.
        i_input.fill('1250000.5')
        metric_cells = page.locator('#member-metrics tr').first.locator('td')
        assert metric_cells.nth(10).inner_text() == '1.25e+6'
        i_input.fill('1000000')
        metric_cells = page.locator('#member-metrics tr').first.locator('td')
        assert metric_cells.nth(10).inner_text() == '1000000'
        assert metric_cells.nth(11).inner_text() == '1'
        assert metric_cells.nth(12).inner_text() == '493.48'
        # Display precision follows the inverse-square effective-length relationship.
        k_input.fill('2')
        metric_cells = page.locator('#member-metrics tr').first.locator('td')
        assert metric_cells.nth(12).inner_text() == '123.37'
        k_input.fill('1')
        metric_cells = page.locator('#member-metrics tr').first.locator('td')
        assert metric_cells.nth(12).inner_text() == '493.48'
        export_index = page.evaluate('window.__exports.length')
        page.locator('#export-material-csv').click()
        euler_export = page.evaluate('''async index => ({name:window.__exports[index].name,body:await window.__exports[index].blob.text()})''', export_index)
        euler_rows = list(csv.reader(io.StringIO(euler_export['body'])))
        assert euler_rows[0][-3:] == ['Second moment of area I (mm⁴)','Effective length factor K (-)','Euler critical load Pcr (kN)']
        assert euler_rows[1][-3:] == ['1000000','1','493.4802200544678']
        # Post-solve Euler screening is compression-only: tension and zero demand never divide.
        page.locator('#solve').click()
        result_cells = page.locator('#member-results tr').first.locator('td')
        assert result_cells.count() == 7
        assert result_cells.nth(4).inner_text() == '—' and result_cells.nth(5).inner_text() == '—'
        assert result_cells.nth(6).inner_text() == 'Tension — not applicable'
        page.locator('#nodes tr').nth(1).locator('input[data-field="fx"]').fill('0')
        page.locator('#solve').click()
        result_cells = page.locator('#member-results tr').first.locator('td')
        assert result_cells.nth(4).inner_text() == '—' and result_cells.nth(5).inner_text() == '—'
        assert result_cells.nth(6).inner_text() == 'No compression demand'
        page.locator('#nodes tr').nth(1).locator('input[data-field="fx"]').fill('-1')
        page.locator('#solve').click()
        result_cells = page.locator('#member-results tr').first.locator('td')
        assert 0 < float(result_cells.nth(4).inner_text().rstrip('%')) < 1
        assert abs(float(result_cells.nth(5).inner_text()) - 493.4802200544678) < 0.1
        assert result_cells.nth(6).inner_text() == 'Below ideal Euler load'
        export_index = page.evaluate('window.__exports.length')
        page.locator('#export-csv').click()
        result_export = page.evaluate('''async index => ({name:window.__exports[index].name,body:await window.__exports[index].blob.text()})''', export_index)
        result_rows = list(csv.reader(io.StringIO(result_export['body'])))
        assert result_rows[0][:7] == ['Member','Axial force (kN)','Stress (MPa)','Strain','Euler utilization (%)','Euler load ratio Pcr/Pcomp (-)','Euler assessment']
        assert result_rows[1][4] and result_rows[1][5] and result_rows[1][6] == 'Below ideal Euler load'
        assert result_export['body'].endswith(chr(13) + chr(10))
        assert result_export['body'].count(chr(13) + chr(10)) == len(result_rows)
        result_without_crlf = result_export['body'].replace(chr(13) + chr(10), '')
        assert chr(13) not in result_without_crlf and chr(10) not in result_without_crlf
        page.locator('#nodes tr').nth(1).locator('input[data-field="fx"]').fill('-600')
        page.locator('#solve').click()
        result_cells = page.locator('#member-results tr').first.locator('td')
        assert float(result_cells.nth(4).inner_text().rstrip('%')) > 100
        assert result_cells.nth(6).inner_text() == 'At/above ideal Euler load'
        page.locator('#nodes tr').nth(1).locator('input[data-field="fx"]').fill('1')
        page.locator('#solve').click()
        k_input.fill('2')
        metric_cells = page.locator('#member-metrics tr').first.locator('td')
        assert metric_cells.nth(12).inner_text() == '123.37'
        k_input.fill('0')
        assert 'Preview unavailable' in page.locator('#preview-summary').inner_text()
        assert 'K must be positive' in page.locator('#status').inner_text()
        k_input.fill('1')
        i_input.fill('-1')
        assert 'Preview unavailable' in page.locator('#preview-summary').inner_text()
        assert 'I must be positive' in page.locator('#status').inner_text()
        i_input.fill('')
        k_input.fill('')
        assert 'Preview ready' in page.locator('#status').inner_text()
        # Negative density is rejected and cannot be exported; clearing it restores the preview.
        density_input.fill('-1')
        assert 'Preview unavailable' in page.locator('#preview-summary').inner_text()
        downloads_before_invalid = page.evaluate('window.__exports.length')
        page.locator('#export-material-csv').click()
        assert page.evaluate('window.__exports.length') == downloads_before_invalid
        assert 'density must be non-negative' in page.locator('#status').inner_text()
        density_input.fill('')
        assert 'Preview ready' in page.locator('#status').inner_text()
        # Legacy SI import keeps density and the Euler estimate physically equivalent.
        legacy_model = page.evaluate('TrussStudio.example')
        for member in legacy_model['members']:
            member['density'] = 7850
            member['I'] = 1e-6
            member['K'] = 1
        page.locator('#import-model').set_input_files({'name':'legacy-density-buckling.json','mimeType':'application/json',
                                                       'buffer':json.dumps(legacy_model).encode('utf-8')})
        page.wait_for_function("""() => document.querySelector('#status').textContent.startsWith('Analysis complete')""")
        legacy_cells = page.locator('#member-metrics tr').first.locator('td')
        assert legacy_cells.nth(8).inner_text() == '7850'
        assert legacy_cells.nth(9).inner_text() == '15.7'
        assert legacy_cells.nth(10).inner_text() == '1000000'
        assert legacy_cells.nth(11).inner_text() == '1'
        assert legacy_cells.nth(12).inner_text() == '493.48'
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2')
        assert not errors, errors
        browser.close()
    print('Truss Studio: pre-solve geometry, validated material schedule CSV, import/export, recovery and mobile PASS')


if __name__ == '__main__':
    main()

"""Standalone 2D truss lab: in-browser references, negative cases, SVG visualization,
keyboard and mobile layout, import recovery, CSV/SVG output and console integrity."""
import csv
import io
import json
import math
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'tools' / 'truss-studio.html').read_text(encoding='utf-8')
# Test the unchanged standalone JS with inline injection to avoid file://, which is
# disallowed in some restricted CI/container browsers. Deployment keeps relative files.
HTML = HTML.replace('<script defer src="truss-fem.js"></script>', '')
HTML = HTML.replace('<script defer src="truss-fem-ui.js"></script>', '')
FEM_JS = (ROOT / 'tools' / 'truss-fem.js').read_text(encoding='utf-8')
UI_JS = (ROOT / 'tools' / 'truss-fem-ui.js').read_text(encoding='utf-8')
# Expose the private CSV helper only in this injected test copy; production keeps it scoped.
UI_JS = UI_JS.replace('  updateSectionShape();',
                      '  window.__testDownloadCsv = downloadCsv;\n  updateSectionShape();', 1)
assert 'window.__testDownloadCsv = downloadCsv;' in UI_JS
HTML = HTML.replace('</body>', '<script>' + FEM_JS + '</script>'
                    + '<script>' + UI_JS + '</script></body>')


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None,
                                     args=['--no-sandbox'])
        for width in (1280, 390):
            page = browser.new_page(viewport={'width': width, 'height': 900}, accept_downloads=True,
                                    reduced_motion='reduce')
            errors = []
            page.on('pageerror', lambda err: errors.append(str(err)))
            page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
            page.set_content(HTML, wait_until='load')
            page.locator('#status').wait_for()
            assert 'Analysis complete' in page.locator('#status').inner_text(), page.locator('#status').inner_text()
            assert 'mm' in page.locator('#disp-card').inner_text()
            assert page.locator('#plot line').count() >= 6
            assert page.locator('#member-results tr').count() == 3
            assert page.locator('#joint-results tr').count() == 3
            assert page.locator('#reactions tr').count() == 2
            results = page.evaluate('''() => { const r=ProMathTrussFEM.solve(ProMathTrussFEM.examples.triangle);
              return [r.reactions[0].ry,r.reactions[1].ry,r.maxDisplacement.magnitude,r.residual,r.energyError]; }''')
            assert abs(results[0] - 10000) < 1e-6 and abs(results[1] - 10000) < 1e-6
            assert results[2] > 0 and results[3] < 1e-10 and results[4] < 1e-10
            # The section helper is intentionally collapsed with the material breakdown.
            # Exercise the real disclosure before interacting with its controls at both widths.
            details = page.locator('#member-material-details')
            content = page.locator('#member-material-content')
            assert not details.evaluate('(node) => node.open'), 'member details should start collapsed'
            assert not content.is_visible(), 'controlled content should be hidden while collapsed'
            summary = details.locator('summary')
            assert summary.inner_text().strip() == 'Member materials and section properties'
            assert summary.get_attribute('aria-controls') == 'member-material-content'
            summary.click()
            assert details.evaluate('(node) => node.open'), 'summary activation should expand member details'
            assert content.is_visible(), 'summary should reveal its controlled content region'
            page.locator('#section-helper').wait_for(state='visible')
            page.locator('#section-member').wait_for(state='visible')
            # A very thin concentric annulus must retain high-precision section properties
            # through the actual helper preview and selected-member application at both widths.
            page.locator('#section-member').select_option('AB')
            page.locator('#section-shape').select_option('hollow-circle')
            page.locator('#section-diameter').fill('1000000')
            page.locator('#section-inner-diameter').fill('999999.9999999')
            circle_caption = page.locator('#section-sketch-caption').inner_text()
            assert circle_caption.startswith('Hollow circle Do='), circle_caption
            assert page.locator('#section-sketch').get_attribute('aria-label') == circle_caption
            assert page.locator('#section-sketch circle[data-centroid]').count() == 1
            assert page.locator('#section-sketch line[data-centroid-axis]').count() == 2
            before_section = page.evaluate("""() => Object.fromEntries(
                [...document.querySelectorAll('#members tr')].map(row => {
                    const id = row.querySelector('input[data-field="id"]')?.value;
                    return id ? [id, Object.fromEntries(
                        [...row.querySelectorAll('input[data-field]')].map(input => [input.dataset.field, input.value])
                    )] : null;
                }).filter(Boolean)
            )""")
            assert set(before_section) == {'AB', 'AC', 'BC'}, before_section
            page.locator('#section-properties-apply').click()
            assert page.locator('#section-result').inner_text().startswith('Hollow circle: area ')
            after_section = page.evaluate("""() => Object.fromEntries(
                [...document.querySelectorAll('#members tr')].map(row => {
                    const id = row.querySelector('input[data-field="id"]')?.value;
                    return id ? [id, Object.fromEntries(
                        [...row.querySelectorAll('input[data-field]')].map(input => [input.dataset.field, input.value])
                    )] : null;
                }).filter(Boolean)
            )""")
            expected_circle_area = 0.15708082876130342
            expected_circle_moment = 19635103595.160965
            assert abs(float(after_section['AB']['area']) - expected_circle_area) <= expected_circle_area * 1e-12
            assert abs(float(after_section['AB']['I']) - expected_circle_moment) <= expected_circle_moment * 1e-12
            for field, value in before_section['AB'].items():
                if field not in ('area', 'I'):
                    assert after_section['AB'][field] == value, (field, before_section['AB'], after_section['AB'])
            assert after_section['AC'] == before_section['AC']
            assert after_section['BC'] == before_section['BC']
            # Restore the original member section before the remaining solver regressions.
            page.evaluate("""(original) => {
                const row = [...document.querySelectorAll('#members tr')].find(
                    item => item.querySelector('input[data-field="id"]')?.value === 'AB');
                for (const field of ['area', 'I']) {
                    const input = row.querySelector('input[data-field="' + field + '"]');
                    input.value = original[field];
                    input.dispatchEvent(new Event('input', {bubbles:true}));
                    input.dispatchEvent(new Event('change', {bubbles:true}));
                }
            }""", before_section['AB'])
            # A normal L-angle stays on the true-scale preview without a detail inset.
            page.locator('#section-shape').select_option('l-angle')
            page.locator('#section-width').fill('100')
            page.locator('#section-height').fill('80')
            page.locator('#section-angle-thickness').fill('10')
            assert page.locator('#section-sketch path[data-section-outline="l-angle"]').count() == 1
            assert page.locator('#section-sketch path[data-section-detail="l-angle"]').count() == 0
            # An extreme-aspect L-angle keeps its measured outline at true scale and
            # adds an explicitly labelled detail inset for its sub-pixel leg thickness.
            page.locator('#section-width').fill('1000000')
            page.locator('#section-height').fill('1')
            page.locator('#section-angle-thickness').fill('0.001')
            angle_caption = page.locator('#section-sketch-caption').inner_text()
            assert 'L-angle B=' in angle_caption and 't=0.001 mm' in angle_caption
            assert 'Magnified leg detail shown below is not to scale.' in angle_caption
            sketch = page.locator('#section-sketch')
            assert sketch.get_attribute('aria-label') == angle_caption
            assert page.locator('#section-sketch-desc').text_content().strip() == angle_caption
            outline = page.locator('#section-sketch path[data-section-outline="l-angle"]')
            assert outline.count() == 1
            assert outline.get_attribute('data-section-width-mm') == '1000000'
            assert outline.get_attribute('data-section-height-mm') == '1'
            assert outline.get_attribute('data-section-thickness-mm') == '0.001'
            assert page.locator('#section-sketch rect[data-section-detail-frame="l-angle"]').count() == 1
            assert page.locator('#section-sketch path[data-section-detail="l-angle"]').count() == 1
            assert page.locator('#section-sketch [data-section-detail-label="l-angle"]').text_content().strip() == 'Leg detail — not to scale'
            assert page.locator('#section-sketch line[data-principal-axis]').count() == 2
            assert page.locator('#section-axis').input_value() == 'principal-major'
            before_angle = page.evaluate("""() => Object.fromEntries(
                [...document.querySelectorAll('#members tr')].map(row => {
                    const id = row.querySelector('input[data-field="id"]')?.value;
                    return id ? [id, Object.fromEntries(
                        [...row.querySelectorAll('input[data-field]')].map(input => [input.dataset.field, input.value])
                    )] : null;
                }).filter(Boolean)
            )""")
            page.locator('#section-properties-apply').click()
            assert page.locator('#section-result').inner_text().startswith('L-angle (web left, bottom leg right): area ')
            after_angle = page.evaluate("""() => Object.fromEntries(
                [...document.querySelectorAll('#members tr')].map(row => {
                    const id = row.querySelector('input[data-field="id"]')?.value;
                    return id ? [id, Object.fromEntries(
                        [...row.querySelectorAll('input[data-field]')].map(input => [input.dataset.field, input.value])
                    )] : null;
                }).filter(Boolean)
            )""")
            expected_angle_area = 1000.000999
            expected_angle_major = 83333583083083.333
            assert abs(float(after_angle['AB']['area']) - expected_angle_area) <= expected_angle_area * 1e-12
            assert abs(float(after_angle['AB']['I']) - expected_angle_major) <= expected_angle_major * 1e-12
            for field, value in before_angle['AB'].items():
                if field not in ('area', 'I'):
                    assert after_angle['AB'][field] == value, (field, before_angle['AB'], after_angle['AB'])
            assert after_angle['AC'] == before_angle['AC']
            assert after_angle['BC'] == before_angle['BC']
            page.evaluate("""(original) => {
                const row = [...document.querySelectorAll('#members tr')].find(
                    item => item.querySelector('input[data-field="id"]')?.value === 'AB');
                for (const field of ['area', 'I']) {
                    const input = row.querySelector('input[data-field="' + field + '"]');
                    input.value = original[field];
                    input.dispatchEvent(new Event('input', {bubbles:true}));
                    input.dispatchEvent(new Event('change', {bubbles:true}));
                }
            }""", before_angle['AB'])
            # Complete the seven-shape browser matrix: solid-circle application plus channel/I-section
            # axis mapping, selected-member isolation and truthful sub-pixel web/flange details.
            def section_member_snapshot():
                return page.evaluate("""() => Object.fromEntries(
                    [...document.querySelectorAll('#members tr')].map(row => {
                        const id = row.querySelector('input[data-field="id"]')?.value;
                        return id ? [id, Object.fromEntries(
                            [...row.querySelectorAll('input[data-field]')].map(input => [input.dataset.field, input.value])
                        )] : null;
                    }).filter(Boolean)
                )""")

            def restore_section_member(member_id, original):
                page.evaluate("""(args) => {
                    const row = [...document.querySelectorAll('#members tr')].find(
                        item => item.querySelector('input[data-field="id"]')?.value === args.id);
                    for (const field of ['area', 'I']) {
                        const input = row.querySelector('input[data-field="' + field + '"]');
                        input.value = args.original[field];
                        input.dispatchEvent(new Event('input', {bubbles:true}));
                        input.dispatchEvent(new Event('change', {bubbles:true}));
                    }
                }""", {'id': member_id, 'original': original[member_id]})

            # Solid-circle preview and application must use the circular I=pi*D^4/64 path.
            page.locator('#section-shape').select_option('solid-circle')
            page.locator('#section-diameter').fill('40')
            solid_circle_caption = page.locator('#section-sketch-caption').inner_text()
            assert solid_circle_caption.startswith('Solid circle D=40 mm'), solid_circle_caption
            assert page.locator('#section-sketch').get_attribute('aria-label') == solid_circle_caption
            assert page.locator('#section-sketch circle[data-section-outline="solid-circle"]').count() == 1
            assert page.locator('#section-sketch line[data-centroid-axis]').count() == 2
            before_solid_circle = section_member_snapshot()
            page.locator('#section-member').select_option('AB')
            page.locator('#section-properties-apply').click()
            assert page.locator('#section-result').inner_text().startswith('Solid circle: area ')
            after_solid_circle = section_member_snapshot()
            expected_solid_circle_area = 1256.6370614359173
            expected_solid_circle_moment = 125663.70614359172
            assert abs(float(after_solid_circle['AB']['area']) - expected_solid_circle_area) <= expected_solid_circle_area * 1e-12
            assert abs(float(after_solid_circle['AB']['I']) - expected_solid_circle_moment) <= expected_solid_circle_moment * 1e-12
            for field, value in before_solid_circle['AB'].items():
                if field not in ('area', 'I'):
                    assert after_solid_circle['AB'][field] == value, (field, before_solid_circle['AB'], after_solid_circle['AB'])
            assert after_solid_circle['AC'] == before_solid_circle['AC']
            assert after_solid_circle['BC'] == before_solid_circle['BC']
            restore_section_member('AB', before_solid_circle)

            # A solid circle's coefficient can make I finite even when the unscaled Do^4 overflows.
            page.locator('#section-shape').select_option('solid-circle')
            page.locator('#section-diameter').fill('2.45e77')
            range_solid_circle_caption = page.locator('#section-sketch-caption').inner_text()
            assert range_solid_circle_caption.startswith('Solid circle D='), range_solid_circle_caption
            assert page.locator('#section-sketch').get_attribute('aria-label') == range_solid_circle_caption
            assert page.locator('#section-sketch circle[data-section-outline="solid-circle"]').count() == 1
            before_range_solid_circle = section_member_snapshot()
            page.locator('#section-member').select_option('AC')
            page.locator('#section-properties-apply').click()
            assert page.locator('#section-result').inner_text().startswith('Solid circle: area ')
            after_range_solid_circle = section_member_snapshot()
            expected_range_solid_circle_area = 4.714352475793184e154
            expected_range_solid_circle_moment = 1.768618795996787e308
            assert abs(float(after_range_solid_circle['AC']['area']) - expected_range_solid_circle_area) <= expected_range_solid_circle_area * 5e-13
            assert abs(float(after_range_solid_circle['AC']['I']) - expected_range_solid_circle_moment) <= expected_range_solid_circle_moment * 5e-13
            for field, value in before_range_solid_circle['AC'].items():
                if field not in ('area', 'I'):
                    assert after_range_solid_circle['AC'][field] == value, (field, before_range_solid_circle['AC'], after_range_solid_circle['AC'])
            assert after_range_solid_circle['AB'] == before_range_solid_circle['AB']
            assert after_range_solid_circle['BC'] == before_range_solid_circle['BC']
            restore_section_member('AC', before_range_solid_circle)

            # A thin annulus can have a finite I even when Do^4 and Di^4 overflow.
            page.locator('#section-shape').select_option('hollow-circle')
            page.locator('#section-diameter').fill('1e78')
            page.locator('#section-inner-diameter').fill('9.999999999999998e77')
            range_circle_caption = page.locator('#section-sketch-caption').inner_text()
            assert range_circle_caption.startswith('Hollow circle Do='), range_circle_caption
            page.locator('#section-member').select_option('AC')
            before_range_circle = section_member_snapshot()
            page.locator('#section-properties-apply').click()
            assert page.locator('#section-result').inner_text().startswith('Hollow circle: area ')
            after_range_circle = section_member_snapshot()
            expected_range_circle_area = 3.230940642955516e140
            expected_range_circle_moment = 4.038675803694394e295
            assert abs(float(after_range_circle['AC']['area']) - expected_range_circle_area) <= expected_range_circle_area * 5e-13
            assert abs(float(after_range_circle['AC']['I']) - expected_range_circle_moment) <= expected_range_circle_moment * 5e-13
            for field, value in before_range_circle['AC'].items():
                if field not in ('area', 'I'):
                    assert after_range_circle['AC'][field] == value, (field, before_range_circle['AC'], after_range_circle['AC'])
            assert after_range_circle['AB'] == before_range_circle['AB']
            assert after_range_circle['BC'] == before_range_circle['BC']
            restore_section_member('AC', before_range_circle)

            for shape, expected_i_yy in (('channel', 2264380.9523809524), ('i-section', 1338666.6666666665)):
                page.locator('#section-shape').select_option(shape)
                page.locator('#section-width').fill('100')
                page.locator('#section-height').fill('80')
                page.locator('#section-web-thickness').fill('10')
                page.locator('#section-flange-thickness').fill('8')
                normal_caption = page.locator('#section-sketch-caption').inner_text()
                assert normal_caption.startswith('Open channel B=' if shape == 'channel' else 'I-section B='), normal_caption
                assert page.locator('#section-sketch').get_attribute('aria-label') == normal_caption
                assert page.locator('#section-sketch [data-section-outline="' + shape + '"]').count() == 1
                assert page.locator('#section-sketch [data-section-detail-frame]').count() == 0
                assert page.locator('#section-sketch line[data-centroid-axis]').count() == 2
                before_composite = section_member_snapshot()
                page.locator('#section-member').select_option('AC')
                page.locator('#section-axis').select_option('depth')
                page.locator('#section-properties-apply').click()
                assert page.locator('#section-result').inner_text().startswith(
                    'Open channel' if shape == 'channel' else 'I-section')
                after_composite = section_member_snapshot()
                assert abs(float(after_composite['AC']['area']) - 2240) <= 2240 * 1e-12
                assert abs(float(after_composite['AC']['I']) - expected_i_yy) <= expected_i_yy * 1e-12
                for field, value in before_composite['AC'].items():
                    if field not in ('area', 'I'):
                        assert after_composite['AC'][field] == value, (shape, field, before_composite['AC'], after_composite['AC'])
                assert after_composite['AB'] == before_composite['AB']
                assert after_composite['BC'] == before_composite['BC']
                restore_section_member('AC', before_composite)

                # At extreme but valid dimensions, the true-scale web/flanges are sub-pixel.
                # Keep the measured outline and axes, and add only a labelled schematic inset.
                page.locator('#section-width').fill('1000000')
                page.locator('#section-height').fill('1000000')
                page.locator('#section-web-thickness').fill('1')
                page.locator('#section-flange-thickness').fill('1')
                detail_caption = page.locator('#section-sketch-caption').inner_text()
                assert 'Magnified web/flange detail shown below is not to scale.' in detail_caption, detail_caption
                sketch = page.locator('#section-sketch')
                assert sketch.get_attribute('aria-label') == detail_caption
                assert page.locator('#section-sketch-desc').text_content().strip() == detail_caption
                outline = page.locator('#section-sketch [data-section-outline="' + shape + '"]')
                assert outline.count() == 1
                assert outline.get_attribute('data-section-width-mm') == '1000000'
                assert outline.get_attribute('data-section-height-mm') == '1000000'
                assert outline.get_attribute('data-web-thickness-mm') == '1'
                assert outline.get_attribute('data-flange-thickness-mm') == '1'
                assert page.locator('#section-sketch [data-section-detail-frame="' + shape + '"]').count() == 1
                assert page.locator('#section-sketch [data-section-detail="' + shape + '"]').count() == 1
                assert page.locator('#section-sketch [data-section-detail-label="' + shape + '"]').text_content().strip() == 'Web/flange detail — not to scale'
                assert page.locator('#section-sketch line[data-centroid-axis]').count() == 2
                assert page.locator('#section-sketch [data-centroid="true"]').count() == 1

            # Simulate an underconstrained joint, then recover without page reload.
            page.locator('#nodes tr').nth(1).locator('input[data-field="fixY"]').uncheck()
            page.get_by_role('button', name='Analyze truss').click()
            assert page.locator('#status.error').count() == 1
            page.locator('#nodes tr').nth(1).locator('input[data-field="fixY"]').check()
            page.get_by_role('button', name='Analyze truss').click()
            assert 'Analysis complete' in page.locator('#status').inner_text()
            assert '[object' not in page.locator('#status').inner_text()
            page.locator('#scale').fill('500')
            page.locator('#scale').press('Tab')
            assert '500' in page.locator('#plot').text_content()
            # Capture the actual generated download Blobs for a UI-level JSON round-trip.
            page.evaluate("""() => { window.__exports=[];
                const create=URL.createObjectURL.bind(URL);
                URL.createObjectURL = blob => {window.__exports.push({blob});return create(blob);};
                HTMLAnchorElement.prototype.click = function() { window.__exports.at(-1).name=this.download; };
            }""")
            legacy_model = {
                'nodes': [
                    {'id': 'A', 'x': 0, 'y': 0, 'fixX': True, 'fixY': True, 'fx': 0, 'fy': 0},
                    {'id': 'B', 'x': 2, 'y': 0, 'fixX': False, 'fixY': True, 'fx': 1000, 'fy': 0}
                ],
                'members': [
                    {'id': 'AB', 'a': 'A', 'b': 'B', 'E': 200e9, 'A': 0.001,
                     'density': 7850, 'I': 1e-6, 'K': 1}
                ]
            }
            page.locator('#import-model').set_input_files({
                'name': 'legacy-truss.json', 'mimeType': 'application/json',
                'buffer': json.dumps(legacy_model).encode('utf-8')
            })
            page.wait_for_function("""() => document.querySelector('#status').textContent.includes(
                'Legacy SI input converted to Studio units.')""")
            assert 'Optional property units in file: density kg/m³, I m⁴, K dimensionless.' in page.locator('#status').inner_text()
            assert page.locator('#nodes tr').count() == 2
            assert page.locator('#members tr').count() == 1
            assert page.locator('#nodes tr').nth(1).locator('input[data-field="fx"]').input_value() == '1'
            legacy_row = page.locator('#members tr').first
            assert legacy_row.locator('input[data-field="E"]').input_value() == '200'
            assert legacy_row.locator('input[data-field="area"]').input_value() == '1000'
            assert legacy_row.locator('input[data-field="density"]').input_value() == '7850'
            assert legacy_row.locator('input[data-field="I"]').input_value() == '1000000'
            assert legacy_row.locator('input[data-field="K"]').input_value() == '1'
            assert '0.01 mm' in page.locator('#disp-card').inner_text()

            page.get_by_role('button', name='Export JSON').click()
            current_export = page.evaluate("""async () => {
                const item=window.__exports.at(-1);
                return {name:item.name,type:item.blob.type,text:await item.blob.text()};
            }""")
            assert current_export['name'] == 'promath-truss-model.json'
            assert current_export['type'] == 'application/json;charset=utf-8'
            studio_model = json.loads(current_export['text'])
            assert float(studio_model['nodes'][1]['fx']) == 1
            assert float(studio_model['members'][0]['E']) == 200
            assert float(studio_model['members'][0]['area']) == 1000
            assert float(studio_model['members'][0]['density']) == 7850
            assert float(studio_model['members'][0]['I']) == 1000000
            assert float(studio_model['members'][0]['K']) == 1

            page.locator('#import-model').set_input_files({
                'name': 'studio-roundtrip.json', 'mimeType': 'application/json',
                'buffer': current_export['text'].encode('utf-8')
            })
            page.wait_for_function("""() => document.querySelector('#status').textContent.includes(
                'Studio units retained from file.')""")
            assert 'Optional property units in file: density kg/m³, I mm⁴, K dimensionless.' in page.locator('#status').inner_text()
            assert page.locator('#nodes tr').nth(1).locator('input[data-field="fx"]').input_value() == '1'
            studio_row = page.locator('#members tr').first
            assert studio_row.locator('input[data-field="E"]').input_value() == '200'
            assert studio_row.locator('input[data-field="area"]').input_value() == '1000'
            assert studio_row.locator('input[data-field="density"]').input_value() == '7850'
            assert studio_row.locator('input[data-field="I"]').input_value() == '1000000'
            assert studio_row.locator('input[data-field="K"]').input_value() == '1'
            displacement_before_rejection = page.locator('#disp-card').inner_text()

            mixed_model = json.loads(json.dumps(legacy_model))
            mixed_model['members'][0]['area'] = 1000
            page.locator('#import-model').set_input_files({
                'name': 'mixed-units.json', 'mimeType': 'application/json',
                'buffer': json.dumps(mixed_model).encode('utf-8')
            })
            page.wait_for_function("""() => document.querySelector('#status').classList.contains('error')""")
            assert 'Mixed legacy SI and current' in page.locator('#status').inner_text()
            assert page.locator('#nodes tr').count() == 2
            assert page.locator('#members tr').count() == 1
            assert page.locator('#members tr').first.locator('input[data-field="E"]').input_value() == '200'
            assert page.locator('#members tr').first.locator('input[data-field="area"]').input_value() == '1000'
            assert page.locator('#members tr').first.locator('input[data-field="density"]').input_value() == '7850'
            assert page.locator('#members tr').first.locator('input[data-field="I"]').input_value() == '1000000'
            assert page.locator('#members tr').first.locator('input[data-field="K"]').input_value() == '1'
            assert page.locator('#disp-card').inner_text() == displacement_before_rejection
            page.evaluate("window.__exports=[]")
            # Reset captured downloads before the CSV and SVG export assertions.
            page.evaluate('window.__exports=[]')
            page.get_by_role('button', name='Export results CSV').click()
            page.get_by_role('button', name='Export material schedule CSV').click()
            page.get_by_role('button', name='Export SVG').click()
            exported=page.evaluate("""async () => await Promise.all(window.__exports.map(async e => {
                const bytes = new Uint8Array(await e.blob.arrayBuffer());
                let bomCount=0;
                for(let i=0;i<=bytes.length-3;i++) {
                    if(bytes[i]===239&&bytes[i+1]===187&&bytes[i+2]===191) bomCount++;
                }
                return {name:e.name,type:e.blob.type,text:await e.blob.text(),
                        prefix:Array.from(bytes.slice(0,3)),bomCount};
            }))""")
            assert exported[0]['name'] == 'promath-truss-results.csv'
            assert exported[1]['name'] == 'promath-truss-material-schedule.csv'
            assert exported[2]['name'] == 'promath-truss-deformation.svg'
            for item in exported[:2]:
                assert item['prefix'] == [239, 187, 191], item['prefix']
                assert item['bomCount'] == 1, item['bomCount']
                content = item['text'].lstrip('\ufeff')
                assert content.endswith('\r\n')
                without_crlf = content.replace('\r\n', '')
                assert '\r' not in without_crlf and '\n' not in without_crlf
            result_csv = exported[0]['text'].lstrip('\ufeff')
            result_rows = list(csv.reader(io.StringIO(result_csv, newline='')))
            assert result_rows[0] == ['Member', 'Axial force (kN)', 'Stress (MPa)', 'Strain',
                                      'Euler utilization (%)', 'Euler load ratio Pcr/Pcomp (-)', 'Euler assessment']
            assert ['Joint', 'Ux (mm)', 'Uy (mm)'] in result_rows
            assert ['Support', 'Rx (kN)', 'Ry (kN)'] in result_rows
            assert sum(1 for row in result_rows if not row) == 2
            assert all(len(row) in (3, 7) for row in result_rows if row)
            member_rows = [row for row in result_rows if row and len(row) == 7]
            assert len(member_rows) == 2, member_rows  # header plus the imported AB member
            assert member_rows[1][0] == 'AB'
            assert abs(float(member_rows[1][1]) - 1.0) < 1e-12
            assert abs(float(member_rows[1][2]) - 1.0) < 1e-12
            material_csv = exported[1]['text'].lstrip('\ufeff')
            material_rows = list(csv.reader(io.StringIO(material_csv, newline='')))
            assert material_rows[0] == [
                'Member ID', 'Start joint ID', 'End joint ID', 'Centreline length (m)',
                'Cross-sectional area (m²)', 'Axial material volume (m³)', 'Elastic modulus (GPa)',
                'Axial stiffness EA/L (kN/mm)', 'Density (kg/m³)', 'Member mass (kg)',
                'Second moment of area I (mm⁴)', 'Effective length factor K (-)', 'Euler critical load Pcr (kN)'
            ]
            assert len(material_rows) == 2  # header plus the imported AB member
            assert all(len(row) == 13 for row in material_rows)
            assert material_rows[1][:3] == ['AB', 'A', 'B']
            assert float(material_rows[1][3]) == 2.0
            assert abs(float(material_rows[1][4]) - 0.001) < 1e-15  # schedule is SI m², not editor mm²
            assert abs(float(material_rows[1][5]) - 0.002) < 1e-15  # 2 m × 0.001 m²
            assert abs(float(material_rows[1][7]) - 100.0) < 1e-12  # EA/L in kN/mm
            assert abs(float(material_rows[1][9]) - 15.7) < 1e-12  # SI density × volume
            assert float(material_rows[1][6]) == 200.0
            assert float(material_rows[1][8]) == 7850.0
            assert float(material_rows[1][10]) == 1000000.0
            assert float(material_rows[1][11]) == 1.0
            svg_metadata = page.evaluate("""text => {
                const document = new DOMParser().parseFromString(text, 'image/svg+xml');
                const root = document.documentElement;
                const title = root.querySelector(':scope > title');
                const description = root.querySelector(':scope > desc');
                const labels = (root.getAttribute('aria-labelledby') || '').split(/\\s+/).filter(Boolean);
                const ids = new Set([...root.querySelectorAll('[id]')].map(node => node.id));
                return {
                    parseError: Boolean(document.querySelector('parsererror')),
                    namespace: root.namespaceURI,
                    width: root.getAttribute('width'),
                    height: root.getAttribute('height'),
                    viewBox: root.getAttribute('viewBox'),
                    preserveAspectRatio: root.getAttribute('preserveAspectRatio'),
                    role: root.getAttribute('role'),
                    labels,
                    labelsResolve: labels.length === 2 && labels.every(id => ids.has(id)),
                    titleId: title?.id || '',
                    title: title?.textContent || '',
                    descriptionId: description?.id || '',
                    description: description?.textContent || '',
                    firstChildren: [...root.children].slice(0, 3).map(node => node.localName),
                    background: root.querySelector(':scope > rect')?.getAttribute('fill') || '',
                    solvedLines: root.querySelectorAll('line').length,
                    geometry: [...root.querySelectorAll('line[data-geometry-role]')].map(line => ({
                        role: line.getAttribute('data-geometry-role'),
                        memberId: line.getAttribute('data-member-id'),
                        nodeId: line.getAttribute('data-node-id'),
                        forceState: line.getAttribute('data-force-state'),
                        loadFxKn: line.getAttribute('data-force-x-kN'),
                        loadFyKn: line.getAttribute('data-force-y-kN'),
                        arrowheadIndex: line.getAttribute('data-arrowhead-index')
                    })),
                    unclassifiedLines: root.querySelectorAll('line:not([data-geometry-role])').length
                };
            }""", exported[2]['text'])
            assert not svg_metadata['parseError'], svg_metadata
            assert svg_metadata['namespace'] == 'http://www.w3.org/2000/svg'
            assert (svg_metadata['width'], svg_metadata['height']) == ('1240', '760')
            assert svg_metadata['viewBox'] == '0 0 620 380'
            assert svg_metadata['preserveAspectRatio'] == 'xMidYMid meet'
            assert exported[2]['type'] == 'image/svg+xml;charset=utf-8'
            assert svg_metadata['role'] == 'img'
            assert svg_metadata['labels'] == ['truss-export-title', 'truss-export-description']
            assert svg_metadata['labelsResolve']
            assert svg_metadata['titleId'] == 'truss-export-title'
            assert svg_metadata['title'] == 'ProMathStudio truss deformation analysis'
            assert svg_metadata['descriptionId'] == 'truss-export-description'
            assert 'original truss members' in svg_metadata['description']
            assert 'tension or compression' in svg_metadata['description']
            assert svg_metadata['firstChildren'] == ['title', 'desc', 'rect']
            assert svg_metadata['background'] == '#09152a'
            assert svg_metadata['solvedLines'] == 5, svg_metadata
            assert svg_metadata['unclassifiedLines'] == 0, svg_metadata
            assert svg_metadata['geometry'] == [
                {'role':'original-member','memberId':'AB','nodeId':None,'forceState':None,
                 'loadFxKn':None,'loadFyKn':None,'arrowheadIndex':None},
                {'role':'deformed-member','memberId':'AB','nodeId':None,'forceState':'tension',
                 'loadFxKn':None,'loadFyKn':None,'arrowheadIndex':None},
                {'role':'applied-load','memberId':None,'nodeId':'B','forceState':None,
                 'loadFxKn':'1','loadFyKn':'0','arrowheadIndex':None},
                {'role':'load-arrowhead','memberId':None,'nodeId':'B','forceState':None,
                 'loadFxKn':None,'loadFyKn':None,'arrowheadIndex':'1'},
                {'role':'load-arrowhead','memberId':None,'nodeId':'B','forceState':None,
                 'loadFxKn':None,'loadFyKn':None,'arrowheadIndex':'2'}
            ], svg_metadata
            # Exercise the actual private CSV helper with an existing BOM and mixed newline styles.
            page.evaluate("""() => {
                window.__exports=[];
                window.__testDownloadCsv('serializer-normalization.csv',
                    '\\uFEFFh1,h2\\n1,2\\r3,4','text/csv;charset=utf-8');
                window.__testDownloadCsv('empty.csv','','text/csv;charset=utf-8');
            }""")
            normalized_csv = page.evaluate("""async () => {
                const item=window.__exports[0];
                const bytes=new Uint8Array(await item.blob.arrayBuffer());
                let bomCount=0;
                for(let i=0;i<=bytes.length-3;i++) {
                    if(bytes[i]===239&&bytes[i+1]===187&&bytes[i+2]===191) bomCount++;
                }
                return {name:item.name,type:item.blob.type,text:await item.blob.text(),
                        prefix:Array.from(bytes.slice(0,3)),tail:Array.from(bytes.slice(-2)),
                        emptyBytes:Array.from(new Uint8Array(await window.__exports[1].blob.arrayBuffer())),bomCount};
            }""")
            assert normalized_csv['name'] == 'serializer-normalization.csv'
            assert normalized_csv['type'] == 'text/csv;charset=utf-8'
            assert normalized_csv['prefix'] == [239, 187, 191]
            assert normalized_csv['bomCount'] == 1
            assert normalized_csv['tail'] == [13, 10], normalized_csv['tail']
            assert normalized_csv['emptyBytes'] == [239, 187, 191], normalized_csv['emptyBytes']
            assert normalized_csv['text'] == 'h1,h2\r\n1,2\r\n3,4\r\n'
            page.locator('#example').select_option('bar')
            page.get_by_role('button', name='Load example').click()
            assert page.locator('#member-results tr').count() == 1
            assert abs(page.evaluate('ProMathTrussFEM.solve(ProMathTrussFEM.examples.bar).displacements[1].x') - 1e-5) < 1e-12

            # Section properties apply atomically to one selected member only.
            page.locator('#example').select_option('triangle')
            page.get_by_role('button', name='Load example').click()
            assert page.locator('#members tr').count() == 3
            # The first section-helper scenario leaves this disclosure open. Reopening must
            # be idempotent: do not blindly click an already-open native summary and collapse it.
            details = page.locator('#member-material-details')
            if not details.evaluate('(node) => node.open'):
                details.locator('summary').click()
            assert details.evaluate('(node) => node.open'), 'member details must be open before helper use'
            assert page.locator('#member-material-content').is_visible()
            assert page.locator('#section-helper').is_visible()

            def section_member_snapshot():
                return page.evaluate("""() => [...document.querySelectorAll('#members tr')].map(tr =>
                    Object.fromEntries([...tr.querySelectorAll('input[data-field]')].map(input =>
                        [input.dataset.field, input.type === 'checkbox' ? input.checked : input.value])))""")

            distinct_member_values = [
                {'E': '190', 'area': '1100', 'density': '7800', 'I': '111000', 'K': '0.9'},
                {'E': '200', 'area': '1200', 'density': '7850', 'I': '222000', 'K': '1.1'},
                {'E': '210', 'area': '1300', 'density': '7900', 'I': '333000', 'K': '1.2'}
            ]
            for index, values in enumerate(distinct_member_values):
                row = page.locator('#members tr').nth(index)
                for field, value in values.items():
                    row.locator(f'input[data-field="{field}"]').fill(value)

            section_target = page.locator('#members tr').nth(1).locator('input[data-field="id"]').input_value()
            other_member_id = page.locator('#members tr').nth(2).locator('input[data-field="id"]').input_value()

            # Duplicate IDs make a target ambiguous; applying properties must not pick
            # the first matching row or modify any member until the ID is unique again.
            page.locator('#members tr').nth(2).locator('input[data-field="id"]').fill(section_target)
            page.locator('#section-member').select_option(section_target)
            section_before_ambiguous = section_member_snapshot()
            page.locator('#section-properties-apply').click()
            assert page.locator('#section-result').inner_text() == (
                'Not applied: Selected member ID is ambiguous.')
            assert section_member_snapshot() == section_before_ambiguous
            page.locator('#members tr').nth(2).locator('input[data-field="id"]').fill(other_member_id)
            page.locator('#section-member').select_option(section_target)
            page.locator('#section-shape').select_option('rectangle')
            page.locator('#section-axis').select_option('width')
            page.locator('#section-width').fill('40')
            page.locator('#section-height').fill('60')
            section_before_invalid_axis = section_member_snapshot()
            invalid_axis_value = page.locator('#section-axis').evaluate(
                "(select) => { select.value = 'unsupported-axis'; return select.value; }")
            assert invalid_axis_value == ''
            page.locator('#section-properties-apply').click()
            assert page.locator('#section-result').inner_text() == (
                'Not applied: Choose a valid section axis.')
            assert section_member_snapshot() == section_before_invalid_axis
            page.locator('#section-axis').select_option('width')
            section_before = section_member_snapshot()
            page.locator('#section-properties-apply').click()
            section_after = section_member_snapshot()
            assert section_after[1]['area'] == '2400', section_after
            assert section_after[1]['I'] == '720000', section_after
            for field, value in section_before[1].items():
                if field not in ('area', 'I'):
                    assert section_after[1][field] == value, (field, section_before, section_after)
            assert section_after[0] == section_before[0]
            assert section_after[2] == section_before[2]
            assert f'applied to member {section_target}.' in page.locator('#section-result').inner_text()

            # A successful application is current only while its geometry, target and axis stay unchanged.
            page.locator('#section-axis').select_option('depth')
            assert page.locator('#section-result').inner_text() == ''
            assert section_member_snapshot() == section_after
            page.locator('#section-axis').select_option('width')
            page.locator('#section-member').select_option('AB')
            assert page.locator('#section-result').inner_text() == ''
            assert section_member_snapshot() == section_after
            page.locator('#section-member').select_option(section_target)
            assert page.locator('#section-result').inner_text() == ''
            page.locator('#section-properties-apply').click()
            assert f'applied to member {section_target}.' in page.locator('#section-result').inner_text()
            section_after_current = section_member_snapshot()

            # Editing valid geometry clears the old success without mutating the applied member.
            page.locator('#section-height').fill('61')
            assert page.locator('#section-result').inner_text() == ''
            assert section_member_snapshot() == section_after_current
            page.locator('#section-height').fill('60')
            assert page.locator('#section-result').inner_text() == ''
            page.locator('#section-properties-apply').click()
            assert f'applied to member {section_target}.' in page.locator('#section-result').inner_text()

            # Invalid and overflowing geometry must leave every member unchanged.
            section_before_invalid = section_member_snapshot()
            page.locator('#section-width').fill('0')
            page.locator('#section-properties-apply').click()
            assert page.locator('#section-result').inner_text().startswith(
                'Not applied: Rectangle width and depth must be positive.')
            assert section_member_snapshot() == section_before_invalid
            page.locator('#section-width').fill('1e308')
            page.locator('#section-height').fill('1e308')
            page.locator('#section-properties-apply').click()
            assert page.locator('#section-result').inner_text().startswith('Not applied:')
            assert section_member_snapshot() == section_before_invalid

            # A very thin but representable hollow rectangle must retain its small net area
            # and positive bending inertias instead of subtracting nearly equal outer/inner values.
            page.locator('#section-shape').select_option('hollow-rectangle')
            page.locator('#section-width').fill('1000000')
            page.locator('#section-height').fill('1000000')
            page.locator('#section-inner-width').fill('999999.9999999')
            page.locator('#section-inner-height').fill('999999.9999999')
            page.locator('#section-axis').select_option('width')
            section_before_thin_wall = section_member_snapshot()
            page.locator('#section-properties-apply').click()
            section_after_thin_wall = section_member_snapshot()
            expected_thin_wall_area = 0.20000152289866402
            expected_thin_wall_moment = 33333587149.774002
            assert abs(float(section_after_thin_wall[1]['area']) - expected_thin_wall_area) <= expected_thin_wall_area * 1e-12
            assert abs(float(section_after_thin_wall[1]['I']) - expected_thin_wall_moment) <= expected_thin_wall_moment * 1e-12
            for field, value in section_before_thin_wall[1].items():
                if field not in ('area', 'I'):
                    assert section_after_thin_wall[1][field] == value, (field, section_before_thin_wall, section_after_thin_wall)
            assert section_after_thin_wall[0] == section_before_thin_wall[0]
            assert section_after_thin_wall[2] == section_before_thin_wall[2]
            assert 'Hollow rectangle' in page.locator('#section-result').inner_text()
            assert 'applied Ixx' in page.locator('#section-result').inner_text()

            # A thin hollow rectangle can have finite net inertias even when both
            # outer and inner solid-rectangle fourth-power intermediates overflow.
            extreme_hollow_rectangle = page.evaluate("""() => {
                const dimensions = {
                    width: 1e-10,
                    height: 1e110,
                    innerWidth: 9.999999999999998e-11,
                    innerHeight: 9.999999999999999e109
                };
                const oldOuterIxx = dimensions.width * dimensions.height *
                    dimensions.height * dimensions.height / 12;
                const oldInnerIxx = dimensions.innerWidth * dimensions.innerHeight *
                    dimensions.innerHeight * dimensions.innerHeight / 12;
                const section = ProMathTrussFEM.sectionProperties('hollow-rectangle', dimensions);
                return {
                    oldOuterOverflow: !Number.isFinite(oldOuterIxx),
                    oldInnerOverflow: !Number.isFinite(oldInnerIxx),
                    area: section.area,
                    ixx: section.secondMoment,
                    iyy: section.secondMomentPerpendicular,
                    sx: section.sectionModulusX,
                    sy: section.sectionModulusY,
                    rx: section.radiusOfGyrationX,
                    ry: section.radiusOfGyrationY,
                    cx: section.centroid.x,
                    cy: section.centroid.y
                };
            }""")
            assert extreme_hollow_rectangle['oldOuterOverflow']
            assert extreme_hollow_rectangle['oldInnerOverflow']
            expected_extreme_hollow_rectangle = {
                'area': 4.253679286041422e84,
                'ixx': 6.325965858056535e303,
                'iyy': 7.852965095414868e63,
                'sx': 1.2651931716113071e194,
                'sy': 1.5705930190829738e74,
                'rx': 3.856390911208362e109,
                'ry': 4.296694365821575e-11,
                'cx': 5e-11,
                'cy': 5e109
            }
            for key, expected in expected_extreme_hollow_rectangle.items():
                actual = extreme_hollow_rectangle[key]
                assert math.isfinite(actual) and abs(actual - expected) <= abs(expected) * 5e-13, (
                    key, actual, expected, extreme_hollow_rectangle)

            # A normalized L-angle determinant can underflow even when I2 is still a
            # representable subnormal; the browser engine must retain the Decimal reference.
            extreme_principal = page.evaluate("""() => {
                const section = ProMathTrussFEM.sectionProperties('l-angle', {
                    width: 1e100, height: 1e-139, thickness: 1e-140
                });
                const scale = Math.max(section.secondMoment, section.secondMomentPerpendicular,
                    Math.abs(section.productOfInertia));
                const ixx = section.secondMoment / scale;
                const iyy = section.secondMomentPerpendicular / scale;
                const ixy = section.productOfInertia / scale;
                return {
                    normalizedDeterminant: ixx * iyy - ixy * ixy,
                    minor: section.principalMomentMinor,
                    major: section.principalMomentMajor,
                    area: section.area,
                    sx: section.sectionModulusX, sy: section.sectionModulusY,
                    rx: section.radiusOfGyrationX, ry: section.radiusOfGyrationY,
                    angle: section.principalAxisAngleDegrees
                };
            }""")
            expected_extreme_minor = float(
                '8.333333333333333047120026461242959511255978638690079422571566289435343033091377208870550837651415192e-322')
            assert extreme_principal['normalizedDeterminant'] == 0
            assert extreme_principal['minor'] == expected_extreme_minor
            for key in ('major', 'area', 'sx', 'sy', 'rx', 'ry', 'angle'):
                assert math.isfinite(extreme_principal[key]) and extreme_principal[key] > 0, (
                    key, extreme_principal)
            
            # Restore the ordinary rectangle setup for the missing-destination-field test.
            page.locator('#section-shape').select_option('rectangle')
            page.locator('#section-width').fill('40')
            page.locator('#section-height').fill('60')

            # If either destination field is absent, preflight prevents a partial write.
            page.locator('#section-width').fill('40')
            page.locator('#section-height').fill('60')
            section_before_missing_field = section_member_snapshot()
            page.evaluate("""memberId => {
                const row = [...document.querySelectorAll('#members tr')].find(tr =>
                    tr.querySelector('input[data-field="id"]')?.value.trim() === memberId);
                row.querySelector('input[data-field="I"]').remove();
            }""", section_target)
            page.locator('#section-properties-apply').click()
            assert page.locator('#section-result').inner_text() == (
                'Not applied: Selected member row is missing area and I fields.')
            section_after_missing_field = section_member_snapshot()
            assert 'I' not in section_after_missing_field[1]
            assert section_after_missing_field[1]['area'] == section_before_missing_field[1]['area']
            for field in ('id', 'a', 'b', 'E', 'density', 'K'):
                assert section_after_missing_field[1][field] == section_before_missing_field[1][field]
            assert section_after_missing_field[0] == section_before_missing_field[0]
            assert section_after_missing_field[2] == section_before_missing_field[2]

            # Restore a clean one-member model for the subsequent asynchronous import tests.
            page.locator('#example').select_option('bar')
            page.get_by_role('button', name='Load example').click()
            # A pending file import must not overwrite edits made to the active model.
            slow_model = {
                'nodes': [
                    {'id': 'S', 'x': 0, 'y': 0, 'fixX': True, 'fixY': True, 'fx': 0, 'fy': 0},
                    {'id': 'T', 'x': 4, 'y': 0, 'fixX': False, 'fixY': True, 'fx': 1, 'fy': 0}
                ],
                'members': [{'id': 'ST', 'a': 'S', 'b': 'T', 'E': 200, 'area': 1000}]
            }
            page.evaluate("""() => {
                const original = File.prototype.arrayBuffer;
                window.__slowImportSettled = false;
                window.__releaseSlowImport = null;
                File.prototype.arrayBuffer = function() {
                    if (this.name !== 'delayed-import.json') return original.call(this);
                    const file = this;
                    return new Promise((resolve, reject) => {
                        window.__releaseSlowImport = () => {
                            File.prototype.arrayBuffer = original;
                            return original.call(file).then(bytes => {
                                window.__slowImportSettled = true;
                                resolve(bytes);
                            }, reject);
                        };
                    });
                };
            }""")
            page.locator('#import-model').set_input_files({
                'name': 'delayed-import.json', 'mimeType': 'application/json',
                'buffer': json.dumps(slow_model).encode('utf-8')
            })
            page.wait_for_function("window.__releaseSlowImport !== null")
            edited_length = page.locator('#nodes tr').nth(1).locator('input[data-field="x"]')
            edited_length.fill('3')
            # Repeated input/change invalidations must not erase the cancellation notice.
            edited_length.dispatch_event('change')
            assert 'Pending import cancelled because the model was edited.' in page.locator('#status').inner_text()
            assert page.locator('#status').get_attribute('aria-busy') == 'false'
            page.evaluate('window.__releaseSlowImport()')
            page.wait_for_function('window.__slowImportSettled === true')
            page.wait_for_timeout(20)
            assert [page.locator('#nodes tr').nth(i).locator('input[data-field="id"]').input_value()
                    for i in range(2)] == ['A', 'B']
            assert page.locator('#nodes tr').nth(1).locator('input[data-field="x"]').input_value() == '3'
            assert page.locator('#members tr').first.locator('input[data-field="id"]').input_value() == 'AB'
            assert 'Pending import cancelled because the model was edited.' in page.locator('#status').inner_text()
            page.get_by_role('button', name='Analyze truss').click()
            assert 'Analysis complete' in page.locator('#status').inner_text()
            assert '0.015 mm' in page.locator('#disp-card').inner_text()

            # File metadata and the actual bytes returned by the browser must agree.
            # The truncated payload is still valid JSON (only trailing whitespace is omitted),
            # so a parser-only check would silently accept it and replace the active model.
            mismatched_payload = (json.dumps(slow_model) + '          ').encode('utf-8')
            # Use a real File with immutable, correct size metadata. Override only this
            # instance's read method so the test deterministically simulates a short read
            # without changing File.prototype state left by earlier import-race coverage.
            page.evaluate("""payload => {
                const input = document.querySelector('#import-model');
                const file = new File([payload], 'mismatched-size.json', {type:'application/json'});
                const nativeRead = Blob.prototype.arrayBuffer;
                window.__mismatchRead = null;
                Object.defineProperty(file, 'arrayBuffer', {
                    configurable: true,
                    value: function() {
                        return nativeRead.call(this).then(bytes => {
                            window.__mismatchRead = {
                                name: this.name,
                                declared: this.size,
                                returned: bytes.byteLength - 10
                            };
                            return bytes.slice(0, bytes.byteLength - 10);
                        });
                    }
                });
                const transfer = new DataTransfer();
                transfer.items.add(file);
                input.files = transfer.files;
                input.dispatchEvent(new Event('change', {bubbles:true}));
            }""", mismatched_payload.decode('utf-8'))
            page.wait_for_function("""() => {
                const status = document.querySelector('#status');
                return window.__mismatchRead !== null &&
                       status?.textContent.includes('Model JSON file size does not match the bytes read.');
            }""")
            mismatch_read = page.evaluate('window.__mismatchRead')
            assert mismatch_read == {
                'name': 'mismatched-size.json',
                'declared': len(mismatched_payload),
                'returned': len(mismatched_payload) - 10
            }, mismatch_read
            mismatch_status = page.locator('#status').inner_text()
            assert mismatch_status.startswith(
                'Import failed: Model JSON file size does not match the bytes read. ('
            ), mismatch_status
            assert mismatch_status.endswith(
                f'(read returned fewer bytes than declared; expected {len(mismatched_payload)} bytes, '
                f'received {len(mismatched_payload) - 10} bytes).'
            ), mismatch_status
            assert [page.locator('#nodes tr').nth(i).locator('input[data-field="id"]').input_value()
                    for i in range(2)] == ['A', 'B']
            assert page.locator('#nodes tr').nth(1).locator('input[data-field="x"]').input_value() == '3'
            assert page.locator('#members tr').first.locator('input[data-field="id"]').input_value() == 'AB'
            assert '0.015 mm' in page.locator('#disp-card').inner_text()

            # Malformed UTF-8 bytes must fail before parsing or replacing the active model.
            def import_state_snapshot():
                return page.evaluate("""() => ({
                    nodes: [...document.querySelectorAll('#nodes tr')].map(tr =>
                        [...tr.querySelectorAll('input[data-field]')].map(input =>
                            [input.dataset.field, input.type === 'checkbox' ? input.checked : input.value])),
                    members: [...document.querySelectorAll('#members tr')].map(tr =>
                        [...tr.querySelectorAll('input[data-field]')].map(input =>
                            [input.dataset.field, input.type === 'checkbox' ? input.checked : input.value])),
                    solved: ['disp-card', 'stress-card', 'res-card', 'verification'].map(id =>
                        document.getElementById(id).textContent)
                })""")

            before_invalid_utf8 = import_state_snapshot()
            invalid_utf8_bytes = b'{"nodes":[{"id":"bad-\xc3("}],"members":[]}'
            page.locator('#import-model').set_input_files({
                'name': 'invalid-utf8.json', 'mimeType': 'application/json',
                'buffer': invalid_utf8_bytes
            })
            page.wait_for_function("""() => document.querySelector('#status').textContent ===
                'Import failed: Model JSON must be valid UTF-8.'""")
            assert page.locator('#status').get_attribute('aria-busy') == 'false'
            assert import_state_snapshot() == before_invalid_utf8

            # A subsequent valid file must recover normally after the rejected byte sequence.
            page.locator('#import-model').set_input_files({
                'name': 'utf8-recovery.json', 'mimeType': 'application/json',
                'buffer': json.dumps(slow_model).encode('utf-8')
            })
            page.wait_for_function("""() => document.querySelector('#status').textContent.includes(
                'Analysis complete')""")
            assert [page.locator('#nodes tr').nth(i).locator('input[data-field="id"]').input_value()
                    for i in range(2)] == ['S', 'T']
            assert page.locator('#members tr').first.locator('input[data-field="id"]').input_value() == 'ST'
            assert '0.02 mm' in page.locator('#disp-card').inner_text()
            assert page.locator('#status').get_attribute('aria-busy') == 'false'

            # A malformed File adapter result has a distinct diagnostic and cannot replace the model.
            before_invalid_length = import_state_snapshot()
            page.evaluate("""() => {
                const nativeRead = File.prototype.arrayBuffer;
                window.__restoreInvalidLengthRead = () => { File.prototype.arrayBuffer = nativeRead; };
                File.prototype.arrayBuffer = function() {
                    if (this.name === 'invalid-byte-length.json') return Promise.resolve({});
                    return nativeRead.call(this);
                };
            }""")
            page.locator('#import-model').set_input_files({
                'name': 'invalid-byte-length.json', 'mimeType': 'application/json',
                'buffer': json.dumps(slow_model).encode('utf-8')
            })
            page.wait_for_function("""() => document.querySelector('#status').textContent ===
                'Import failed: Model JSON read returned an invalid byte length.'""")
            page.evaluate('window.__restoreInvalidLengthRead()')
            assert import_state_snapshot() == before_invalid_length
            assert page.locator('#status').get_attribute('aria-busy') == 'false'

            # A real UTF-8 BOM is part of File.size; accept it at the exact 1 MiB boundary.
            exact_limit = 1024 * 1024
            bom_prefix = bytes((0xEF, 0xBB, 0xBF)) + json.dumps(slow_model, separators=(',', ':')).encode('utf-8')
            assert len(bom_prefix) < exact_limit
            bom_exact_payload = bom_prefix + b' ' * (exact_limit - len(bom_prefix))
            before_bom = import_state_snapshot()
            page.evaluate("""() => {
                const nativeRead = File.prototype.arrayBuffer;
                window.__bomRead = null;
                File.prototype.arrayBuffer = function() {
                    if (this.name !== 'bom-exact-boundary.json') return nativeRead.call(this);
                    return nativeRead.call(this).then(bytes => {
                        window.__bomRead = {
                            declared: this.size,
                            actual: bytes.byteLength,
                            prefix: Array.from(new Uint8Array(bytes).slice(0, 3))
                        };
                        File.prototype.arrayBuffer = nativeRead;
                        return bytes;
                    });
                };
            }""")
            page.locator('#import-model').set_input_files({
                'name': 'bom-exact-boundary.json', 'mimeType': 'application/json',
                'buffer': bom_exact_payload
            })
            page.wait_for_function("""() => window.__bomRead !== null &&
                document.querySelector('#status').textContent.includes('Studio units retained from file.')""")
            assert page.evaluate('window.__bomRead') == {
                'declared': exact_limit, 'actual': exact_limit, 'prefix': [239, 187, 191]
            }
            assert import_state_snapshot() == before_bom
            assert page.locator('#status').get_attribute('aria-busy') == 'false'

            # One byte beyond the limit is rejected from immutable File.size before reading.
            over_limit_payload = bom_exact_payload + b' '
            before_over_limit = import_state_snapshot()
            page.evaluate("""() => {
                const nativeRead = File.prototype.arrayBuffer;
                window.__oversizeReadStarted = false;
                window.__restoreOversizeRead = () => { File.prototype.arrayBuffer = nativeRead; };
                File.prototype.arrayBuffer = function() {
                    if (this.name === 'over-limit.json') window.__oversizeReadStarted = true;
                    return nativeRead.call(this);
                };
            }""")
            page.locator('#import-model').set_input_files({
                'name': 'over-limit.json', 'mimeType': 'application/json',
                'buffer': over_limit_payload
            })
            page.wait_for_function("""() => document.querySelector('#status').textContent ===
                'Import failed: Model JSON exceeds 1 MiB.'""")
            assert page.evaluate('window.__oversizeReadStarted') is False
            page.evaluate('window.__restoreOversizeRead()')
            assert import_state_snapshot() == before_over_limit
            assert page.locator('#status').get_attribute('aria-busy') == 'false'

            # A longer-than-declared read is also rejected before JSON parsing. The extra
            # byte is legal JSON whitespace, so parser-only validation would accept it.
            long_read_payload = json.dumps(slow_model, separators=(',', ':')).encode('utf-8')
            assert 0 < len(long_read_payload) < 1024 * 1024
            before_long_read = import_state_snapshot()
            page.evaluate("""payload => {
                const input = document.querySelector('#import-model');
                const file = new File([payload], 'long-read.json', {type:'application/json'});
                const nativeRead = Blob.prototype.arrayBuffer;
                window.__longRead = null;
                Object.defineProperty(file, 'arrayBuffer', {
                    configurable: true,
                    value: function() {
                        return nativeRead.call(this).then(bytes => {
                            const source = new Uint8Array(bytes);
                            const extended = new Uint8Array(source.byteLength + 1);
                            extended.set(source);
                            extended[source.byteLength] = 0x20;
                            window.__longRead = {
                                name: this.name,
                                declared: this.size,
                                returned: extended.byteLength
                            };
                            return extended.buffer;
                        });
                    }
                });
                const transfer = new DataTransfer();
                transfer.items.add(file);
                input.files = transfer.files;
                input.dispatchEvent(new Event('change', {bubbles:true}));
            }""", long_read_payload)
            page.wait_for_function("""() => {
                const status = document.querySelector('#status');
                return window.__longRead !== null &&
                       status?.textContent.includes('read returned more bytes than declared');
            }""")
            long_read = page.evaluate('window.__longRead')
            assert long_read == {
                'name': 'long-read.json',
                'declared': len(long_read_payload),
                'returned': len(long_read_payload) + 1
            }, long_read
            long_read_status = page.locator('#status').inner_text()
            assert long_read_status.startswith(
                'Import failed: Model JSON file size does not match the bytes read. ('
            ), long_read_status
            assert long_read_status.endswith(
                f'(read returned more bytes than declared; expected {len(long_read_payload)} bytes, '
                f'received {len(long_read_payload) + 1} bytes).'
            ), long_read_status
            assert import_state_snapshot() == before_long_read
            assert page.locator('#status').get_attribute('aria-busy') == 'false'

            # A newer file selection must win even when an older read resolves or rejects later.
            def race_model(prefix, length=2.0, load=1.0):
                return {
                    'nodes': [
                        {'id': prefix + '-A', 'x': 0, 'y': 0, 'fixX': True, 'fixY': True, 'fx': 0, 'fy': 0},
                        {'id': prefix + '-B', 'x': length, 'y': 0, 'fixX': False, 'fixY': True, 'fx': load, 'fy': 0}
                    ],
                    'members': [{'id': prefix + '-AB', 'a': prefix + '-A', 'b': prefix + '-B', 'E': 200, 'area': 1000}]
                }

            def start_delayed_import(name, model, key):
                page.evaluate("""({name, payload, key}) => {
                    const file = new File([payload], name, {type:'application/json'});
                    const nativeRead = Blob.prototype.arrayBuffer;
                    const pending = window[key] = {settled:false, release:null, reject:null};
                    Object.defineProperty(file, 'arrayBuffer', {
                        configurable:true,
                        value:function() {
                            const target = this;
                            return new Promise((resolve, reject) => {
                                pending.release = () => nativeRead.call(target).then(bytes => {
                                    pending.settled = true;
                                    resolve(bytes);
                                }, error => {
                                    pending.settled = true;
                                    reject(error);
                                });
                                pending.reject = error => {
                                    pending.settled = true;
                                    reject(error);
                                };
                            });
                        }
                    });
                    const transfer = new DataTransfer();
                    transfer.items.add(file);
                    const input = document.querySelector('#import-model');
                    input.files = transfer.files;
                    input.dispatchEvent(new Event('change', {bubbles:true}));
                }""", {'name': name, 'payload': json.dumps(model), 'key': key})
                page.wait_for_function(f"window.{key}.release !== null && window.{key}.reject !== null")

            def assert_race_model(prefix):
                assert page.locator('#nodes tr').nth(0).locator('input[data-field="id"]').input_value() == prefix + '-A'
                assert page.locator('#nodes tr').nth(1).locator('input[data-field="id"]').input_value() == prefix + '-B'
                assert page.locator('#members tr').first.locator('input[data-field="id"]').input_value() == prefix + '-AB'
                assert 'Analysis complete' in page.locator('#status').inner_text()
                assert page.locator('#status').get_attribute('aria-busy') == 'false'
                assert page.locator('#disp-card').inner_text().strip()

            # Older successful read after a newer successful import is ignored.
            start_delayed_import('older-success.json', race_model('OLD-SUCCESS', length=5), '__staleSuccess')
            page.locator('#import-model').set_input_files({
                'name': 'latest-success.json', 'mimeType': 'application/json',
                'buffer': json.dumps(race_model('LATEST-SUCCESS')).encode('utf-8')
            })
            page.wait_for_function("document.querySelector('#status')?.textContent.includes('Analysis complete')")
            assert_race_model('LATEST-SUCCESS')
            latest_success_status = page.locator('#status').inner_text()
            latest_success_result = page.locator('#disp-card').inner_text()
            page.evaluate('window.__staleSuccess.release()')
            page.wait_for_function('window.__staleSuccess.settled === true')
            page.wait_for_timeout(20)
            assert_race_model('LATEST-SUCCESS')
            assert page.locator('#status').inner_text() == latest_success_status
            assert page.locator('#disp-card').inner_text() == latest_success_result

            # An older rejected read after a newer successful import cannot replace its status.
            start_delayed_import('older-failure.json', race_model('OLD-FAILURE', length=6), '__staleFailure')
            page.locator('#import-model').set_input_files({
                'name': 'latest-after-failure.json', 'mimeType': 'application/json',
                'buffer': json.dumps(race_model('LATEST-AFTER-FAILURE', length=3)).encode('utf-8')
            })
            page.wait_for_function("document.querySelector('#status')?.textContent.includes('Analysis complete')")
            assert_race_model('LATEST-AFTER-FAILURE')
            latest_failure_status = page.locator('#status').inner_text()
            latest_failure_result = page.locator('#disp-card').inner_text()
            page.evaluate("window.__staleFailure.reject(new Error('deliberately stale read failure'))")
            page.wait_for_function('window.__staleFailure.settled === true')
            page.wait_for_timeout(20)
            assert_race_model('LATEST-AFTER-FAILURE')
            assert page.locator('#status').inner_text() == latest_failure_status
            assert page.locator('#disp-card').inner_text() == latest_failure_result

            # A newer rejected selection settles the current request; a previously pending
            # older success must not replace its diagnostic or clear its settled busy state.
            start_delayed_import('older-before-rejection.json',
                                 race_model('OLD-BEFORE-REJECTION', length=7),
                                 '__staleAfterRejectedSelection')
            before_newer_rejection = import_state_snapshot()
            page.locator('#import-model').set_input_files({
                'name': 'latest-invalid.json', 'mimeType': 'application/json',
                'buffer': b'{'
            })
            page.wait_for_function("""() => {
                const status = document.querySelector('#status');
                return status?.classList.contains('error') &&
                       status.textContent.startsWith('Import failed:');
            }""")
            newer_rejection_status = page.locator('#status').inner_text()
            assert page.locator('#status').get_attribute('aria-busy') == 'false'
            assert import_state_snapshot() == before_newer_rejection
            page.evaluate('window.__staleAfterRejectedSelection.release()')
            page.wait_for_function('window.__staleAfterRejectedSelection.settled === true')
            page.wait_for_timeout(20)
            assert import_state_snapshot() == before_newer_rejection
            assert page.locator('#status').inner_text() == newer_rejection_status
            assert page.locator('#status').get_attribute('aria-busy') == 'false'

            # Analyze explicitly cancels a pending import and keeps that decision visible.
            # A late successful read must not replace the current model or analysis status.
            start_delayed_import('cancelled-by-analyze-success.json',
                                 race_model('CANCELLED-BY-ANALYZE-SUCCESS', length=8),
                                 '__staleAfterAnalyzeSuccess')
            page.get_by_role('button', name='Analyze truss').click()
            page.wait_for_function("""() => {
                const status = document.querySelector('#status');
                return status?.textContent.includes('Analysis complete') &&
                       status.textContent.includes('Pending import cancelled; analysis used the current model.');
            }""")
            analyze_success_status = page.locator('#status').inner_text()
            analyze_success_snapshot = import_state_snapshot()
            assert page.locator('#status').get_attribute('aria-busy') == 'false'
            page.evaluate('window.__staleAfterAnalyzeSuccess.release()')
            page.wait_for_function('window.__staleAfterAnalyzeSuccess.settled === true')
            page.wait_for_timeout(20)
            assert import_state_snapshot() == analyze_success_snapshot
            assert page.locator('#status').inner_text() == analyze_success_status
            assert page.locator('#status').get_attribute('aria-busy') == 'false'

            # The same cancellation guard must ignore a late rejected read.
            start_delayed_import('cancelled-by-analyze-rejection.json',
                                 race_model('CANCELLED-BY-ANALYZE-REJECTION', length=9),
                                 '__staleAfterAnalyzeRejection')
            page.get_by_role('button', name='Analyze truss').click()
            page.wait_for_function("""() => {
                const status = document.querySelector('#status');
                return status?.textContent.includes('Analysis complete') &&
                       status.textContent.includes('Pending import cancelled; analysis used the current model.');
            }""")
            analyze_rejection_status = page.locator('#status').inner_text()
            analyze_rejection_snapshot = import_state_snapshot()
            assert page.locator('#status').get_attribute('aria-busy') == 'false'
            page.evaluate("window.__staleAfterAnalyzeRejection.reject(new Error('deliberately stale Analyze read failure'))")
            page.wait_for_function('window.__staleAfterAnalyzeRejection.settled === true')
            page.wait_for_timeout(20)
            assert import_state_snapshot() == analyze_rejection_snapshot
            assert page.locator('#status').inner_text() == analyze_rejection_status
            assert page.locator('#status').get_attribute('aria-busy') == 'false'

            # Layout is contained even on 390px viewport; inner tables scroll independently.
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2'), page.evaluate('''() => ({width: innerWidth, scroll:document.documentElement.scrollWidth, wide:[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>innerWidth+2).slice(0,12).map(e=>[e.tagName,e.id,e.className?.baseVal||e.className,Math.round(e.getBoundingClientRect().right)])})''')
            assert not errors, errors
            page.close()
        browser.close()
    print('Truss FEM reference, validation, graphics, export, keyboard and mobile checks passed')


if __name__ == '__main__':
    main()

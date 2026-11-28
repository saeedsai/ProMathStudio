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
            initial_preview = page.locator('#preview-summary').inner_text()
            assert 'mass estimate unavailable · 3 members missing density' in initial_preview, initial_preview
            energy_summary = page.locator('#energy-residual-summary')
            assert energy_summary.is_visible()
            assert 'Energy balance residual =' in energy_summary.inner_text()
            assert energy_summary.get_attribute('data-analysis-state') == 'valid'
            energy_references = page.evaluate("""() => {
                const result=ProMathTrussFEM.solve(ProMathTrussFEM.examples.triangle);
                const roundTrip=value=>Object.is(value,-0)?'-0':String(value);
                return {residual:roundTrip(result.energyResidual),error:roundTrip(result.energyError)};
            }""")
            assert energy_summary.get_attribute('data-energy-residual-j') == energy_references['residual']
            assert energy_summary.get_attribute('data-energy-error') == energy_references['error']
            assert not page.locator('#verification').is_visible()
            page.locator('#results details > summary').click()
            assert page.locator('#verification').is_visible()
            assert 'Energy balance residual =' in page.locator('#verification').inner_text()
            assert 'mm' in page.locator('#disp-card').inner_text()
            assert page.locator('#plot line').count() >= 6
            assert page.locator('#member-results tr').count() == 3
            assert page.locator('#joint-results tr').count() == 3
            assert page.locator('#reactions tr').count() == 2
            results = page.evaluate('''() => { const r=ProMathTrussFEM.solve(ProMathTrussFEM.examples.triangle);
              return [r.reactions[0].ry,r.reactions[1].ry,r.maxDisplacement.magnitude,r.residual,r.energyError]; }''')
            assert abs(results[0] - 10000) < 1e-6 and abs(results[1] - 10000) < 1e-6
            assert results[2] > 0 and results[3] < 1e-10 and results[4] < 1e-10

            # Aggregate preview totals must retain small same-sign member contributions.
            aggregate_totals = page.evaluate("""() => {
                const nodes = [
                    {id:'L0',x:0,y:0,fixX:true,fixY:true},
                    {id:'L1',x:1e16,y:0,fixX:true,fixY:true}
                ];
                const members = [{id:'LONG',a:'L0',b:'L1',E:200,area:1}];
                for (let i=0;i<20;i++) {
                    const a='S'+i+'A', b='S'+i+'B', y=10+i*2;
                    nodes.push({id:a,x:0,y,fixX:true,fixY:true},{id:b,x:1,y,fixX:true,fixY:true});
                    members.push({id:'M'+i,a,b,E:200,area:1});
                }
                const byId = new Map(nodes.map(node => [node.id,node]));
                const lengths = members.map(member => {
                    const a=byId.get(member.a), b=byId.get(member.b);
                    return Math.hypot(b.x-a.x,b.y-a.y);
                });
                const preview = ProMathTrussFEM.inspectJSON(JSON.stringify({nodes,members}));
                return {
                    totalMemberLength: preview.totalMemberLength,
                    totalMemberVolume: preview.totalMemberVolume,
                    naiveLength: lengths.reduce((sum,length) => sum+length,0),
                    naiveVolume: lengths.reduce((sum,length) => sum+length*1e-6,0)
                };
            }""")
            assert aggregate_totals['totalMemberLength'] == 10000000000000020, aggregate_totals
            assert aggregate_totals['totalMemberVolume'] == 10000000000.00002, aggregate_totals
            assert aggregate_totals['naiveLength'] != 10000000000000020, aggregate_totals
            assert aggregate_totals['naiveVolume'] != 10000000000.00002, aggregate_totals

            # A 2^55 J bar plus thirty-two 0.5 J bars gives an exact 2^55+16 J total.
            # Each small term is below half an ulp at the large member, so ordinary
            # member-order addition loses all 16 J while compensated summation retains them.
            energy_accumulation = page.evaluate("""() => {
                const nodes = [], members = [];
                for (let i=0;i<32;i++) {
                    const y=2*i, a='S'+i+'A', b='S'+i+'B';
                    nodes.push({id:a,x:0,y,fixX:true,fixY:true},
                        {id:b,x:1,y,fixY:true,fx:0.256,fy:0});
                    members.push({id:'S'+i,a,b,E:65.536,area:1});
                }
                nodes.push({id:'LA',x:0,y:64,fixX:true,fixY:true},
                    {id:'LB',x:1,y:64,fixY:true,fx:2**36/1000,fy:0});
                members.unshift({id:'LARGE',a:'LA',b:'LB',E:65.536,area:1});
                const result=ProMathTrussFEM.solve({nodes,members});
                const naiveEnergy=result.members.reduce((sum,member)=>sum+member.force*member.extension/2,0);
                return {naiveEnergy,elasticEnergy:result.elasticEnergy,energyResidual:result.energyResidual,
                    energyError:result.energyError,forceBalance:result.forceBalance.x};
            }""");
            # Playwright's JSON bridge emits shortest decimal text for JS binary64 values;
            # Python may parse an integer-looking token as an arbitrary-precision int. Convert
            # back to binary64 before exact comparison, preserving one-ULP sensitivity.
            assert float(2**55 + 8) != float(2**55), 'the fixture must distinguish one binary64 ulp'
            assert float(energy_accumulation['naiveEnergy']) == float(2**55), energy_accumulation
            assert float(energy_accumulation['elasticEnergy']) == float(2**55 + 16), energy_accumulation
            assert energy_accumulation['energyResidual'] == 0, energy_accumulation
            assert energy_accumulation['energyError'] == 0, energy_accumulation
            assert energy_accumulation['forceBalance'] == 0, energy_accumulation

            # Numeric text is decimal/scientific input, not JavaScript Number() radix coercion.
            numeric_string_contract = page.evaluate("""() => {
                const copy = model => JSON.parse(JSON.stringify(model));
                const valid = copy(ProMathTrussFEM.examples.bar);
                valid.nodes[1].fx = ' 1e3 ';
                valid.members[0].area = '1.0e3';
                const validDisplacement = ProMathTrussFEM.solve(valid).displacements[1].x;
                const invalid = ['0x10', '0b10', '0o10'].map(value => {
                    const model = copy(ProMathTrussFEM.examples.bar);
                    model.nodes[1].fx = value;
                    const message = action => {
                        try { action(); return null; } catch (error) { return error.message; }
                    };
                    return {
                        value,
                        parse: message(() => ProMathTrussFEM.parseModel(model)),
                        solve: message(() => ProMathTrussFEM.solve(model)),
                        section: message(() => ProMathTrussFEM.sectionProperties(
                            'rectangle', {width:value, height:2}))
                    };
                });
                const errorMessage = action => { try { action(); return null; } catch (error) { return error.message; } };
                const boundaryPaddedDecimal = ' '.repeat(255) + '1';
                const boundaryModel = copy(ProMathTrussFEM.examples.bar);
                boundaryModel.nodes[1].fx = boundaryPaddedDecimal;
                const boundary = {
                    parse: errorMessage(() => ProMathTrussFEM.parseModel(boundaryModel)),
                    displacement: ProMathTrussFEM.solve(boundaryModel).displacements[1].x,
                    area: ProMathTrussFEM.sectionProperties('rectangle', {width:boundaryPaddedDecimal, height:2}).area
                };
                const overlong = ['0'.repeat(256) + '1', ' '.repeat(256) + '1'].map(value => {
                    const model = copy(ProMathTrussFEM.examples.bar);
                    model.nodes[1].fx = value;
                    return {
                        valueLength: value.length,
                        number: Number(value),
                        parse: errorMessage(() => ProMathTrussFEM.parseModel(model)),
                        solve: errorMessage(() => ProMathTrussFEM.solve(model)),
                        section: errorMessage(() => ProMathTrussFEM.sectionProperties('rectangle', {width:value, height:2}))
                    };
                });
                return {validDisplacement, invalid, boundary, overlong};
            }""")
            assert abs(numeric_string_contract['validDisplacement'] / 0.01 - 1) <= 1e-13
            assert len(numeric_string_contract['invalid']) == 3
            for item in numeric_string_contract['invalid']:
                assert item['parse'].endswith('must be a finite number.'), item
                assert item['solve'].endswith('must be a finite number.'), item
                assert item['section'].endswith('must be a finite number.'), item
            assert numeric_string_contract['boundary']['parse'] is None
            assert numeric_string_contract['boundary']['displacement'] > 0
            assert numeric_string_contract['boundary']['area'] > 0
            assert len(numeric_string_contract['overlong']) == 2
            for item in numeric_string_contract['overlong']:
                assert item['valueLength'] == 257 and item['number'] == 1, item
                for key in ('parse', 'solve', 'section'):
                    assert item[key].endswith('must be a finite number.'), item
            # Signed resultants must survive overflowing partial sums and retain subnormal residuals.
            resultant_range = page.evaluate("""() => {
                const copy = model => JSON.parse(JSON.stringify(model));
                const horizontal = copy(ProMathTrussFEM.examples.bar);
                horizontal.nodes.forEach(node => { node.fx = 0; node.fy = 0; });
                horizontal.nodes.push({id:'C',x:1,y:0,fixX:true,fixY:true});
                horizontal.nodes[0].fx = 1e305;
                horizontal.nodes[1].fx = 1e305;
                horizontal.nodes[2].fx = -1e305;
                const naiveForceOverflow = !Number.isFinite(horizontal.nodes.reduce((sum,node) => sum + node.fx*1000, 0));
                const horizontalPreview = ProMathTrussFEM.inspectJSON(JSON.stringify(horizontal));

                const residual = copy(ProMathTrussFEM.examples.bar);
                residual.nodes.forEach(node => { node.fx = 0; node.fy = 0; });
                residual.nodes.push({id:'C',x:1,y:0,fixX:true,fixY:true});
                residual.nodes[0].fx = 1e305;
                residual.nodes[1].fx = Number.MIN_VALUE;
                residual.nodes[2].fx = -1e305;
                const naiveResidualLost = residual.nodes.reduce((sum,node) => sum + node.fx*1000, 0) === 0;
                const residualPreview = ProMathTrussFEM.inspectJSON(JSON.stringify(residual));

                const subnormalRatio = copy(ProMathTrussFEM.examples.bar);
                subnormalRatio.nodes.forEach(node => { node.fx = 0; node.fy = 0; });
                subnormalRatio.nodes.push({id:'C',x:1,y:0,fixX:true,fixY:true});
                subnormalRatio.nodes[0].fx = 1e305;
                subnormalRatio.nodes[1].fx = 1e-13;
                subnormalRatio.nodes[2].fx = -1e305;
                const naiveSubnormalRatioLost = subnormalRatio.nodes.reduce((sum,node) => sum + node.fx*1000, 0) === 0;
                const subnormalRatioPreview = ProMathTrussFEM.inspectJSON(JSON.stringify(subnormalRatio));

                const mixedScale = copy(ProMathTrussFEM.examples.bar);
                mixedScale.nodes = [
                    {id:'A',x:0,y:1,fixX:true,fixY:true,fx:1e305,fy:0},
                    {id:'B',x:2,y:1,fixX:true,fixY:true,fx:-1e305,fy:0},
                    ...Array.from({length:35},(_,i)=>({id:'P'+i,x:0,y:1,fx:0.0023,fy:0})),
                    ...Array.from({length:40},(_,i)=>({id:'N'+i,x:0,y:1,fx:-0.002,fy:0})),
                    {id:'C',x:0,y:1,fx:-0.0005,fy:0},
                    {id:'D',x:0,y:1,fx:1e-13,fy:0}
                ];
                const mixedScalePreview = ProMathTrussFEM.inspectJSON(JSON.stringify(mixedScale));
                const mixedScaleNaive = mixedScale.nodes.reduce((sum,node) => sum + node.fx*1000, 0);

                const vertical = copy(ProMathTrussFEM.examples.bar);
                vertical.nodes.forEach(node => { node.fx = 0; node.fy = 0; });
                vertical.nodes[1].x = 0; vertical.nodes[1].y = 2;
                vertical.nodes.push({id:'C',x:0,y:1,fixX:true,fixY:true});
                vertical.nodes[0].fy = 1e305;
                vertical.nodes[1].fy = 1e305;
                vertical.nodes[2].fy = -1e305;
                const verticalPreview = ProMathTrussFEM.inspectJSON(JSON.stringify(vertical));

                const moment = copy(ProMathTrussFEM.examples.bar);
                moment.nodes.forEach(node => { node.fx = 0; node.fy = 0; });
                moment.nodes[0].y = 1;
                moment.nodes[0].fx = -1e305;
                moment.nodes[1].fy = 5e304;
                moment.nodes.push({id:'C',x:1,y:0,fixX:true,fixY:true,fx:0,fy:-1e305});
                const naiveMomentOverflow = !Number.isFinite(moment.nodes.reduce(
                    (sum,node) => sum + node.x*(node.fy*1000) - node.y*(node.fx*1000), 0));
                const momentPreview = ProMathTrussFEM.inspectJSON(JSON.stringify(moment));

                const balanceModel = copy(ProMathTrussFEM.examples.triangle);
                balanceModel.nodes.forEach(node => {
                    node.fx = 0; node.fy = 0; node.fixX = true; node.fixY = true;
                });
                balanceModel.nodes[2].fixY = false;
                balanceModel.nodes[0].fx = 1e305;
                balanceModel.nodes[1].fx = 1e305;
                balanceModel.nodes[2].fx = -1e305;
                const balanceSolution = ProMathTrussFEM.solve(balanceModel);
                const naiveAppliedForce = balanceModel.nodes.reduce((sum,node) => sum + node.fx*1000, 0);
                const naiveReactionForce = balanceSolution.reactions.reduce((sum,reaction) => sum + reaction.rx, 0);
                const naiveForceBalanceNonFinite = !Number.isFinite(naiveAppliedForce + naiveReactionForce);

                const overflow = copy(ProMathTrussFEM.examples.bar);
                overflow.nodes[0].fx = 1e305;
                overflow.nodes[1].fx = 1e305;
                let overflowError = null;
                try { ProMathTrussFEM.inspectJSON(JSON.stringify(overflow)); }
                catch (error) { overflowError = error.message; }
                return {
                    naiveForceOverflow,
                    horizontalForce: horizontalPreview.appliedForce.x,
                    naiveResidualLost,
                    residualForce: residualPreview.appliedForce.x,
                    naiveSubnormalRatioLost,
                    subnormalRatioForce: subnormalRatioPreview.appliedForce.x,
                    mixedScaleForce: mixedScalePreview.appliedForce.x,
                    mixedScaleMoment: mixedScalePreview.appliedMoment,
                    mixedScaleNaive,
                    verticalForce: verticalPreview.appliedForce.y,
                    naiveMomentOverflow,
                    appliedMoment: momentPreview.appliedMoment,
                    momentForceX: momentPreview.appliedForce.x,
                    momentForceY: momentPreview.appliedForce.y,
                    naiveForceBalanceNonFinite,
                    forceBalanceX: balanceSolution.forceBalance.x,
                    forceBalanceY: balanceSolution.forceBalance.y,
                    overflowError
                };
            }""")
            assert resultant_range['naiveForceOverflow'] is True
            assert resultant_range['horizontalForce'] == 1e308
            assert resultant_range['naiveResidualLost'] is True
            assert resultant_range['residualForce'] == math.ulp(0.0) * 1000
            assert resultant_range['naiveSubnormalRatioLost'] is True
            assert resultant_range['subnormalRatioForce'] == 1e-10
            assert resultant_range['mixedScaleForce'] == 9.99937827510621e-11
            assert resultant_range['mixedScaleMoment'] == -9.99937827510621e-11
            assert abs(resultant_range['mixedScaleNaive'] - resultant_range['mixedScaleForce']) > 1e-14
            assert resultant_range['verticalForce'] == 1e308
            assert resultant_range['naiveMomentOverflow'] is True
            assert resultant_range['appliedMoment'] == 1e308
            assert resultant_range['momentForceX'] == -1e308
            assert resultant_range['momentForceY'] == -5e307
            assert resultant_range['overflowError'].startswith('Applied force x (N) must be a finite number.')
            assert resultant_range['naiveForceBalanceNonFinite'] is True
            assert resultant_range['forceBalanceX'] == 0
            assert resultant_range['forceBalanceY'] == 0
            reaction_precision = page.evaluate("""() => {
                const model = {
                    nodes: [
                        {id:'A',x:0,y:0,fixX:true,fixY:true},
                        {id:'B',x:1,y:0,fixY:true,fx:0.001},
                        {id:'C',x:1,y:0,fixY:true,fx:1e13},
                        {id:'D',x:1,y:0,fixY:true,fx:-1e13}
                    ],
                    members: [
                        {id:'AB',a:'A',b:'B',E:1e14,area:1000},
                        {id:'AC',a:'A',b:'C',E:1e14,area:1000},
                        {id:'AD',a:'A',b:'D',E:1e14,area:1000}
                    ]
                };
                const result = ProMathTrussFEM.solve(model);
                const stiffness = ProMathTrussFEM.parseModel(model).members[0].stiffness;
                const ux = id => result.displacements.find(node => node.id === id).x;
                const naiveReaction = ['B','C','D'].reduce((sum,id) => sum-stiffness*ux(id), 0);
                return {
                    naiveReaction,
                    supportReaction: result.reactions.find(reaction => reaction.id === 'A').rx,
                    forceBalance: result.forceBalance.x,
                    residual: result.residual,
                    energyError: result.energyError
                };
            }""")
            assert reaction_precision['naiveReaction'] == 0
            assert reaction_precision['supportReaction'] == -1
            assert reaction_precision['forceBalance'] == 0
            assert reaction_precision['residual'] < 1e-12
            assert reaction_precision['energyError'] < 1e-12
            # EA/L must remain representable when E*A alone overflows or underflows.
            stiffness_range = page.evaluate("""() => {
                const parseMember = (length, E, area, density) => ProMathTrussFEM.parseModel({
                    nodes: [{id:'A',x:0,y:0},{id:'B',x:length,y:0}],
                    members: [{id:'AB',a:'A',b:'B',E,area,density}]
                }).members[0];
                const parse = (length, E, area) => parseMember(length, E, area).stiffness;
                const overflowE = 1e299 * 1e9, overflowA = 1e308 * 1e-6;
                const underflowE = 1e-16 * 1e9, underflowA = 5e-315 * 1e-6;
                const volumeUnderflow = parseMember(2e-12, 1e299, 4.940656458412465e-318, 1e308);
                const volumeOverflow = parseMember(1e308, 1e-308, 1e308, 1e-310);
                return {
                    overflowIntermediate: !Number.isFinite(overflowE * overflowA),
                    overflowStiffness: parse(1e308, 1e299, 1e308),
                    underflowIntermediate: underflowE * underflowA === 0,
                    underflowStiffness: parse(2e-12, 1e-16, 5e-315),
                    volumeUnderflowIntermediate: volumeUnderflow.L * volumeUnderflow.A === 0,
                    massAfterVolumeUnderflow: volumeUnderflow.mass,
                    volumeOverflowIntermediate: !Number.isFinite(volumeOverflow.L * volumeOverflow.A),
                    massAfterVolumeOverflow: volumeOverflow.mass,
                    previewVolumeUnderflow: (() => {
                        try {
                            ProMathTrussFEM.inspectJSON(JSON.stringify({
                                nodes: [{id:'A',x:0,y:0},{id:'B',x:2e-12,y:0}],
                                members: [{id:'AB',a:'A',b:'B',E:1e299,area:4.940656458412465e-318,density:1e308}]
                            }));
                            return null;
                        } catch (error) { return error.message; }
                    })(),
                    massFinalUnderflow: (() => {
                        try {
                            parseMember(2e-12, 200, 5e-318, 1e-300);
                            return null;
                        } catch (error) { return error.message; }
                    })(),
                    zeroDensityMass: parseMember(2e-12, 200, 5e-318, 0).mass
                };
            }""")
            assert stiffness_range['overflowIntermediate'] is True
            assert stiffness_range['underflowIntermediate'] is True
            assert math.isfinite(stiffness_range['overflowStiffness'])
            assert abs(stiffness_range['overflowStiffness'] / 9.999999999999999e301 - 1) <= 5e-15
            assert stiffness_range['underflowStiffness'] > 0 and math.isfinite(stiffness_range['underflowStiffness'])
            assert abs(stiffness_range['underflowStiffness'] / 2.49997217e-316 - 1) <= 5e-15
            assert stiffness_range['volumeUnderflowIntermediate'] is True
            assert abs(stiffness_range['massAfterVolumeUnderflow'] / 9.88131291682493e-28 - 1) <= 5e-15
            assert stiffness_range['volumeOverflowIntermediate'] is True
            assert math.isfinite(stiffness_range['massAfterVolumeOverflow'])
            assert abs(stiffness_range['massAfterVolumeOverflow'] / 9.999999999999968e299 - 1) <= 5e-15
            assert isinstance(stiffness_range['previewVolumeUnderflow'], str)
            assert stiffness_range['previewVolumeUnderflow'].startswith('Member AB material volume underflow; increase dimensions.')
            assert isinstance(stiffness_range['massFinalUnderflow'], str)
            assert stiffness_range['massFinalUnderflow'].startswith('Member AB: mass underflow; increase dimensions or density.')
            assert stiffness_range['zeroDensityMass'] == 0
            # Optional Euler Pcr must survive numerator/effective-length intermediate range loss.
            euler_range = page.evaluate("""() => {
                const parse = (length, E, area, I, K) => ProMathTrussFEM.parseModel({
                    nodes: [{id:'A',x:0,y:0},{id:'B',x:length,y:0}],
                    members: [{id:'AB',a:'A',b:'B',E,area,I,K}]
                }).members[0];
                const large = parse(1e200, 1e291, 1e-100, 1e308, 1e200);
                const small = parse(2e-12, 1e-318, 1e300, 1e-310, 5e-151);
                return {
                    largeNumerator: Math.PI*Math.PI*large.E*large.secondMoment,
                    largeEffectiveLength: large.effectiveLengthFactor*large.L,
                    largeDenominator: (large.effectiveLengthFactor*large.L)**2,
                    largePcr: large.eulerCriticalLoad,
                    smallNumerator: Math.PI*Math.PI*small.E*small.secondMoment,
                    smallDenominator: (small.effectiveLengthFactor*small.L)**2,
                    smallPcr: small.eulerCriticalLoad
                };
            }""")
            assert math.isinf(euler_range['largeNumerator'])
            assert math.isinf(euler_range['largeEffectiveLength'])
            assert math.isinf(euler_range['largeDenominator'])
            assert abs(euler_range['largePcr'] / 9.869604401089358e-204 - 1) <= 5e-15
            assert euler_range['smallNumerator'] == 0
            assert euler_range['smallDenominator'] == 0
            assert abs(euler_range['smallPcr'] / 9.752452739990855e-307 - 1) <= 5e-15
            # An out-of-range Euler ratio must not invalidate an otherwise finite FEM solution.
            euler_ratio_range = page.evaluate("""() => {
                const solve = (E, area, I, fx) => ProMathTrussFEM.solve({
                    nodes: [{id:'A',x:0,y:0,fixX:true,fixY:true},
                            {id:'B',x:2,y:0,fixY:true,fx}],
                    members: [{id:'AB',a:'A',b:'B',E,area,I,K:1}]
                });
                const below = solve(200, 1e-300, 1e301, -2e-11);
                const above = solve(1e-300, 1e300, 4e-15, -2e-11);
                const underflow = solve(1e-300, 1e300, 2e-21, -0.002);
                return {
                    below: {force:below.members[0].force, utilization:below.members[0].eulerUtilization,
                        utilizationRange:below.members[0].eulerUtilizationRange,
                        loadRatio:below.members[0].eulerLoadRatio, loadRatioRange:below.members[0].eulerLoadRatioRange,
                        assessment:below.members[0].eulerAssessment, residual:below.residual, energyError:below.energyError},
                    above: {force:above.members[0].force, utilization:above.members[0].eulerUtilization,
                        utilizationRange:above.members[0].eulerUtilizationRange,
                        loadRatio:above.members[0].eulerLoadRatio, loadRatioRange:above.members[0].eulerLoadRatioRange,
                        assessment:above.members[0].eulerAssessment, residual:above.residual, energyError:above.energyError},
                    underflow: {pcr:underflow.members[0].eulerCriticalLoad, utilization:underflow.members[0].eulerUtilization,
                        utilizationRange:underflow.members[0].eulerUtilizationRange,
                        loadRatio:underflow.members[0].eulerLoadRatio, loadRatioRange:underflow.members[0].eulerLoadRatioRange,
                        assessment:underflow.members[0].eulerAssessment, residual:underflow.residual, energyError:underflow.energyError}
                };
            }""")
            assert euler_ratio_range['below']['force'] < 0
            assert euler_ratio_range['below']['utilization'] > 0
            assert euler_ratio_range['below']['utilizationRange'] is None
            assert euler_ratio_range['below']['loadRatio'] is None
            assert euler_ratio_range['below']['loadRatioRange'] == 'overflow'
            assert euler_ratio_range['below']['assessment'] == 'Below ideal Euler load (load ratio exceeds binary64 range)'
            assert math.isfinite(euler_ratio_range['below']['residual'])
            assert math.isfinite(euler_ratio_range['below']['energyError'])
            assert euler_ratio_range['above']['force'] < 0
            assert euler_ratio_range['above']['utilization'] is None
            assert euler_ratio_range['above']['utilizationRange'] == 'overflow'
            assert euler_ratio_range['above']['loadRatio'] > 0
            assert euler_ratio_range['above']['loadRatioRange'] is None
            assert euler_ratio_range['above']['assessment'] == 'At/above ideal Euler load (utilization exceeds binary64 range)'
            assert math.isfinite(euler_ratio_range['above']['residual'])
            assert math.isfinite(euler_ratio_range['above']['energyError'])
            assert euler_ratio_range['underflow']['pcr'] == 5e-324
            assert euler_ratio_range['underflow']['utilization'] is None
            assert euler_ratio_range['underflow']['utilizationRange'] == 'overflow'
            assert euler_ratio_range['underflow']['loadRatio'] is None
            assert euler_ratio_range['underflow']['loadRatioRange'] == 'underflow'
            assert euler_ratio_range['underflow']['assessment'] == 'At/above ideal Euler load (utilization exceeds binary64 range)'
            assert euler_ratio_range['underflow']['residual'] == 0
            assert euler_ratio_range['underflow']['energyError'] == 0
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
            # Exercise the compatibility path used when BigInt is unavailable.
            fallback = page.evaluate("""() => {
                const originalBigInt = window.BigInt;
                try {
                    window.BigInt = undefined;
                    const summary = section => ({
                        area: section.area, x: section.centroid.x, y: section.centroid.y,
                        ixx: section.secondMoment, iyy: section.secondMomentPerpendicular
                    });
                    return {
                        angle1: summary(ProMathTrussFEM.sectionProperties('l-angle', {
                            width: 8605413.972369973, height: 4.292204701476468,
                            thickness: 2.136125318978258e-5
                        })),
                        angle2: summary(ProMathTrussFEM.sectionProperties('l-angle', {
                            width: 1.1143751945503119e-20, height: 4.305111224234166e-16,
                            thickness: 2.015788401705846e-21
                        })),
                        channelArea: ProMathTrussFEM.sectionProperties('channel', {
                            width: 1e154, height: 1e154, webThickness: 1e-154,
                            flangeThickness: 6.661338147750939e-171
                        }).area,
                        iArea: ProMathTrussFEM.sectionProperties('i-section', {
                            width: 1e154, height: 1e154, webThickness: 1e-154,
                            flangeThickness: 6.661338147750939e-171
                        }).area,
                        channel: summary(ProMathTrussFEM.sectionProperties('channel', {
                            width: 2, height: 1, webThickness: 1, flangeThickness: 2e-17
                        })),
                        iSection: summary(ProMathTrussFEM.sectionProperties('i-section', {
                            width: 2, height: 1, webThickness: 1, flangeThickness: 2e-17
                        }))
                    };
                } finally {
                    window.BigInt = originalBigInt;
                }
            }""")
            assert fallback['angle1'] == {
                'area': 183.82251835310274, 'x': 4302704.840094387,
                'y': 1.1751052746539924e-5, 'ixx': 0.0005630523010274837,
                'iyy': 1134387503114039.5
            }, fallback['angle1']
            assert fallback['angle2'] == {
                'area': 8.678377274295314e-37, 'x': 1.0080123367146022e-21,
                'y': 2.1525099734807228e-16, 'ixx': 1.3404309505588713e-68,
                'iyy': 2.9455728539715605e-79
            }, fallback['angle2']
            assert fallback['channelArea'] == 1.0000000000000002
            assert fallback['iArea'] == 1.0000000000000002
            assert fallback['channel']['x'] == 0.5000000000000001
            assert fallback['channel']['ixx'] == 0.08333333333333334
            assert fallback['channel']['iyy'] == 0.08333333333333337
            assert fallback['iSection']['ixx'] == 0.08333333333333334
            assert fallback['iSection']['iyy'] == 0.08333333333333336

            # A slender L-angle can have finite Iyy and area while Iyy/area overflows;
            # the square-root-first radius calculation must remain finite in Chromium.
            slender = page.evaluate("""() => {
                const section = ProMathTrussFEM.sectionProperties('l-angle', {
                    width: 1e200, height: 1e100, thickness: 1e-293
                });
                return {
                    area: section.area,
                    secondMoment: section.secondMoment,
                    secondMomentPerpendicular: section.secondMomentPerpendicular,
                    radiusOfGyrationX: section.radiusOfGyrationX,
                    radiusOfGyrationY: section.radiusOfGyrationY
                };
            }""")
            assert not math.isfinite(slender['secondMomentPerpendicular'] / slender['area'])
            assert math.isfinite(slender['radiusOfGyrationY'])
            assert abs(slender['radiusOfGyrationY'] / 2.8867513459481287e199 - 1) <= 5e-13
            assert abs(slender['radiusOfGyrationX'] / 5.773502691896258e49 - 1) <= 5e-13

            # One L-angle axis can be subnormal while the other is normal; retain
            # geometric Sy/ry rather than dividing a quantized dimensional Iyy.
            mixed_axis = page.evaluate("""() => {
                const section = ProMathTrussFEM.sectionProperties('l-angle', {
                    width: 1e-60, height: 1e60, thickness: 1e-140
                });
                return {
                    iyy: section.secondMomentPerpendicular, area: section.area,
                    oldSy: section.secondMomentPerpendicular / section.extremeFiberDistanceAboutY,
                    oldRy: Math.sqrt(section.secondMomentPerpendicular / section.area),
                    sy: section.sectionModulusY, ry: section.radiusOfGyrationY
                };
            }""")
            assert 0 < mixed_axis['iyy'] < 2.2250738585072014e-308
            assert abs(mixed_axis['sy'] / 3.333333333333333e-261 - 1) <= 5e-13
            assert abs(mixed_axis['ry'] / 5.773502691896258e-121 - 1) <= 5e-13
            assert abs(mixed_axis['oldSy'] / mixed_axis['sy'] - 1) > 1e-4
            assert abs(mixed_axis['oldRy'] / mixed_axis['ry'] - 1) > 1e-4

            # Subnormal Ixx values remain finite but are too coarsely quantized for sqrt(I/A).
            # Rectangular radii must use the unrounded dimensionless geometry at both viewports.
            thin = page.evaluate("""() => {
                const solid = ProMathTrussFEM.sectionProperties('rectangle', {width: 1e-6, height: 3.5e-106});
                const hollow = ProMathTrussFEM.sectionProperties('hollow-rectangle', {
                    width: 1e-6, height: 3.5e-106, innerWidth: 5e-7, innerHeight: 1.75e-106
                });
                return {
                    solid: {area: solid.area, ixx: solid.secondMoment, rx: solid.radiusOfGyrationX, ry: solid.radiusOfGyrationY},
                    hollow: {area: hollow.area, ixx: hollow.secondMoment, rx: hollow.radiusOfGyrationX, ry: hollow.radiusOfGyrationY}
                };
            }""")
            assert thin['solid']['ixx'] == math.ulp(0.0)
            assert thin['hollow']['ixx'] == math.ulp(0.0)
            assert abs(thin['solid']['rx'] / (3.5e-106 / math.sqrt(12)) - 1) <= 2e-15
            assert abs(thin['solid']['ry'] / (1e-6 / math.sqrt(12)) - 1) <= 2e-15
            assert abs(math.sqrt(thin['solid']['ixx'] / thin['solid']['area']) /
                       (3.5e-106 / math.sqrt(12)) - 1) > 0.1
            bw, bh, bi, hi = 1e-6, 3.5e-106, 5e-7, 1.75e-106
            rb, rh = bi / bw, hi / bh
            gb, gh = (bw - bi) / bw, (bh - hi) / bh
            fa = gb + rb * gh
            fx = gb + rb * gh * (1 + rh + rh * rh)
            fy = gh + rh * gb * (1 + rb + rb * rb)
            assert abs(thin['hollow']['rx'] / (bh * math.sqrt(fx / fa / 12)) - 1) <= 2e-15
            assert abs(thin['hollow']['ry'] / (bw * math.sqrt(fy / fa / 12)) - 1) <= 2e-15
            assert abs(math.sqrt(thin['hollow']['ixx'] / thin['hollow']['area']) /
                       (bh * math.sqrt(fx / fa / 12)) - 1) > 0.1

            # Section moduli must use unrounded rectangle geometry when Ixx/Iyy are subnormal.
            # Dividing the quantized inertia by the extreme-fibre distance previously lost 2–4%.
            thin_moduli = page.evaluate("""() => {
                const dimensions = {width: 4.5e-81, height: 6e-81};
                const solid = ProMathTrussFEM.sectionProperties('rectangle', dimensions);
                const hollowDimensions = {...dimensions, innerWidth: 2.25e-81, innerHeight: 3e-81};
                const hollow = ProMathTrussFEM.sectionProperties('hollow-rectangle', hollowDimensions);
                return {
                    solid: {
                        ixx: solid.secondMoment, iyy: solid.secondMomentPerpendicular,
                        oldSx: solid.secondMoment / solid.extremeFiberDistanceAboutX,
                        oldSy: solid.secondMomentPerpendicular / solid.extremeFiberDistanceAboutY,
                        sx: solid.sectionModulusX, sy: solid.sectionModulusY
                    },
                    hollow: {
                        ixx: hollow.secondMoment, iyy: hollow.secondMomentPerpendicular,
                        oldSx: hollow.secondMoment / hollow.extremeFiberDistanceAboutX,
                        oldSy: hollow.secondMomentPerpendicular / hollow.extremeFiberDistanceAboutY,
                        sx: hollow.sectionModulusX, sy: hollow.sectionModulusY
                    }
                };
            }""")
            expected_moduli = {
                'solid': {'sx': 2.7e-242, 'sy': 2.025e-242},
                'hollow': {'sx': 2.53125e-242, 'sy': 1.8984375e-242}
            }
            for shape, expected in expected_moduli.items():
                result = thin_moduli[shape]
                assert 0 < result['ixx'] < 2.2250738585072014e-308, (shape, result)
                assert 0 < result['iyy'] < 2.2250738585072014e-308, (shape, result)
                assert abs(result['oldSx'] / expected['sx'] - 1) > 0.02, (shape, result)
                assert abs(result['oldSy'] / expected['sy'] - 1) > 0.02, (shape, result)
                assert abs(result['sx'] / expected['sx'] - 1) <= 5e-13, (shape, result)
                assert abs(result['sy'] / expected['sy'] - 1) <= 5e-13, (shape, result)

            # Circular I values can be subnormal while the exact radii remain representable.
            # Solid and hollow circles must use their analytic geometry rather than rounded I/A.
            thin_circles = page.evaluate("""() => {
                const diameter = 3e-81;
                const solid = ProMathTrussFEM.sectionProperties('solid-circle', {diameter});
                const hollowDimensions = {diameter, innerDiameter: 1.5e-81};
                const hollow = ProMathTrussFEM.sectionProperties('hollow-circle', hollowDimensions);
                const ratio = hollowDimensions.innerDiameter / hollowDimensions.diameter;
                return {
                    solid: {
                        area: solid.area, i: solid.secondMoment,
                        oldRadius: Math.sqrt(solid.secondMoment / solid.area),
                        rx: solid.radiusOfGyrationX, ry: solid.radiusOfGyrationY,
                        oldS: solid.secondMoment / solid.extremeFiberDistanceAboutX,
                        sx: solid.sectionModulusX, sy: solid.sectionModulusY,
                        expected: diameter / 4,
                        expectedS: 2.6507188014663876e-243
                    },
                    hollow: {
                        area: hollow.area, i: hollow.secondMoment,
                        oldRadius: Math.sqrt(hollow.secondMoment / hollow.area),
                        rx: hollow.radiusOfGyrationX, ry: hollow.radiusOfGyrationY,
                        oldS: hollow.secondMoment / hollow.extremeFiberDistanceAboutX,
                        sx: hollow.sectionModulusX, sy: hollow.sectionModulusY,
                        expected: (diameter / 4) * Math.sqrt(1 + ratio * ratio),
                        expectedS: 2.4850488763747383e-243
                    }
                };
            }""")
            for shape in ('solid', 'hollow'):
                assert thin_circles[shape]['i'] == math.ulp(0.0), (shape, thin_circles[shape])
                assert math.isfinite(thin_circles[shape]['area']) and thin_circles[shape]['area'] > 0
                assert abs(thin_circles[shape]['oldRadius'] / thin_circles[shape]['expected'] - 1) > 0.1
                assert abs(thin_circles[shape]['oldS'] / thin_circles[shape]['expectedS'] - 1) > 0.2
                for axis in ('rx', 'ry'):
                    assert abs(thin_circles[shape][axis] / thin_circles[shape]['expected'] - 1) <= 2e-15
                for axis in ('sx', 'sy'):
                    assert abs(thin_circles[shape][axis] / thin_circles[shape]['expectedS'] - 1) <= 5e-13

            # A tiny concentric cavity below half an ulp must round to the solid envelope.
            # The former product of complementary factors lost one ulp in both A and I.
            small_cavity_circle = page.evaluate("""() => {
                const dimensions = {diameter: 1, innerDiameter: 9.313225746154786e-14};
                const ratio = dimensions.innerDiameter / dimensions.diameter;
                const previousAreaFactor = ((dimensions.diameter - dimensions.innerDiameter) / dimensions.diameter) * (1 + ratio);
                const previousInertiaFactor = previousAreaFactor * (1 + ratio * ratio);
                const outerSquare = dimensions.diameter * dimensions.diameter;
                const previousArea = (Math.PI / 4) * outerSquare * previousAreaFactor;
                const previousMoment = (Math.PI / 64) * outerSquare * previousInertiaFactor * outerSquare;
                const solid = ProMathTrussFEM.sectionProperties('solid-circle', {diameter: dimensions.diameter});
                const hollow = ProMathTrussFEM.sectionProperties('hollow-circle', dimensions);
                const keys = ['area', 'secondMoment', 'secondMomentPerpendicular', 'sectionModulusX',
                    'sectionModulusY', 'radiusOfGyrationX', 'radiusOfGyrationY'];
                return {
                    previousAreaFactor, previousInertiaFactor, previousArea, previousMoment,
                    solidArea: solid.area, solidMoment: solid.secondMoment,
                    same: keys.every(key => hollow[key] === solid[key]),
                    centroidSame: JSON.stringify(hollow.centroid) === JSON.stringify(solid.centroid),
                    dimensionsUnchanged: dimensions.diameter === 1 && dimensions.innerDiameter === 9.313225746154786e-14
                };
            }""")
            assert small_cavity_circle['previousAreaFactor'] == 0.9999999999999999, small_cavity_circle
            assert small_cavity_circle['previousInertiaFactor'] == 0.9999999999999999, small_cavity_circle
            assert small_cavity_circle['previousArea'] != small_cavity_circle['solidArea'], small_cavity_circle
            assert small_cavity_circle['previousMoment'] != small_cavity_circle['solidMoment'], small_cavity_circle
            assert small_cavity_circle['same'] and small_cavity_circle['centroidSame'], small_cavity_circle
            assert small_cavity_circle['dimensionsUnchanged'], small_cavity_circle

            # A moderate cavity is still well-conditioned for direct 1-r² / 1-r⁴ differences.
            # The old complementary-product path loses one ulp immediately above r=0.5.
            transition_cavity_circle = page.evaluate("""() => {
                const dimensions = {diameter: 1, innerDiameter: 0.5000000000000001};
                const ratio = dimensions.innerDiameter / dimensions.diameter;
                const previousAreaFactor = (1 - ratio) * (1 + ratio);
                const previousInertiaFactor = previousAreaFactor * (1 + ratio * ratio);
                const previousArea = (Math.PI / 4) * previousAreaFactor;
                const previousMoment = (Math.PI / 64) * previousInertiaFactor;
                const section = ProMathTrussFEM.sectionProperties('hollow-circle', dimensions);
                return {
                    ratioSquared: ratio * ratio, previousArea, previousMoment,
                    area: section.area, ixx: section.secondMoment, iyy: section.secondMomentPerpendicular,
                    sx: section.sectionModulusX, sy: section.sectionModulusY,
                    rx: section.radiusOfGyrationX, ry: section.radiusOfGyrationY,
                    centroid: section.centroid,
                    dimensionsUnchanged: dimensions.diameter === 1 && dimensions.innerDiameter === 0.5000000000000001
                };
            }""")
            assert transition_cavity_circle['ratioSquared'] <= 0.5, transition_cavity_circle
            assert transition_cavity_circle['previousArea'] == 0.589048622548086, transition_cavity_circle
            assert transition_cavity_circle['previousMoment'] == 0.046019423636569225, transition_cavity_circle
            assert transition_cavity_circle['area'] == 0.5890486225480861, transition_cavity_circle
            assert transition_cavity_circle['ixx'] == 0.04601942363656923, transition_cavity_circle
            assert transition_cavity_circle['iyy'] == transition_cavity_circle['ixx'], transition_cavity_circle
            assert transition_cavity_circle['sx'] == 0.09203884727313846, transition_cavity_circle
            assert transition_cavity_circle['sy'] == transition_cavity_circle['sx'], transition_cavity_circle
            assert transition_cavity_circle['rx'] == 0.2795084971874737, transition_cavity_circle
            assert transition_cavity_circle['ry'] == transition_cavity_circle['rx'], transition_cavity_circle
            assert transition_cavity_circle['centroid'] == {'x': 0.5, 'y': 0.5}, transition_cavity_circle
            assert transition_cavity_circle['dimensionsUnchanged'], transition_cavity_circle

            # A hollow cavity's own area/square may underflow even when every net property is representable.
            # The ratio-based hollow helpers must accept these geometries at desktop and mobile widths.
            unresolved_cavities = page.evaluate("""() => {
                const rectangleDimensions = {
                    width: 1e100, height: 1e-100, innerWidth: 1e-162, innerHeight: 1e-162
                };
                const circleDimensions = {diameter: 1e-50, innerDiameter: 1e-200};
                const before = JSON.stringify([rectangleDimensions, circleDimensions]);
                const hollowRectangle = ProMathTrussFEM.sectionProperties('hollow-rectangle', rectangleDimensions);
                const solidRectangle = ProMathTrussFEM.sectionProperties('rectangle', {
                    width: rectangleDimensions.width, height: rectangleDimensions.height
                });
                const hollowCircle = ProMathTrussFEM.sectionProperties('hollow-circle', circleDimensions);
                const solidCircle = ProMathTrussFEM.sectionProperties('solid-circle', {
                    diameter: circleDimensions.diameter
                });
                const keys = ['area', 'secondMoment', 'secondMomentPerpendicular', 'sectionModulusX',
                    'sectionModulusY', 'radiusOfGyrationX', 'radiusOfGyrationY'];
                return {
                    rectangle: {
                        cavityArea: rectangleDimensions.innerWidth * rectangleDimensions.innerHeight,
                        same: keys.every(key => hollowRectangle[key] === solidRectangle[key]),
                        values: keys.map(key => hollowRectangle[key])
                    },
                    circle: {
                        innerSquare: circleDimensions.innerDiameter * circleDimensions.innerDiameter,
                        same: keys.every(key => hollowCircle[key] === solidCircle[key]),
                        values: keys.map(key => hollowCircle[key])
                    },
                    unchanged: JSON.stringify([rectangleDimensions, circleDimensions]) === before
                };
            }""")
            assert unresolved_cavities['rectangle']['cavityArea'] == 0, unresolved_cavities
            assert unresolved_cavities['circle']['innerSquare'] == 0, unresolved_cavities
            assert unresolved_cavities['rectangle']['same'], unresolved_cavities
            assert unresolved_cavities['circle']['same'], unresolved_cavities
            assert unresolved_cavities['unchanged'], unresolved_cavities
            for shape in ('rectangle', 'circle'):
                assert all(math.isfinite(value) and value > 0
                           for value in unresolved_cavities[shape]['values']), unresolved_cavities

            # Composite section inertias can be subnormal while both radii remain representable.
            # The normalized geometry path must avoid quantized physical I/A at desktop and mobile.
            composite_thin = page.evaluate("""() => {
                const scale = 10 ** -82.2;
                const references = {
                    channel: {rx: 2.0220658289055487e-81, ry: 2.0060914979751612e-81},
                    'i-section': {rx: 2.0220658289055487e-81, ry: 1.5424539802421713e-81}
                };
                return Object.fromEntries(Object.entries(references).map(([shape, expected]) => {
                    const section = ProMathTrussFEM.sectionProperties(shape, {
                        width: 100 * scale, height: 80 * scale,
                        webThickness: 10 * scale, flangeThickness: 8 * scale
                    });
                    return [shape, {
                        area: section.area, ixx: section.secondMoment, iyy: section.secondMomentPerpendicular,
                        oldRx: Math.sqrt(section.secondMoment / section.area),
                        oldRy: Math.sqrt(section.secondMomentPerpendicular / section.area),
                        rx: section.radiusOfGyrationX, ry: section.radiusOfGyrationY, expected
                    }];
                }));
            }""")
            for shape, result in composite_thin.items():
                assert result['area'] > 0 and math.isfinite(result['area']), (shape, result)
                assert 0 < result['ixx'] < 16 * math.ulp(0.0), (shape, result)
                assert 0 < result['iyy'] < 16 * math.ulp(0.0), (shape, result)
                assert abs(result['oldRx'] / result['expected']['rx'] - 1) > 0.01, (shape, result)
                assert abs(result['oldRy'] / result['expected']['ry'] - 1) > 0.01, (shape, result)
                assert abs(result['rx'] / result['expected']['rx'] - 1) <= 5e-13, (shape, result)
                assert abs(result['ry'] / result['expected']['ry'] - 1) <= 5e-13, (shape, result)

            # A symmetric I-section may have a positive central web whose area and local
            # inertias are below binary64 range while both flange-dominated axes remain valid.
            centered_web = page.evaluate("""() => {
                const dimensions = {
                    width: 1e100, height: 1e-100,
                    webThickness: Number.MIN_VALUE, flangeThickness: 1e-101
                };
                const webHeight = dimensions.height - 2 * dimensions.flangeThickness;
                const section = ProMathTrussFEM.sectionProperties('i-section', dimensions);
                let channelRejected = false;
                try { ProMathTrussFEM.sectionProperties('channel', dimensions); }
                catch (error) { channelRejected = /Composite section area underflow/.test(error.message); }
                return {
                    webArea: dimensions.webThickness * webHeight,
                    webCenterX: (dimensions.width - dimensions.webThickness) / 2 + dimensions.webThickness / 2,
                    webCenterY: dimensions.flangeThickness + webHeight / 2,
                    area: section.area, ixx: section.secondMoment, iyy: section.secondMomentPerpendicular,
                    sx: section.sectionModulusX, sy: section.sectionModulusY,
                    rx: section.radiusOfGyrationX, ry: section.radiusOfGyrationY,
                    cx: section.centroid.x, cy: section.centroid.y, channelRejected
                };
            }""")
            assert centered_web['webArea'] == 0, centered_web
            assert centered_web['webCenterX'] == 5e99 and centered_web['webCenterY'] == 5e-101, centered_web
            for key, expected in {
                'area': 0.2, 'ixx': 4.066666666666667e-202,
                'iyy': 1.6666666666666667e198, 'sx': 8.133333333333335e-102,
                'sy': 3.333333333333333e98, 'rx': 4.509249752822894e-101,
                'ry': 2.8867513459481287e99, 'cx': 5e99, 'cy': 5e-101
            }.items():
                assert math.isfinite(centered_web[key]) and abs(centered_web[key] / expected - 1) <= 5e-13, (key, centered_web)
            assert centered_web['channelRejected'], centered_web

            # An off-axis channel web may underflow only when its area, first moments,
            # local/offset inertias and both normalized contributions are all negligible.
            negligible_channel_web = page.evaluate("""() => {
                const dimensions = {
                    width: 1e40, height: 1e-100,
                    webThickness: Number.MIN_VALUE, flangeThickness: 2e-101
                };
                const section = ProMathTrussFEM.sectionProperties('channel', dimensions);
                return {
                    webArea: dimensions.webThickness * dimensions.height,
                    area: section.area, cx: section.centroid.x, cy: section.centroid.y,
                    ixx: section.secondMoment, iyy: section.secondMomentPerpendicular,
                    sx: section.sectionModulusX, sy: section.sectionModulusY,
                    rx: section.radiusOfGyrationX, ry: section.radiusOfGyrationY,
                    cX: section.extremeFiberDistanceAboutX, cY: section.extremeFiberDistanceAboutY
                };
            }""")
            assert negligible_channel_web['webArea'] == 0, negligible_channel_web
            for key, expected in {
                'area': 4e-61, 'cx': 5e39, 'cy': 5e-101,
                'ixx': 6.533333333333334e-262, 'iyy': 3.333333333333334e18,
                'sx': 1.306666666666667e-161, 'sy': 6.666666666666667e-22,
                'rx': 4.041451884327381e-101, 'ry': 2.886751345948129e39,
                'cX': 5e-101, 'cY': 5e39
            }.items():
                assert math.isfinite(negligible_channel_web[key]) and abs(negligible_channel_web[key] / expected - 1) <= 5e-13, (key, negligible_channel_web)

            # Dimensional Ixy may underflow while the normalized tensor still
            # determines finite principal moments and the principal-axis angle.
            product_underflow = page.evaluate("""() => {
                const dimensions = {
                    width: 1e-75, height: 1e-75,
                    thickness: 1e-75 * (1 - 1e-14)
                };
                const section = ProMathTrussFEM.sectionProperties('l-angle', dimensions);
                return {
                    area: section.area, ixx: section.secondMoment, iyy: section.secondMomentPerpendicular,
                    ixy: section.productOfInertia, major: section.principalMomentMajor,
                    minor: section.principalMomentMinor, angle: section.principalAxisAngleDegrees,
                    sx: section.sectionModulusX, sy: section.sectionModulusY,
                    rx: section.radiusOfGyrationX, ry: section.radiusOfGyrationY
                };
            }""")
            assert product_underflow['ixy'] == 0 and math.copysign(1.0, product_underflow['ixy']) == 1.0, product_underflow
            assert abs(product_underflow['angle'] - 45) <= 1e-12, product_underflow
            for key, expected in {
                'area': 9.999999999999999e-151,
                'ixx': 8.333333333333331e-302, 'iyy': 8.333333333333331e-302,
                'major': 8.333333333333331e-302, 'minor': 8.333333333333331e-302,
                'sx': 1.6666666666666664e-226, 'sy': 1.6666666666666664e-226,
                'rx': 2.886751345948129e-76, 'ry': 2.886751345948129e-76
            }.items():
                assert math.isfinite(product_underflow[key]) and abs(product_underflow[key] / expected - 1) <= 5e-13, (key, product_underflow)

            # Composite Sx/Sy must use normalized inertia and extreme-fibre geometry when
            # dimensional inertias are subnormal; I/c previously lost 5–24% here.
            composite_moduli = page.evaluate("""() => {
                const scale = 10 ** -82.2;
                const references = {
                    channel: {sx: 1.444703108127935e-242, sy: 9.048880575086456e-243},
                    'i-section': {sx: 1.444703108127935e-242, sy: 6.725157272628184e-243}
                };
                return Object.fromEntries(Object.entries(references).map(([shape, expected]) => {
                    const section = ProMathTrussFEM.sectionProperties(shape, {
                        width: 100 * scale, height: 80 * scale,
                        webThickness: 10 * scale, flangeThickness: 8 * scale
                    });
                    return [shape, {
                        area: section.area, ixx: section.secondMoment, iyy: section.secondMomentPerpendicular,
                        oldSx: section.secondMoment / section.extremeFiberDistanceAboutX,
                        oldSy: section.secondMomentPerpendicular / section.extremeFiberDistanceAboutY,
                        sx: section.sectionModulusX, sy: section.sectionModulusY, expected
                    }];
                }));
            }""")
            for shape, result in composite_moduli.items():
                assert result['area'] > 0 and math.isfinite(result['area']), (shape, result)
                assert 0 < result['ixx'] < 16 * math.ulp(0.0), (shape, result)
                assert 0 < result['iyy'] < 16 * math.ulp(0.0), (shape, result)
                assert abs(result['oldSx'] / result['expected']['sx'] - 1) > 0.04, (shape, result)
                assert abs(result['oldSy'] / result['expected']['sy'] - 1) > 0.04, (shape, result)
                assert abs(result['sx'] / result['expected']['sx'] - 1) <= 5e-13, (shape, result)
                assert abs(result['sy'] / result['expected']['sy'] - 1) <= 5e-13, (shape, result)

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
            preview_summary = page.locator('#preview-summary').inner_text()
            assert 'estimated total mass 15.7 kg' in preview_summary, preview_summary
            assert page.locator('#nodes tr').count() == 2
            assert page.locator('#members tr').count() == 1
            assert page.locator('#nodes tr').nth(1).locator('input[data-field="fx"]').input_value() == '1'
            legacy_row = page.locator('#members tr').first
            assert legacy_row.locator('input[data-field="E"]').input_value() == '200'
            assert legacy_row.locator('input[data-field="area"]').input_value() == '1000'
            assert legacy_row.locator('input[data-field="density"]').input_value() == '7850'
            assert legacy_row.locator('input[data-field="I"]').input_value() == '1000000'
            assert legacy_row.locator('input[data-field="K"]').input_value() == '1'
            partial_model = json.loads(json.dumps(legacy_model))
            partial_model['members'].append({
                'id': 'AB2', 'a': 'A', 'b': 'B', 'E': 200e9, 'A': 0.0005
            })
            page.locator('#import-model').set_input_files({
                'name': 'partial-density.json', 'mimeType': 'application/json',
                'buffer': json.dumps(partial_model).encode('utf-8')
            })
            page.wait_for_function("""() => document.querySelector('#status').textContent.includes(
                'Legacy SI input converted to Studio units.')""")
            partial_summary = page.locator('#preview-summary').inner_text()
            assert 'known mass subtotal 15.7 kg' in partial_summary, partial_summary
            assert '1 member missing density' in partial_summary, partial_summary
            assert page.locator('#members tr').count() == 2
            page.locator('#import-model').set_input_files({
                'name': 'legacy-truss-restored.json', 'mimeType': 'application/json',
                'buffer': json.dumps(legacy_model).encode('utf-8')
            })
            page.wait_for_function("""() => document.querySelector('#status').textContent.includes(
                'Legacy SI input converted to Studio units.')""")
            assert 'estimated total mass 15.7 kg' in page.locator('#preview-summary').inner_text()
            assert page.locator('#members tr').count() == 1
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
            
            # Subnormal L-angle moments lose precision if derived properties use rounded dimensional I values.
            low_exponent_angle = page.evaluate("""() => {
                const section = ProMathTrussFEM.sectionProperties('l-angle', {
                    width: 1e-80, height: 8e-81, thickness: 1e-81
                });
                return {
                    area: section.area, ixx: section.secondMoment, iyy: section.secondMomentPerpendicular,
                    ixy: section.productOfInertia, major: section.principalMomentMajor,
                    minor: section.principalMomentMinor, sx: section.sectionModulusX,
                    sy: section.sectionModulusY, rx: section.radiusOfGyrationX,
                    ry: section.radiusOfGyrationY, angle: section.principalAxisAngleDegrees,
                    cx: section.centroid.x, cy: section.centroid.y
                };
            }""")
            expected_low_exponent_subnormal = {
                'ixx': 9.4e-323, 'iyy': 1.7e-322, 'ixy': -7.4e-323,
                'major': 2.1e-322, 'minor': 5e-323
            }
            for key, expected in expected_low_exponent_subnormal.items():
                assert low_exponent_angle[key] == expected, (key, low_exponent_angle, expected)
            expected_low_exponent_regular = {
                'area': 1.7e-161,
                'cx': 3.1470588235294115e-81, 'cy': 2.1470588235294115e-81,
                'sx': 1.62822445561139e-242, 'sy': 2.4412732474964233e-242,
                'rx': 2.3676622822552844e-81, 'ry': 3.1370557534830907e-81,
                'angle': 57.953253999757194
            }
            for key, expected in expected_low_exponent_regular.items():
                actual = low_exponent_angle[key]
                assert math.isfinite(actual) and math.isclose(actual, expected, rel_tol=5e-13, abs_tol=0.0), (
                    key, actual, expected, low_exponent_angle)
            old_rx = math.sqrt(1e-322 / 1.7000000000000001e-161)
            old_ry = math.sqrt(1.63e-322 / 1.7000000000000001e-161)
            old_angle = 0.5 * math.degrees(math.atan2(-2 * -7.4e-323, 1e-322 - 1.63e-322))
            assert abs(old_rx - expected_low_exponent_regular['rx']) > expected_low_exponent_regular['rx'] * 0.01
            assert abs(old_ry - expected_low_exponent_regular['ry']) > expected_low_exponent_regular['ry'] * 0.01
            assert abs(old_angle - expected_low_exponent_regular['angle']) > 1.0

            # A max-dimension-only normalization loses the thin-axis inertia for B/H=1e304.
            # Axis-separated coordinates must retain representable radii and section moduli.
            extreme_aspect_composites = page.evaluate("""() => {
                const dimensions = {
                    width: 1e150, height: 1e-154,
                    webThickness: 1e-154, flangeThickness: 4.9e-155
                };
                return ['channel', 'i-section'].map(shape => {
                    const section = ProMathTrussFEM.sectionProperties(shape, dimensions);
                    return {
                        shape, area: section.area, ixx: section.secondMoment,
                        iyy: section.secondMomentPerpendicular,
                        sx: section.sectionModulusX, sy: section.sectionModulusY,
                        rx: section.radiusOfGyrationX, ry: section.radiusOfGyrationY,
                        oldRx: Math.sqrt(section.secondMoment / section.area),
                        oldSx: section.secondMoment / section.extremeFiberDistanceAboutX
                    };
                });
            }""")
            extreme_aspect_reference = {
                'rx': 2.9160475533388224e-155,
                'ry': 2.8867513459481288e149,
                'sx': 1.6666533333333332e-159,
                'sy': 1.6333333333333333e145
            }
            for section in extreme_aspect_composites:
                assert math.isfinite(section['area']) and section['area'] > 0, section
                assert 0 < section['ixx'] < 2.2250738585072014e-308, section
                assert section['iyy'] > 2.2250738585072014e-308, section
                assert abs(section['oldRx'] / extreme_aspect_reference['rx'] - 1) > 1e-11, section
                assert abs(section['oldSx'] / extreme_aspect_reference['sx'] - 1) > 1e-11, section
                for key, expected in extreme_aspect_reference.items():
                    assert math.isfinite(section[key]) and abs(section[key] / expected - 1) <= 5e-13, (
                        section['shape'], key, section[key], expected, section)

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

            # Small hollow-rectangle cavities must use the stable small-cavity path.
            small_cavity = page.evaluate("""() => {
                const dimensions = {width: 1, height: 1, innerWidth: 1.2e-16, innerHeight: 0.5};
                const section = ProMathTrussFEM.sectionProperties('hollow-rectangle', dimensions);
                const tiny = ProMathTrussFEM.sectionProperties('hollow-rectangle', {
                    width: 1, height: 1, innerWidth: 1.2e-16, innerHeight: 0.25
                });
                const smallIyy = ProMathTrussFEM.sectionProperties('hollow-rectangle', {
                    width: 1, height: 1, innerWidth: 1.1e-16, innerHeight: 0.51
                });
                const originalBigInt = window.BigInt;
                let fallback;
                try {
                    window.BigInt = undefined;
                    fallback = ProMathTrussFEM.sectionProperties('hollow-rectangle', dimensions);
                } finally { window.BigInt = originalBigInt; }
                return {
                    area: section.area, ixx: section.secondMoment, iyy: section.secondMomentPerpendicular,
                    rx: section.radiusOfGyrationX, ry: section.radiusOfGyrationY,
                    cx: section.centroid.x, cy: section.centroid.y,
                    tinyArea: tiny.area, smallIyy: smallIyy.secondMomentPerpendicular,
                    fallbackArea: fallback.area, fallbackIxx: fallback.secondMoment,
                    fallbackIyy: fallback.secondMomentPerpendicular
                };
            }""")
            assert small_cavity['area'] == 0.9999999999999999, small_cavity
            assert small_cavity['ixx'] == 0.08333333333333333, small_cavity
            assert small_cavity['iyy'] == 0.08333333333333333, small_cavity
            assert small_cavity['rx'] == 0.28867513459481287, small_cavity
            assert small_cavity['ry'] == 0.28867513459481287, small_cavity
            assert small_cavity['cx'] == 0.5 and small_cavity['cy'] == 0.5, small_cavity
            assert small_cavity['tinyArea'] == 1, small_cavity
            assert small_cavity['smallIyy'] == 0.08333333333333333, small_cavity
            assert small_cavity['fallbackArea'] == 0.9999999999999999, small_cavity
            assert small_cavity['fallbackIxx'] == 0.08333333333333333, small_cavity
            assert small_cavity['fallbackIyy'] == 0.08333333333333333, small_cavity

            # The global stiffness matrix must retain parallel-member terms that a naive
            # left-to-right += loses after a dominant member contribution.
            for width in (1280, 390):
                page.set_viewport_size({"width": width, "height": 850})
                stiffness = page.evaluate("""() => {
                    const model = {
                        nodes: [
                            {id:'A',x:0,y:0,fixX:true,fixY:true,fx:0,fy:0},
                            {id:'B',x:1,y:0,fixX:false,fixY:true,fx:1e13,fy:0}
                        ],
                        members: [
                            {id:'large',a:'A',b:'B',E:1e13,area:1},
                            ...Array.from({length:20},(_,i) => ({
                                id:'small-'+i,a:'A',b:'B',E:1e-6,area:1000
                            }))
                        ]
                    };
                    const naive = [1e16,...Array(20).fill(1)].reduce((sum,value) => sum+value,0);
                    const result = ProMathTrussFEM.solve(model);
                    return {
                        naive,
                        displacement: result.displacements.find(node => node.id === 'B').x,
                        residual: result.residual,
                        energyError: result.energyError,
                        memberCount: result.members.length
                    };
                }""")
                expected_displacement = 1e16 / (1e16 + 20)
                assert stiffness["naive"] == 1e16, stiffness
                assert abs(stiffness["displacement"] - expected_displacement) <= 2e-16, (width, stiffness)
                assert stiffness["displacement"] < 1 - 1e-15, (width, stiffness)
                assert stiffness["residual"] < 1e-6 and stiffness["energyError"] < 1e-6, (width, stiffness)
                assert stiffness["memberCount"] == 21, (width, stiffness)

                # Scale stiffness before direction-cosine products: the unscaled product
                # double-rounds each minimum-subnormal contribution upward.
                subnormal_stiffness = page.evaluate("""() => {
                    const model = {
                        nodes: [
                            {id:'A',x:0,y:0,fixX:true,fixY:true,fx:0,fy:0},
                            {id:'B',x:2e-12,y:2e-12,fixX:false,fixY:true,fx:Number.MIN_VALUE,fy:0}
                        ],
                        members: Array.from({length:20},(_,i) => ({
                            id:'S'+i,a:'A',b:'B',E:1e-323,area:1e-15
                        }))
                    };
                    const parsed = ProMathTrussFEM.parseModel(model);
                    const member = parsed.members[0];
                    const result = ProMathTrussFEM.solve(model);
                    const force = Number.MIN_VALUE*1000;
                    return {
                        memberStiffness: member.stiffness,
                        sequentialTerm: member.stiffness*member.c*member.c,
                        singleProduct: member.stiffness*(member.c*member.c),
                        expectedCoefficient: Number.MIN_VALUE*10,
                        naiveCoefficient: Number.MIN_VALUE*20,
                        displacement: result.displacements.find(node=>node.id==='B').x,
                        expectedDisplacement: force/(Number.MIN_VALUE*10),
                        naiveDisplacement: force/(Number.MIN_VALUE*20),
                        residual: result.residual,
                        energyError: result.energyError,
                        forceBalanceX: result.forceBalance.x,
                        memberCount: result.members.length
                    };
                }""")
                assert subnormal_stiffness["memberStiffness"] == math.ulp(0.0), subnormal_stiffness
                assert subnormal_stiffness["sequentialTerm"] == math.ulp(0.0), subnormal_stiffness
                assert subnormal_stiffness["singleProduct"] == 0, subnormal_stiffness
                assert subnormal_stiffness["expectedCoefficient"] == math.ulp(0.0)*10, subnormal_stiffness
                assert subnormal_stiffness["naiveCoefficient"] == math.ulp(0.0)*20, subnormal_stiffness
                assert subnormal_stiffness["expectedDisplacement"] == 100, subnormal_stiffness
                assert subnormal_stiffness["naiveDisplacement"] == 50, subnormal_stiffness
                assert subnormal_stiffness["displacement"] == 100, (width, subnormal_stiffness)
                assert subnormal_stiffness["residual"] == 0, (width, subnormal_stiffness)
                assert subnormal_stiffness["energyError"] < 1e-6, (width, subnormal_stiffness)
                assert subnormal_stiffness["forceBalanceX"] == 0, (width, subnormal_stiffness)
                assert subnormal_stiffness["memberCount"] == 20, (width, subnormal_stiffness)

            # Legacy SI values that become zero in kN/GPa must be rejected, not silently erased.
            legacy_unit_conversion = page.evaluate("""() => {
                const copy = () => JSON.parse(JSON.stringify(TrussStudio.example));
                const forceCases = [];
                for (const field of ['fx', 'fy']) {
                    for (const value of [Number.MIN_VALUE, -Number.MIN_VALUE]) {
                        const model = copy();
                        model.nodes[2][field] = value;
                        let message = null;
                        try { ProMathTrussFEM.fromLegacy(model); } catch (error) { message = error.message; }
                        forceCases.push({field, value, message});
                    }
                }
                const tinyModulus = copy();
                tinyModulus.members[0].E = Number.MIN_VALUE;
                let modulusMessage = null;
                try { ProMathTrussFEM.fromLegacy(tinyModulus); } catch (error) { modulusMessage = error.message; }
                const zero = copy();
                zero.nodes[2].fx = 0;
                zero.nodes[2].fy = 0;
                const normalizedZero = ProMathTrussFEM.fromLegacy(zero);
                const normalized = ProMathTrussFEM.fromLegacy(copy());
                return {
                    forceCases,
                    modulusMessage,
                    zeroFx: normalizedZero.nodes[2].fx,
                    zeroFy: normalizedZero.nodes[2].fy,
                    normalFy: normalized.nodes[2].fy,
                    normalE: normalized.members[0].E
                };
            }""")
            assert len(legacy_unit_conversion["forceCases"]) == 4, legacy_unit_conversion
            for case in legacy_unit_conversion["forceCases"]:
                label = "Fx" if case["field"] == "fx" else "Fy"
                assert case["message"] == f"Legacy {label} (N) underflows the supported SI range.", case
            assert legacy_unit_conversion["modulusMessage"] == "Legacy E (Pa) underflows the supported SI range.", legacy_unit_conversion
            assert legacy_unit_conversion["zeroFx"] == 0 and legacy_unit_conversion["zeroFy"] == 0, legacy_unit_conversion
            assert legacy_unit_conversion["normalFy"] == -10 and legacy_unit_conversion["normalE"] == 200, legacy_unit_conversion

            # Layout is contained even on 390px viewport; inner tables scroll independently.
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2'), page.evaluate('''() => ({width: innerWidth, scroll:document.documentElement.scrollWidth, wide:[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>innerWidth+2).slice(0,12).map(e=>[e.tagName,e.id,e.className?.baseVal||e.className,Math.round(e.getBoundingClientRect().right)])})''')
            # The scenario above intentionally switches the example selector to "bar".
            # Reset restores the selected example, so compute its reference now rather than
            # reusing the initial triangle reference captured before those later interactions.
            energy_references = page.evaluate("""() => {
                const model=ProMathTrussFEM.examples[document.querySelector('#example').value];
                const result=ProMathTrussFEM.solve(model);
                const roundTrip=value=>Object.is(value,-0)?'-0':String(value);
                return {residual:roundTrip(result.energyResidual),error:roundTrip(result.energyError)};
            }""")
            # Editing the model clears the previous energy diagnostic; reset recomputes it.
            page.locator('#reset').click()
            page.locator('#nodes tr').nth(1).locator('input[data-field="x"]').fill('0.01')
            assert page.locator('#energy-residual-summary').inner_text() == 'Energy balance residual: —'
            assert page.locator('#energy-residual-summary').get_attribute('data-analysis-state') == 'stale'
            assert page.locator('#energy-residual-summary').get_attribute('data-energy-residual-j') == ''
            assert page.locator('#energy-residual-summary').get_attribute('data-energy-error') == ''
            page.locator('#reset').click()
            assert 'Energy balance residual =' in page.locator('#energy-residual-summary').inner_text()
            assert page.locator('#energy-residual-summary').get_attribute('data-analysis-state') == 'valid'
            assert page.locator('#energy-residual-summary').get_attribute('data-energy-residual-j') == energy_references['residual']
            assert page.locator('#energy-residual-summary').get_attribute('data-energy-error') == energy_references['error']
            assert not errors, errors
            page.close()
        browser.close()
    print('Truss FEM reference, validation, graphics, export, keyboard and mobile checks passed')


if __name__ == '__main__':
    main()

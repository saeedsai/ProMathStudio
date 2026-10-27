"""Extended exact-quotient regression: long valid outputs must not be rejected as user inputs."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    a = '1' + '0' * 299    # 300-digit operand: 10^299
    b = '0.' + '0' * 298 + '1'  # 300-digit operand: 10^-299
    expected = '1' + '0' * 598
    assert len(expected) == 599
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv('CHROMIUM_PATH') or '/usr/bin/chromium',
            args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 850})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.set_content(html, wait_until='load')
        for x, wanted in ((a, expected), ('-' + a, '-' + expected)):
            result = page.evaluate(
                'v => MathStudio.precisionTools.calculate({a:v.a,b:v.b,operation:"divide",precision:40})',
                {'a': x, 'b': b})
            assert result['result'] == wanted
            assert result['exact'] is True, result
        compound = page.evaluate(
            'expr => MathStudio.precisionTools.evaluateExpression(expr,40)', a + '/' + b)
        assert compound['result'] == expected and compound['exact'] is True, compound
        assert page.evaluate(
            '() => MathStudio.precisionTools.calculate({a:"1",b:"3",operation:"divide"}).exact') is False
        # The larger result allowance must NOT weaken the strict external input limit.
        assert page.evaluate(
            'v => {try {MathStudio.precisionTools.calculate({a:v,b:"1",operation:"divide"});return false;} catch(e) {return !!e.message;}}',
            '1' + '0' * 300)
        page.locator('[data-workspace="calculator"]').click()
        assert page.locator('[data-workspace="calculator"].active').count() == 1
        page.locator('#precision-details > summary').click()
        assert page.locator('#precision-details').evaluate('(e) => e.open')
        page.locator('#precision-a').fill(a)
        page.locator('#precision-b').fill(b)
        page.locator('#precision-op').select_option('divide')
        page.locator('#precision-run').click()
        display = page.locator('#precision-output').inner_text()
        assert expected in display and 'Exact decimal result' in display
        assert not page.locator('#precision-output').evaluate(
            '(e) => e.classList.contains("error")')
        assert not errors, errors
        browser.close()
    print('PASS 599-digit exact quotient, signed case, expression path, strict 300-digit operands and UI')


if __name__ == '__main__':
    main()

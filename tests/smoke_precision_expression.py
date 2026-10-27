"""High-precision expression parsing, rounding, bounds, and Calculator UI regression."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def main():
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv('CHROMIUM_PATH') or '/usr/bin/chromium', args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 850})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content(html, wait_until='load')
        cases = [
            ('0.1 + 0.2 * 3', '0.7', 40),
            ('(0.1 + 0.2) * 3', '0.9', 40),
            ('-(2 + 3) * .5', '-2.5', 40),
            ('2--3', '5', 40),
            ('1/8 + 1/8', '0.25', 40),
            ('1/3', '0.' + '3' * 40, 40),
            ('1.2345678901234565/1', '1.234567890123456', 16),
            ('1.2345678901234575/1', '1.234567890123458', 16),
            ('-1.2345678901234575/1', '-1.234567890123458', 16),
            ('(2+3)/(5*2)', '0.5', 40),
        ]
        for expr, expected, precision in cases:
            actual = page.evaluate('a => MathStudio.precisionTools.evaluateExpression(a.expr,a.precision).result', {'expr': expr, 'precision': precision})
            assert actual == expected, (expr, actual, expected)
        for expr in ['', '1e3', '1/0', '2(3)', '(1+2', '1+)', '1**2', 'foo', '9'*301,
                     '1+'*80+'1', '('*17+'1'+')'*17]:
            assert page.evaluate('x => {try{MathStudio.precisionTools.evaluateExpression(x);return false;}catch(e){return !!e.message;}}', expr), expr
        assert page.evaluate('() => MathStudio.precisionTools.calculate({a:"1",b:"8",operation:"divide"}).exact') is True
        assert page.evaluate('() => MathStudio.precisionTools.calculate({a:"1",b:"3",operation:"divide"}).exact') is False
        assert page.evaluate('() => MathStudio.precisionTools.evaluateExpression("1/8+1/8").exact') is True
        assert page.evaluate('() => MathStudio.precisionTools.evaluateExpression("1/8+1/3").exact') is False
        assert page.evaluate('() => MathStudio.precisionTools.evaluateExpression("1/3").exact') is False
        assert page.evaluate('() => MathStudio.precisionTools.evaluateExpression("1/8+1/8").operations') == 3
        page.locator('[data-workspace="calculator"]').click()
        page.get_by_role('button', name='High precision').click()
        page.locator('#precision-expression').fill('(0.1+0.2)*3')
        page.locator('#precision-expression-run').click()
        assert '0.9' in page.locator('#precision-expression-output').inner_text()
        page.locator('#precision-expression').fill('2*(3+4)')
        page.locator('#precision-expression').press('Control+Enter')
        assert '14' in page.locator('#precision-expression-output').inner_text()
        page.locator('#precision-expression').fill('1/0')
        assert 'changed' in page.locator('#precision-expression-output').inner_text().lower()
        page.locator('#precision-expression-run').click()
        assert 'Division by zero' in page.locator('#precision-expression-output').inner_text()
        assert page.locator('#precision-expression-output').evaluate('(e) => e.classList.contains("error")')
        page.set_viewport_size({'width': 390, 'height': 844})
        assert page.locator('#precision-expression-run').is_visible()
        assert not errors, errors
        browser.close()
    print('PASS high precision expression parsing, precedence, half-even rounding, invalid input, and UI')

if __name__ == '__main__':
    main()

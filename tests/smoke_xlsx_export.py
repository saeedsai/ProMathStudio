"""XLSX export ZIP/XML, formula shift, safety limits and browser download regression."""
from pathlib import Path
import io
import os
import zipfile
from xml.etree import ElementTree as ET
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
NS={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def main():
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    source=(ROOT/'src/xlsx-tools.js').read_text(encoding='utf-8')
    assert source.rstrip('\n') in html
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,
            executable_path=os.getenv('CHROMIUM_PATH') or '/usr/bin/chromium',
            args=['--no-sandbox'])
        page=browser.new_page(accept_downloads=True,viewport={'width':1280,'height':850})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(html,wait_until='load')
        result=page.evaluate("""() => {
          const M=MathStudio;
          const a=M.dataTables.create('Sales 2026',['a','b','total'],
            [['1','2','=A1+B1'],['2','','=SUM(A1:A2)']]);
          const b=M.dataTables.create('Budget',['total','note'],
            [["='Sales 2026'!C1",'north & <south>'],['001','']]);
          return Array.from(M.xlsxTools.build({tables:[a,b]}));
        }""")
        data=bytes(result)
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            assert z.testzip() is None
            names=set(z.namelist())
            assert {'[Content_Types].xml','_rels/.rels','xl/workbook.xml',
                    'xl/_rels/workbook.xml.rels','xl/worksheets/sheet1.xml',
                    'xl/worksheets/sheet2.xml'}==names,names
            book=ET.fromstring(z.read('xl/workbook.xml'))
            assert [e.attrib['name'] for e in book.findall('.//x:sheet',NS)]==['Sales 2026','Budget']
            sheet1=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
            sheet2=ET.fromstring(z.read('xl/worksheets/sheet2.xml'))
            formulas=[e.text for e in sheet1.findall('.//x:f',NS)]
            assert formulas==['A2+B2','SUM(A2:A3)'],formulas
            assert [e.text for e in sheet2.findall('.//x:f',NS)]==["'Sales 2026'!C2"]
            assert sheet2.find(".//x:c[@r='B2']/x:is/x:t",NS).text=='north & <south>'
            assert sheet2.find(".//x:c[@r='A3']",NS).attrib['t']=='inlineStr'
            assert sheet1.find(".//x:c[@r='A2']/x:v",NS).text=='1'
            assert sheet1.find(".//x:c[@r='B3']",NS) is None
        assert page.evaluate("""() => MathStudio.xlsxTools.formulaToExcel(
          'IF(A1>0,"A1",SUM($B$2:B3))')""")=='IF(A2>0,"A1",SUM($B$3:B4))'
        invalid=[
            [{'name':'A','columns':['x'],'rows':[]},{'name':'a','columns':['y'],'rows':[]}],
            [{'name':'Bad/Name','columns':['x'],'rows':[]}],
            [{'name':'TooLongName_1234567890123456789012345','columns':['x'],'rows':[]}],
            [{'name':'A','columns':['x'],'rows':[['\u0001']]}],
            [{'name':'A','columns':['x'],'rows':[['='+('x'*8001)]]}],
            [{'name':'A','columns':['x'],'rows':[[]]*1001}],
        ]
        for tables in invalid:
            assert page.evaluate("""tables => {
              try{MathStudio.xlsxTools.build({tables});return false}
              catch(e){return !!e.message}
            }""",tables),tables[0]['name']
        before=page.evaluate('MathStudio.dataTables.tables.length')
        page.locator('[data-workspace="data"]').click()
        page.locator('#xlsx-export-details').evaluate('(e)=>e.open=true')
        page.locator('#xlsx-first').select_option(label='Sales 2026')
        page.locator('#xlsx-second').select_option(label='Budget')
        with page.expect_download() as download:
            page.locator('#xlsx-export').click()
        assert download.value.suggested_filename=='ProMathStudio.xlsx'
        with zipfile.ZipFile(download.value.path()) as z:
            assert z.testzip() is None
        assert page.evaluate('MathStudio.dataTables.tables.length')==before
        page.locator('#xlsx-second').select_option(label='Sales 2026')
        page.locator('#xlsx-export').click()
        assert 'two different sheets' in page.locator('#xlsx-status').inner_text()
        page.set_viewport_size({'width':390,'height':844})
        assert page.locator('#xlsx-export').is_visible()
        assert not errors,errors
        browser.close()
    print('PASS: XLSX ZIP/XML formulas, data types, invalid inputs, browser download')

if __name__=='__main__':
    main()

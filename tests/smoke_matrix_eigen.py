"""Symmetric 2x2/3x3 Jacobi eigenanalysis: references, residuals, UI and editor."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

def check(A,r,expected):
 n=len(A)
 assert len(r['values'])==n and len(r['vectors'])==n
 assert all(len(row)==n for row in r['vectors'])
 assert r['residual']<1e-8 and r['reconstructionResidual']<1e-8
 assert r['orthogonality']<1e-8 and r['iterations']<=64
 for a,b in zip(r['values'],expected):
  assert math.isclose(a,b,rel_tol=1e-8,abs_tol=1e-10),(A,a,b)
 for i in range(n):
  for j in range(n):
   av=sum(A[i][k]*r['vectors'][k][j] for k in range(n))
   assert math.isclose(av,r['values'][j]*r['vectors'][i][j],rel_tol=1e-8,abs_tol=1e-8*max(1,max(abs(x) for row in A for x in row)))
   dot=sum(r['vectors'][k][i]*r['vectors'][k][j] for k in range(n))
   assert math.isclose(dot,float(i==j),abs_tol=1e-8)

def main():
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or None,args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1280,'height':850})
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='load')
  page.locator('[data-workspace="calculator"]').click()
  page.locator('#matrix-tools').evaluate('(e)=>e.open=true')
  cases=[
   ([[2,1],[1,2]],[3,1]),
   ([[-2,0],[0,3]],[3,-2]),
   ([[0,0],[0,0]],[0,0]),
   ([[5,0,0],[0,5,0],[0,0,5]],[5,5,5]),
   ([[1,1,1],[1,1,1],[1,1,1]],[3,0,0]),
   ([[4,1,1],[1,3,0],[1,0,2]],[4.879385241571816,2.652703644666139,1.4679111137620442]),
   ([[1e12,0],[0,1e-9]],[1e12,1e-9]),
  ]
  for A,expected in cases:
   original=[row[:] for row in A]
   result=page.evaluate('(A)=>MathStudio.matrixTools.eigenSymmetric(A)',A)
   check(A,result,expected)
   assert A==original
  for A,phrase in [
   ([[1,2],[3,4]],'symmetric'),
   ([[1,2,3],[4,5,6]],'square'),
   ([[1,1],[1,float('nan')]],'finite'),
   ([[1,2],[2,1e13]],'finite'),
  ]:
   if any(not math.isfinite(x) for row in A for x in row):
    message=page.evaluate('()=>{try{MathStudio.matrixTools.eigenSymmetric([[1,1],[1,NaN]]);return ""}catch(e){return e.message}}')
   else:
    message=page.evaluate('(A)=>{try{MathStudio.matrixTools.eigenSymmetric(A);return ""}catch(e){return e.message}}',A)
   assert phrase in message,(A,message)
  page.locator('#mat-rows').select_option('3')
  page.locator('#mat-cols').select_option('3')
  for i,value in enumerate(['1','0','0','0','2','0','0','0','3']):
   page.locator('#mat-grid input').nth(i).fill(value)
  page.locator('#mat-eigen').click()
  out=page.locator('#mat-result').inner_text()
  assert 'Eigenvalues (descending): 3, 2, 1' in out,out
  assert 'Relative residual:' in out and 'Orthogonality residual:' in out
  page.locator('#mat-eigen-factor').select_option('values')
  page.locator('#mat-send').click()
  assert 'matrix([3],[2],[1])' in page.locator('#equation-input').input_value()
  page.locator('[data-workspace="calculator"]').click()
  page.locator('#matrix-tools').evaluate('(e)=>e.open=true')
  page.locator('#mat-grid input').nth(1).fill('5')
  assert page.locator('#mat-send').is_disabled()
  page.locator('#mat-eigen').click()
  assert 'symmetric' in page.locator('#mat-result').inner_text()
  page.set_viewport_size({'width':390,'height':844})
  assert page.locator('#mat-eigen').is_visible()
  assert not errors,errors
  browser.close()
 print('PASS symmetric Jacobi eigenvalues/vectors, repeated spectrum, residual, invalid inputs, editor, mobile')

if __name__=='__main__':main()

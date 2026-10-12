/* Deploy this as an Apps Script web app. Set Script Properties:
   SPREADSHEET_ID = your Google Sheet ID
   SHARED_SECRET = long random secret (32+ chars)
   It stores only Timestamp, Participant name, Total correct. */
function doPost(e) {
  const p = PropertiesService.getScriptProperties();
  const secret = p.getProperty('SHARED_SECRET'), id = p.getProperty('SPREADSHEET_ID');
  let b;
  try { b = JSON.parse((e && e.postData && e.postData.contents) || '{}'); }
  catch (_) { return out({ok:false}); }
  if (!secret || !id || !b.secret || !equal(String(b.secret), String(secret))) return out({ok:false});
  const name = String(b.name || '').trim().replace(/\s+/g,' ').slice(0,100);
  const score = Number(b.score);
  if (!name || !Number.isInteger(score) || score < 0 || score > 22) return out({ok:false});
  const lock = LockService.getScriptLock(); lock.waitLock(10000);
  try {
    const s = SpreadsheetApp.openById(id).getSheetByName('Scores');
    if (!s) return out({ok:false});
    if (s.getLastRow() === 0) s.appendRow(['Timestamp','Participant name','Total correct']);
    s.appendRow([new Date(), /^[=+\-@]/.test(name) ? "'"+name : name, score]);
  } finally { lock.releaseLock(); }
  return out({ok:true});
}
function equal(a,b){if(a.length!==b.length)return false;let d=0;for(let i=0;i<a.length;i++)d|=a.charCodeAt(i)^b.charCodeAt(i);return d===0;}
function out(x){return ContentService.createTextOutput(JSON.stringify(x)).setMimeType(ContentService.MimeType.JSON);}

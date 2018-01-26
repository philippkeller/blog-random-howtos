---
title: How to attach a file to google spreadsheet
tags:
  - google-spreadsheet
  - google-apps-scripts
  - attachments
date: 2014-01-20 16:06:00
alias: /post/73949358752/how-to-attach-a-file-to-google-spreadsheet
css:
  - "pre>code.hljs {font-size: 80%}"
---

![attach file](/images/attach.png)

The following setup lets you

*   choose a file from your computer to upload
*   upload it to a defined folder on google drive
*   inserts the link to the current cell

<!-- more -->

To get it working:

1.  find out the id of the google drive folder you want your attachments be saved (in the example below this is `0B0uw1JCogWHuc29FWFJMWmc3Z1k`)
2.  in the spreadsheet where you want to upload the file: do Tools→Script Editor.. and paste the script below. Be sure to replace the id with your folders id

**Update 2014**: Made it working with [the new sheets](http://googleblog.blogspot.ch/2013/12/new-google-sheets-faster-more-powerful.html)
**Update 2016-05** Fixed the script thanks to the comments by Fede and Dov (DocsList.getFolderId was not working any more)

```javascript
// upload document into google spreadsheet
// and put link to it into current cell

function onOpen(e) {
  var ss = SpreadsheetApp.getActiveSpreadsheet()
  var menuEntries = [];
  menuEntries.push({name: "File...", functionName: "doGet"});
  ss.addMenu("Attach ...", menuEntries);
}

function doGet(e) {
  var app = UiApp.createApplication().setTitle("upload attachment into Google Drive");
  SpreadsheetApp.getActiveSpreadsheet().show(app);
  var form = app.createFormPanel().setId('frm').setEncoding('multipart/form-data');
  var formContent = app.createVerticalPanel();
  form.add(formContent);  
  formContent.add(app.createFileUpload().setName('thefile'));

  // these parameters need to be passed by form
  // in doPost() these cannot be found out anymore
  formContent.add(app.createHidden("activeCell", SpreadsheetApp.getActiveRange().getA1Notation()));
  formContent.add(app.createHidden("activeSheet", SpreadsheetApp.getActiveSheet().getName()));
  formContent.add(app.createHidden("activeSpreadsheet", SpreadsheetApp.getActiveSpreadsheet().getId()));
  formContent.add(app.createSubmitButton('Submit'));
  app.add(form);
  SpreadsheetApp.getActiveSpreadsheet().show(app);
  return app;
}

function doPost(e) {
  var app = UiApp.getActiveApplication();
  app.createLabel('saving...');
  var fileBlob = e.parameter.thefile;
  var doc = DriveApp.getFolderById('0B0uw1JCogWHuc29FWFJMWmc3Z1k').createFile(fileBlob);
  var label = app.createLabel('file uploaded successfully');

  // write value into current cell
  var value = 'hyperlink("' + doc.getUrl() + '";"' + doc.getName() + '")'
  var activeSpreadsheet = e.parameter.activeSpreadsheet;
  var activeSheet = e.parameter.activeSheet;
  var activeCell = e.parameter.activeCell;
  var label = app.createLabel('file uploaded successfully');
  app.add(label);
  SpreadsheetApp.openById(activeSpreadsheet).getSheetByName(activeSheet).getRange(activeCell).setFormula(value);
  app.close();
  return app;
}

```
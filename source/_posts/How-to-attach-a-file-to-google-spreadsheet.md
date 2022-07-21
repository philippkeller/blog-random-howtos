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

![](/images/sheet-upload.gif)

**Update 2022**: There is a new solution which **actually works**! DropSpread is a google sheet extension which let's you…

1. choose a file from your computer to upload
2. upload it to a defined folder on google drive
3. inserts the link to the current cell

In order to use it:

1. Click Extensions -> Add-Ons -> Get add-ons
2. Search for DropSpread and install it
3. Reload the spreadsheet
4. Click Extensions -> DropSpread -> Open DropSpread.io -> opens a sidebar
5. in the sidebar next to settings, click "show"
6. in Folder ID paste in the id of your google drive folder you want the files to go to. Look at the URL of your google drive folder, you'll see something like <pre>drive.google.com/drive/u/0/folders/<strong style="color: red">0A0ab1ABabABabmAabSTUqrFkTkk</strong>?resourcekey=0-vWjySqCUUgZUcgvA2Kno8A</pre> The red part is what you need to past into there

That's it, now you can move your mouse into any cell, do Extensions -> DropSpread -> Open DropSpread.io, drag'n'drop your file into the sidebar and the file is uploaded into drive and the link is pasted into the current cell.

If you're happy about the solution, then please give [the author a good review](https://workspace.google.com/marketplace/app/dropspread/1038626361348).

-----------

&nbsp;

-----------

&nbsp;

-----------

The old solution, for history reasons. I couldn't get it to work again, if anyone is interested, I think [this stackoverflow answer](https://stackoverflow.com/questions/57090349/uploading-file-to-spreadsheet-shows-uiapp-has-been-deprecated-please-use-htmls) is pointing into the right direction.

![attach file](/images/attach.png)

The following setup lets you


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

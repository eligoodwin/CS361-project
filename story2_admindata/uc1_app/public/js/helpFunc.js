
var serverAddress = 'flip1.engr.oregonstate.edu:12432';

function validateForm(event){
    
    var tableIn = document.getElementById('gymList');
    var dataIn = [];
    var checkSum = true;
    var unitType;
    
    dataIn.push(document.getElementById("nameIn").value);
    dataIn.push(document.getElementById("repIn").value);
    dataIn.push(document.getElementById("weightIn").value);
    dataIn.push(document.getElementById("dateIn").value);
    var lbsIn = document.getElementById("lbsIn");
    var kgIn = document.getElementById("kgIn");
    
    if (lbsIn.checked) {
        unitType = '1';
    }
    else if(kgIn.checked){
        unitType = '0';
    }
    else
        unitType = '';
    
    dataIn.push(unitType);
    
    for(var i = 0; i < dataIn.length; i++){
        if(dataIn[i] == ""){
            checkSum = false;
        }
    }
    
    if(checkSum){
        addItem(tableIn, dataIn);
        return true;
    }
    
    else{
        alert("Fill out all available boxes");
        return false;
    }
    
    event.preventDefault
}

function addItem(tableIn, dataIn){
    
        var req = new XMLHttpRequest();
        var payload = {'addItem':'Add Item',
                        'name':dataIn[0],
                        'reps':dataIn[1],
                        'weight':dataIn[2],
                        'date':dataIn[3],
                        'unit':dataIn[4]};
  
        req.open('POST', serverAddress, true);
        req.setRequestHeader('Content-Type', 'application/json');
        req.addEventListener('load',function(){
            if(req.status >= 200 && req.status < 400){
                var response = req.responseText;
                var dataOut = JSON.parse(response);
                editTable(dataOut);
                //editTable(response, tableIn);
          } else {
            console.log("Error in network request: " + req.statusText);
          }});  
        req.send(JSON.stringify(payload));
    
}


function editTable(dataIn){
    var wrkTable = document.getElementById('gymList');
    var existIDsForm = document.getElementsByName('IdDel');
    var existIDs = createExistIdArray(existIDsForm);
    var newId = createIdArray(dataIn);
    
    var i, j;
    // See if we need to add any new rows
    for(i = 0; i < newId.length; i++){
        if(!existIDs.includes(newId[i])){
            addRow(dataIn[i], wrkTable);
            break;
        }
    }
    
    // see if we need to delete any rows
    for(i = 0; i < existIDs.length; i++){
        if(!newId.includes(existIDs[i])){
            deleteRow(existIDsForm[i], wrkTable);
            break;
        }
    }
}

function addRow(objectIn, tableIn){
    if(objectIn.lbs == '1'){
        unitType = "lbs"
    }
    else{
        unitType = "kg"
    }
    
    var headerId = [objectIn.name, objectIn.reps, objectIn.weight, unitType, objectIn.date];
    
    var newRow = document.createElement("tr");
    for(var i = 0; i < headerId.length; i++){
        var newData = document.createElement("td");
        newData.textContent = headerId[i];
        newRow.appendChild(newData); 
    }
    
    // Create the forms to edit and delete the element.
    addButton(newRow, objectIn.id);
    
    tableIn.appendChild(newRow);
}

function addButton(rowIn, idIn){
    
    // Start with the Edit Button
    
    var newButtOne = document.createElement("td");
    var editButton = document.createElement("form");
    editButton.setAttribute("method", "post");
    editButton.setAttribute("action", serverAddress);
    
    var hiddenFieldEdit = document.createElement("input")
    hiddenFieldEdit.setAttribute("type", "hidden");
    hiddenFieldEdit.setAttribute("name", "IdEdit");
    hiddenFieldEdit.setAttribute("value", idIn.toString());
    
    var submitEdit = document.createElement("input")
    submitEdit.setAttribute("type", "submit");
    submitEdit.setAttribute("name", "editItemPage");
    submitEdit.setAttribute("value", "Edit");
    
    editButton.appendChild(hiddenFieldEdit);
    editButton.appendChild(submitEdit);
    
    newButtOne.appendChild(editButton);
    
    //Move on to the Delete Button
    
    var newButtTwo = document.createElement("td");
    var hiddenFieldDel = document.createElement("input")
    hiddenFieldDel.setAttribute("type", "hidden");
    hiddenFieldDel.setAttribute("name", "IdDel");
    hiddenFieldDel.setAttribute("value", idIn.toString());
    
    var submitDelete = document.createElement("input");
    submitDelete.setAttribute("type", "button");
    submitDelete.setAttribute("name", "Delete"); 
    submitDelete.setAttribute("value", "Delete");
    submitDelete.setAttribute("onclick", "deleteExcercise(this)")
    
    var deleteButton = document.createElement("form");
    deleteButton.appendChild(hiddenFieldDel);
    deleteButton.appendChild(submitDelete);
    
    newButtTwo.appendChild(deleteButton);
    
    // now append the data blocks to the row
    
    rowIn.appendChild(newButtOne);
    rowIn.appendChild(newButtTwo);
}

function createIdArray(dataIn){
    var i;
    var idOut = [];
    for(i = 0; i < dataIn.length; i++){
        idOut.push((dataIn[i].id).toString());
    }
    
    return idOut;
}

function createExistIdArray(IdArray){
    var i;
    var idOut = [];
    for(i = 0; i < IdArray.length; i++){
        idOut.push(IdArray[i].value);
    }
    
    return idOut;
}

// The following function was adapted from that provided in the lectures/HW Description
function deleteRow(rowIn, tableIn) {
        var numbRow = tableIn.rows.length;
        for (var i = 0; i < numbRow; i++) {
            var rowCheck = tableIn.rows[i];
            
            if (rowCheck == rowIn.parentNode.parentNode.parentNode) {
                tableIn.deleteRow(i);
                return;
            }
        }
}

function deleteExcercise(formIn){
        var req = new XMLHttpRequest();
        var hiddenIdForm = formIn.previousElementSibling;
        var idIn = hiddenIdForm.value;
        var payload = {'delItem':'Delete Item',
                        'id':idIn};

        req.open('POST', serverAddress, true);
        req.setRequestHeader('Content-Type', 'application/json');
        req.addEventListener('load',function(){
            if(req.status >= 200 && req.status < 400){
                var response = req.responseText;
                var dataOut = JSON.parse(response);
                editTable(dataOut);
                
          } else {
            console.log("Error in network request: " + req.statusText);
          }});  
        req.send(JSON.stringify(payload));
    
}

function validateFormEdit(event){

    var dataIn = [];
    var checkSum = true;
    var unitType;
    
    dataIn.push(document.getElementById("IdEdit").value)
    dataIn.push(document.getElementById("nameIn").value);
    dataIn.push(document.getElementById("repIn").value);
    dataIn.push(document.getElementById("weightIn").value);
    dataIn.push(document.getElementById("dateIn").value);
    var lbsIn = document.getElementById("lbsIn");
    var kgIn = document.getElementById("kgIn");
    
    if (lbsIn.checked) {
        unitType = '1';
    }
    else if(kgIn.checked){
        unitType = '0';
    }
    else
        unitType = '';
    
    dataIn.push(unitType);
    
    for(var i = 0; i < dataIn.length; i++){
        if(dataIn[i] == ""){
            checkSum = false;
        }
    }
    
    if(checkSum){
        editItem(dataIn);
        return true;
    }
    
    else{
        alert("Fill out all available boxes");
        return false;
    }
    
    event.preventDefault
}

function editItem(dataIn){
        var req = new XMLHttpRequest();
        var payload = {'editItem':'change Item',
                        'IdEdit':dataIn[0],
                        'name':dataIn[1],
                        'reps':dataIn[2],
                        'weight':dataIn[3],
                        'date':dataIn[4],
                        'unit':dataIn[5]};
  
        req.open('POST', serverAddress, true);
        req.setRequestHeader('Content-Type', 'application/json');
        req.addEventListener('load',function(){
            if(req.status >= 200 && req.status < 400){
                
          } else {
            console.log("Error in network request: " + req.statusText);
          }});  
        req.send(JSON.stringify(payload));
}

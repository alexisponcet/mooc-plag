var lastSortIndex = 0;

var ascendingSort = false;

/**
 * Get the index of the clicked column
 *
 * @param columnName : name of the current column
 */
function getColumnIndex(columnName){	
	var index = 0;
	var columns = document.getElementsByClassName("displaySimiliarity_submissionsTable")[0].getElementsByTagName("thead")[0].getElementsByTagName("th");
	for(var i = 0; i < columns.length; i++){
		if (columns[i].innerHTML == columnName)
			break;
		index = index + 1;
	}	
	return index;
}

/**
 * Sort the similarities table
 */
function sortTable(){
	if (document.getElementsByClassName("displaySimiliarity_submissionsTable").length > 0){
		var index = 0;
		 
		// Get the index of the column
		if (this.innerHTML != null)
			index = getColumnIndex(this.innerHTML);
		else
			index = lastSortIndex;

		if (index != lastSortIndex) ascendingSort = false;
		
		var tbody = document.getElementsByClassName("displaySimiliarity_submissionsTable")[0].getElementsByTagName("tbody")[0];

		// Manual Sort
		for(var j = 0 ; j < tbody.children.length-1;j++){
			var itemJ = tbody.rows[j].cells[index].innerHTML;
			
			if (itemJ == "")	itemJ = 0;
			if (!isNaN(itemJ)) itemJ = parseFloat(itemJ);			
			k = j;

			for(var i = k + 1 ; i < tbody.children.length; i++){


				var itemI = tbody.rows[i].cells[index].innerHTML;

				if (itemI == "")	itemI = 0;
				if (!isNaN(itemI)) itemI = parseFloat(itemI);
				
				if (((ascendingSort && itemI < itemJ) || (!ascendingSort && itemI > itemJ))){
					itemJ = itemI;
					j = i;
				}
			}
			tbody.insertBefore(tbody.children[j], tbody.children[k]);
			j = k;
		}

		// Prepare the next sort
		ascendingSort = !ascendingSort;
		lastSortIndex = index;
	}
}

/**
 * Add the sort event
 */
function addEventSortTable(){
	if (document.getElementsByClassName("displaySimiliarity_submissionsTable").length > 0){
		var columns = document.getElementsByClassName("displaySimiliarity_submissionsTable")[0].getElementsByTagName("thead")[0].getElementsByTagName("th");
		for(var i = 0; i < columns.length; i++){
			columns[i].addEventListener("click", sortTable, false);
		}
	}
}

/**
 * Return to the reception
 */
function returnIndex(){
	window.location = '/jplag/';
}

/**
 * Add the return event
 */
function addEventReturn(){
	$("#similarity_returnIndex").on("click", returnIndex);
}

/**
 * Get name of student by its id
 */
function getNameById(){
	$.getJSON("getStudentNameById/" + $("#id_student").val(), function(data) {
	  	$.each(data, function(key, value){
		    if (value != "notExist") {
		       $("#selectSubmission_student").val(value);
		    } else {
		       $("#selectSubmission_student").val("");
		    }
		});
   }, "json");
}

/**
 * Get name of student by its id
 *
 * @param event : current event
 */
function searchNameById(event){
	getNameById();  
	return true; 
}

/**
 * Set the focus to the name field 
 *
 * @param event : current event
 */
function searchNameByIdEnter(event){
    if(event.keyCode == 13){
	      $("#selectSubmission_student").focus();
	      return false;  
    }
}

/**
 * Initialize the page
 */
function load(){
  addEventSortTable();
  addEventReturn();

  lastSortIndex = 2;
  sortTable();

  lastSortIndex = 0;

  $("#id_student").on("keyup", searchNameById);
  $("#id_student").on("input", searchNameById);
  $("#id_student").on("keypress", searchNameByIdEnter);

  $("#id_student").focus();
}

$(window).bind("load", load);

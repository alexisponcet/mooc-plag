// Regex to validate the name of the assignment.
var fieldRegex = '^.{1,255}$';

/*
 * Update current location with the aim of showing assignment details
 */
function goToAssignmentDetail(){
  var assignment = $('select[name="assignment"]').val();

  //$('#formAssignment').attr('action', "/jplag/assignment/" + assignment).submit();
  window.location = "/jplag/assignment/" + assignment;
  return false;
}

/*
 * Initialize pop-up
 */
function popUpCreateAssignment(){
  $("#createAssignment_overlay").fadeIn("slow");
  $("#createAssignment_container").fadeIn("slow");
  $("#createAssignment_cell").fadeIn("slow");
  $("#createAssignment_part").fadeIn("slow");
  $("#createAssignment_popupBox").fadeIn("slow");
  $("#createAssignment_popupContent").fadeIn("slow");  
  $("#createAssignment_validate").fadeIn("slow"); 
  $("#createAssignment_cancelValidation").fadeIn("slow"); 

  $("#createAssignment_validate").on("click", verifyFrmCreateAssignment);
  $("#createAssignment_nameAssignment").on("keyup", verifyAssignment);

  $("#createAssignment_nameAssignment").on("focusout", verifyAssignment);

  $("#createAssignment_overlay").on("click", returnIndex);
  $("#createAssignment_cancelValidation").on("click", returnIndex);

  return false;
}

/*
 * Return to the reception
 */
function returnIndex(){
  $("#createAssignment_overlay").fadeOut("slow");
  $("#createAssignment_container").fadeOut("slow");
  $("#createAssignment_cell").fadeOut("slow");
  $("#createAssignment_part").fadeOut("slow");
  $("#createAssignment_popupBox").fadeOut("slow");
  $("#createAssignment_popupContent").fadeOut("slow");   
  $("#createAssignment_validate").fadeOut("slow"); 
  $("#createAssignment_cancelValidation").fadeOut("slow"); 
  $("#createAssignment_nameAssignment").val("");
  $("#createAssignment_nameAssignment").removeClass("error"); 
  $("#createAssignment_errAssignment").text("");

  $("#createAssignment_validate").off("click", verifyFrmCreateAssignment);
  $("#createAssignment_nameAssignment").off("keyup", verifyAssignment);
  $("#createAssignment_nameAssignment").off("focusout", verifyAssignment);
  $("#createAssignment_overlay").off("click", returnIndex);
  $("#createAssignment_cancelValidation").off("click", returnIndex);
}

/**
 * Create assignment if name is Ok
 */
function verifyFrmCreateAssignment(){
  if(verifyAssignment()){
    $.post("createAssignment/", $("#createAssignment_frmCreateAssignment").serialize(), function(data, textStatus) {
       $.each(data, function(key, value){
        if (value == "creation") {
           $("#createAssignment_popupContent").fadeOut("slow"); 
           $("#createAssignment_validate").fadeOut("slow"); 
           $("#createAssignment_cancelValidation").fadeOut("slow"); 
           $("#createAssignment_confValidation").fadeIn("slow");
           $("#createAssignment_overlay").delay(2500).fadeOut("slow");
           $("#createAssignment_container").delay(2500).fadeOut("slow");
           $("#createAssignment_cell").delay(2500).fadeOut("slow");
           $("#createAssignment_part").delay(2500).fadeOut("slow");
           $("#createAssignment_popupBox").delay(2500).fadeOut("slow"); 


           $("#createAssignment_confValidation").delay(2300).fadeOut("slow");
           var assignment = $("#createAssignment_nameAssignment").val();
           $("#createAssignment_nameAssignment").val("");

           $("#createAssignment_validate").off("click", verifyFrmCreateAssignment);
           $("#createAssignment_nameAssignment").off("keyup", verifyAssignment);
           $("#createAssignment_nameAssignment").off("focusout", verifyAssignment);
           $("#createAssignment_overlay").off("click", returnIndex);
           $("#createAssignment_cancelValidation").off("click", returnIndex); 
           setTimeout(function(){
                window.location = "/jplag/"   
           }, 2500); 
        } else {
           $("#createAssignment_nameAssignment").val("");
           $("#createAssignment_nameAssignment").addClass("error");
           $("#createAssignment_errAssignment").text("Assignment already exist. Retry.");
        }
      });
    }, "json");
  }
}

/**
 * Verify assignment's name
 */
function verifyAssignment(){
  var field = $("#createAssignment_nameAssignment");
  if ((field.val()).match(fieldRegex) == null || $.trim(field.val()) == ""){
      field.addClass("error");
      if($.trim(field.val()) == "") {
          $("#createAssignment_errAssignment").text("Name of assignment is mandatory.");
      } else if (field.val().length > 255){
          $("#createAssignment_errAssignment").text("Name of assignment invalid. Assignment name is too long (255 char max).");
      }
      return 0;
    } else {
      field.removeClass("error");
        $("#createAssignment_errAssignment").text("");
      return 1;
    }
}

/**
 * If enter : Create assignment if name is Ok
 */
function validFormByEnter(){
    if(event.keyCode == 13){
      verifyFrmCreateAssignment();
      return false;    
    }
}

/**
 * Initialize the page
 */
function load(){
  $("#selectAssignment_searchAssignment").on("click", goToAssignmentDetail);
  $("#selectAssignment_createAssignment").on("click", popUpCreateAssignment);

  $("#createAssignment_nameAssignment").on("keypress", validFormByEnter);
}

$(window).bind("load", load);

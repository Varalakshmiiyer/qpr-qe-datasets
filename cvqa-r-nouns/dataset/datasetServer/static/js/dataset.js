
var user = "";
var nextUrl = "/next";
var saveUrl = "/save";

var wordSelection = [];
var words = [];

function saveQuestion(){
	// console.log(wordSelection);
	// console.log(words);

	var selectedWords = [];
	var newQuestionWords = [];
	var correction = [];
	var found = false;
	for (var i = 0; i < words.length; i++) {
		if (wordSelection[i]){
			selectedWords.push(words[i]);
			newQuestionWords.push($("#" + i + "Text").val());
			correction.push($("#" + i + "Text").val());
			found = true;
		} else {
			if (found == true){
				correction.push("|");
			}
			newQuestionWords.push(words[i]);
			found = false;
		}
	}

	data = {};
	data['question_error_correction'] = correction.join(" ");
	data['question_error_correction_answer'] = $("#newAnswer").val();
	data['question_error'] = selectedWords.join(" ");
	data['question_error_new_question'] = newQuestionWords.join(" ");
	data['question_is_premise_true'] = (selectedWords.length == 0);

	console.log(data);

	 $.ajax({
	    url: "/" + user + saveUrl,
	    dataType: "json",
	    type: "POST",
	    contentType: "application/json; charset=utf-8",
	    data: JSON.stringify(data),
	    success: function (data) {
	    	getNextQuestion();
	    }
	  });
}

function getNextQuestion(){
	 $.ajax({
        url: "/" + user + nextUrl,
        dataType: "json",
        type: "GET",
        success: function (data) {
        	question = data;
        	$("#label").text(question["Unnamed: 0"] + "/" + question["total"]);
        	$("#image").attr("src", question["image_url"]);
        	var split = question["questionDisplay"].split(" ");
        	$("#questionParts").empty();
        	$("#correction").val("");
        	$("#newAnswer").val("");
        	$("#fileLink").attr("href", question["file"]);
        	wordSelection = [];
        	words = split;
        	for (var i = 0; i < split.length; i++) {
        		var $button = $('<button/>', {
		            text: split[i],
		            id: i,
		            class: "pure-button",
		            style: "width:100%;"
		        });

		        var $text = $('<input/>', {
		            text: "",
		            id: i + "Text",
		            type: "text"
		        });

        		 $button.click(function(){
        		 	var id = $( this ).attr("id");
        		 	wordSelection[id] =! wordSelection[id];
    				$( this ).toggleClass("button-warning");
  				});

        		var $buttonRow = $('<tr>');

        		wordSelection.push(false);
        		$buttonRow.append($("<td>").append($button));
        		$buttonRow.append($("<td>").append($text));
		        $("#questionParts").append($buttonRow);
        	}
        }
     });
}

$(document).ready(function() {
	$("#saveButton").click(saveQuestion);

	$("#userSelect").change(function(){
		user = $(this).val();
		if (user != ""){
			$("#questionSection").show();
			getNextQuestion();
		} else {
			$("#questionSection").hide();
		}
	});
})
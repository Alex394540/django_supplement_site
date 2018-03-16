function resetInputs(doc=true, prod=true, date=true)
{
    if (doc) {
        $('#doctor_name').val('');
    }
    
    if (prod) {
        $('#product_name').val('');
    }
    
    if (date) {
        $('#start_date_search').val('');
        $('#end_date_search').val('');
    }
}


function dateCheck(date) {
	
	var test = /\d\d\d\d-\d\d-\d\d/i.test(date);
	if (test) {
		var ar = date.split('-');
		var year = parseInt(ar[0]);
		var month = parseInt(ar[1]);
		var day = parseInt(ar[2]);
		return year > 1970 && year < 2038 && month > 0 && month < 13 && day > 0 && day < 32; 
	}
	return false;
}

function displayResult(res, table) {
	var html = "";
	for (var i = 0; i < res.length; i++) {
		var row = "<tr>";
		res[i].forEach(function(el) {
			row += '<td>' + el + '</td>';
		});
		row += "</tr>";
		html += row;
	}
		
	$(table).find("tr:gt(0)").remove();
	$(table).append(html);
}

function searchDoctor()
{
    resetInputs(false, true, true);
    
	var d_name = $("#doctor_name").val().split(' ');
    var doctor = d_name[1] + "_" + d_name[2];
	var url = '/trial/ajax/filter_operations?search_type=doc_name&search_prop=' + doctor;
		
	$.getJSON(url, function( res ) {
        displayResult(res[1], '#sellTable');
	});
			
	return true;
}

function searchName()
{
    resetInputs(true, false, true);
    
	var product = $("#product_name").val();
	var url = '/trial/ajax/filter_operations?search_type=name&search_prop=' + product;

	$.getJSON(url, function( res ) {
		displayResult(res[0], '#buyTable');
        displayResult(res[1], '#sellTable');
	});
			
	return true;
}

function searchDate()
{
    resetInputs(true, true, false);
    
	var start = $("#start_date_search").val();
	start = (start == '') ? '1971-01-01' : start;
			
	var end = $("#end_date_search").val();
	end = (end == '') ? '2037-12-31' : end;
			
	var test1 = dateCheck(start);
	var test2 = dateCheck(end);
			
	if (!(test1 && test2)) {
        alert("Wrong date or date format!");				
		return false;
	}
			
	var date = start + '__' + end;
			
	var url = '/trial/ajax/filter_operations?search_type=date&search_prop=' + date;
		
	$.getJSON(url, function( res ) {
		displayResult(res[0], '#buyTable');
        displayResult(res[1], '#sellTable');
	});
}

$(document).ready(function() {
	
	function showProd()  
	{
		$.getJSON('/trial/ajax/show_prod/', function( prods ) {
			ans = prods.map(x => '<option>' + x + '</option>');
			ans.forEach(function(i) {
		        $('#products').append(i);
	        });
		});
	}
    
    function showDocs()
    {
		$.getJSON('/trial/ajax/show_docs/', function( docs ) {
			ans = docs.map(x => '<option>' + x + '</option>');
			ans.forEach(function(i) {
		        $('#doctors').append(i);
	        });
		});        
    }
	
	showProd();
    showDocs();

});
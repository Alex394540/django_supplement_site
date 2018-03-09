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

function searchName(sell = true)
{
	var product;
	var url;
	if (sell) 
	{
		product = $("#product_name").val();
		url = '/trial/ajax/filter_operations?op_type=sell&search_type=name&search_prop=' + product;
	} 
	else 
	{
		product = $("#product_name2").val();
		url = '/trial/ajax/filter_operations?op_type=buy&search_type=name&search_prop=' + product;
	}
		
	$.getJSON(url, function( res ) {
		var selector = (sell) ? '#sellTable' : '#buyTable';
		displayResult(res, selector);
	});
			
	return true;
}

function searchDate(sell = true)
{
	var url;
	if (sell) 
	{
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
			
		url = '/trial/ajax/filter_operations?op_type=sell&search_type=date&search_prop=' + date;
	} 
	else 
	{
		var start = $("#start_date_search2").val();
		start = (start == '') ? '1971-01-01' : start;
			
		var end = $("#end_date_search2").val();
		end = (end == '') ? '2037-12-31' : end;
			
		var test1 = dateCheck(start);
		var test2 = dateCheck(end);
			
		if (!(test1 && test2)) {
            alert("Wrong date or date format!");				
		    return false;
		}
			
		var date = start + '__' + end;
			
		url = '/trial/ajax/filter_operations?op_type=buy&search_type=date&search_prop=' + date;
	}
		
	$.getJSON(url, function( res ) {
		var selector = (sell) ? '#sellTable' : '#buyTable';
		displayResult(res, selector);
	});
}

$(document).ready(function() {
	
	function showProd()  
	{
		$.getJSON('/trial/ajax/show_prod/', function( prods ) {
			ans = prods.map(x => '<option>' + x + '</option>');
			ans.forEach(function(i) {
		        $('#products').append(i);
				$('#products2').append(i);
	        });
		});
	}
	
	showProd();

});
$(document).ready(function() {
	
    function showCat() 
	{
		$.getJSON('/ajax/show_cat/', function( cats ) {
			ans = cats.map(x => '<option>' + x + '</option>');
			ans.forEach(function(i) {
				$('#categories').append(i);
			});
		});
	}

	function showMan() 
	{
		$.getJSON('/ajax/show_man/', function( mans ) {
			ans = mans.map(x => '<option>' + x + '</option>');
			ans.forEach(function(i) {
		        $('#manufacturers').append(i);
			});
		});
	}

	function showProd()  
	{
		$.getJSON('/ajax/show_prod/', function( prods ) {
			ans = prods.map(x => '<option>' + x + '</option>');
			ans.forEach(function(i) {
		        $('#products').append(i);
	        });
		});
	}
	
	showCat();
    showMan();
    showProd();
	
});
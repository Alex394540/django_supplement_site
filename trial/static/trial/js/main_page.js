function findProduct() {
    
	var product = $('#product_name').val();
	var table = $('.table tr').find('td:first');
		
	for (var i = 0; i < table.length; i++) {
		if (table[i].textContent.trim() == product.trim()) {
			var $scrollTo = $('tr:nth-of-type(' + (i + 2) + ')');

			var previous = $scrollTo.css('background-color');
			$scrollTo.css('background-color', '#cafc6f');
			setTimeout(function() {
				$scrollTo.css('background-color', previous);
			}, 5000);
			
			$('#product_name').val('');
			
			$('html, body').animate({
				scrollTop: $('tr:nth-of-type(' + (i + 2) + ')').offset().top
			}, 500);
			
			return true;
		}
	}
	return false;
}


$(document).ready(function() {
    
    function showProd()  
	{
		$.getJSON('/ajax/show_prod/', function( prods ) {
			ans = prods.map(x => '<option>' + x + '</option>');
			ans.forEach(function(i) {
		        $('#products').append(i);
	        });
		});
	}
    
    showProd();
    
});
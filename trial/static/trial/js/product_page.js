function deleteDrug(id) {
	
	var req = new XMLHttpRequest();
	req.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			location = "/trial/";
		}
	}
	
	req.open('GET', '/trial/ajax/delete_product?id=' + id, true);
	req.send();
	return true;
}

function saveChanges(id) {

	var req = new XMLHttpRequest();
	req.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			location = "/trial/";
		}
	}
		
	var form = document.querySelector('#form').textContent;
	var total_dosage = document.querySelector('#total_dosage').textContent;
	var manufacturer = document.querySelector('#manufacturer').textContent;
	var category = document.querySelector('#category').textContent;
	var price = document.querySelector('#price').textContent;
		
	var url = '/trial/ajax/save_changes?' + 'id=' + id + '&form=' + form + '&total_dosage=' + total_dosage + '&manufacturer=' + 
			   manufacturer + "&category=" + category + "&price=" + price;
		
	req.open('GET', url, true);
	req.send();
	return true;
}
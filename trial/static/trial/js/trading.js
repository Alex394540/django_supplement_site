function get_panel(id) {
	var panel = '#panel_' + id;
	var d = document.querySelector(panel);
	return d;
}

function change_amount(id, coef) {
	
	var d = get_panel(id);
	var inp = parseInt(d.value, 10);
    
    var f_name = '';
    var l_name = '';
    
    if (coef < 0)
    {
        var doc_el = document.querySelector("#doctor_" + id);
        var doctor = doc_el.options[doc_el.selectedIndex].text;
        
        if (doctor == '*Select doctor') 
        {
            alert('Please, specify a doctor');
            return false;
        }
        
        var arr = doctor.split(' ');
        f_name = arr[1];
        l_name = arr[2];
    }

	var amount = inp * coef;
	var request = new XMLHttpRequest();
	request.onreadystatechange = function() {
		if (request.readyState == 4 && request.status == 200) {
			data = JSON.parse(request.responseText);
			if (data['performed']) {
				document.location.reload(true);
			} 
			else {
				alert('Wrong amount!');
				d.value = '';
			}
		}			
	}
		
	request.open('GET', 'ajax/change_amount?id=' + id + '&amount=' + amount + '&f_name=' + f_name + '&l_name=' + l_name, true);
	request.send(null);
	return true;
}

function show_input(id) {
	var d = get_panel(id);
	d.style.visibility = 'visible';
}

function hide_input(id) {
	
	var d = get_panel(id);
	
	if (d.value != '') 
	{
		d.parentElement.onblur = function() {
			d.value = '';
			d.style.visibility = 'hidden';
		}
	}
	else {
	    d.style.visibility = 'hidden';
	}
}

function make_order(id) {
    
    var d = get_panel(id);
    var inp = parseInt(d.value, 10);
    
    if (inp < 1) 
    {
        alert("Please, enter correct amount");
        return false;
    }
    
    var url = '/order_details?' + 'drug_id=' + id + '&amount=' + inp;
    
    centered_window(url, 450, 450);
    d.value = '';
}    
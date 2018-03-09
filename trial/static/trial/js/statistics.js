function change_year(el, diff) {
	var div = el.parentElement;
	var btn = div.getElementsByTagName('button')[0];
	var new_year = parseInt(btn.value) + diff;
	if (new_year <= (new Date()).getFullYear() && new_year >= 2017 ) {
		btn.value = new_year;
		btn.innerHTML = new_year.toString() + '<span class="caret"></span>';
	}
}

//Building google Pie charts - requires JSON with data, title, id_element
function draw_prod_cat(pattern, title, id_element) {

    var data = google.visualization.arrayToDataTable(JSON.parse(pattern));
	var options = {
		width: 800, 
		height: 800, 
		is3D: true,
		chartArea: {left: '7%'},
		title: title,
		fontName: 'Georgia',
	    titleTextStyle: {
			fontName: 'Trebuchet Ms',
	        fontSize: 30
	    },
		backgroundColor: '#f4f6f9'
	}
	
	var formatter = new google.visualization.NumberFormat({prefix: '$', decimalSymbol: '.'});
    formatter.format(data, 1);
	
	var chart = new google.visualization.PieChart(document.getElementById(id_element));
	chart.draw(data, options);
}

//Building google column chart - requires JSON with data and id_element
function draw_month(pattern, id_elem) {

	var data = google.visualization.arrayToDataTable(JSON.parse(pattern));
	var chart = new google.visualization.ColumnChart(document.getElementById(id_elem));
	var options = { backgroundColor: '#f4f6f9', vAxis: {format: '$#,###'}, fontName: 'Georgia' };
	
	var formatter = new google.visualization.NumberFormat({prefix: '$', decimalSymbol: '.'});
    formatter.format(data, 1);
	
	chart.draw(data, options);
}

function resetChart(el, chart_type, month = false, is_category=false) {
	
    if (chart_type == 'all_prod' || chart_type == 'by_categ') 
	{
		var div = el.parentElement.parentElement.parentElement;
		var btn = div.getElementsByTagName('button')[0];
		var year = parseInt(btn.value);
		var data = "?year=" + year + "&month=" + month +"&chart_type=" + chart_type;
		var url = chart_type == 'by_categ' ? '/trial/ajax/get_categ/' : '/trial/ajax/all_prod/'; 
		var title_name = chart_type == 'all_prod' ? 'All products ' : 'Sales by category ';
		var full_title = title_name + (month == '00' ? year : year + '-' + month);
	}
	else if (chart_type == 'by_months')
	{
		var type = is_category ? 'category' : 'product';
		var data = '?type=' + type + '&name=' + el;
		var url = '/trial/ajax/stat_month/';
		var by_months_id = is_category ? '#sel2' : '#sel1';
		
		//Reset default value of other select
		$(by_months_id).val( $(by_months_id + ' option[selected]').val() );
	}
	else
	{
		alert('WRONG CHART TYPE!!!');
	}
	
	//send ajax request to server
	var req = new XMLHttpRequest();
	
	//on ready state - draw chart
	req.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			data = (this.responseText).replace('\'', '');			
			if (chart_type == 'by_categ' || chart_type == 'all_prod') 
			{
				draw_prod_cat(data, full_title, chart_type);
			}
			else 
			{
				draw_month(data, 'by_months');
			}
		}
	}
	
	req.open('GET', url + data, true);
	req.send(data);
    return true;
	}
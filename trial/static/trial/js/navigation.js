function centered_window(url, width, height) {
	window.open(url, '', 'width=' + width + ',height=' + height + ',left=' + ((window.innerWidth - width)/2) + 
	            ',top=' + ((window.innerHeight - height)/2));
    }
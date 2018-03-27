function fillInfo(elem) {
    
    var user = elem.options[elem.selectedIndex].value;
    $('#psw_username').val(user);
    var url = '/trial/ajax/user_info?username=' + user;    
    
    $.getJSON(url, function(res) {
        var rows = $('#info_table tr');
        for (var i = 0; i < 6; i++) {
            (rows[i].querySelectorAll('td')[1]).textContent = res[i];
        }            
    });
    
    return true;
}

function deleteUser() {
    var elem = document.querySelector('#select_user');
    var user = elem.options[elem.selectedIndex].value;
    
    var result = confirm("Do you really want to delete user '" + user +  "' ?");
    if (result) {
        var url = '/trial/ajax/delete_user?username=' + user;
        
        $.ajax(url).done(function() {
                window.location.reload();
            });
    }
    return true;
}
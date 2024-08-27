function playElm(element) {
    let elm = document.getElementById(element);
    elm.play();
}

function pauseElm(element) {
    let elm = document.getElementById(element);
    elm.pause();
}

function newSelection(element, hide, val) {
    let value = document.getElementById(element).value;
    let div = document.getElementById(hide);
    if (value === val) {
        div.style.visibility = 'visible';
    } else {
        div.style.visibility = 'hidden';
    }
}

function changeToLibrary(library_name) {
    $.ajax({ 
        url: '/change_library',
        type: 'POST',
        contentType: 'application/json', 
        data: JSON.stringify({ 'name': library_name }), 
        success: function(response) {},
        error: function(error) { 
            console.log(error); 
        }
    });
}

function changeToRanking(user_id, rank_id) {
    document.location.href = '/'+user_id+'/ranking_results'+'/'+rank_id
}

function changeRating(user_id, ranking_id, song_id, amount) {
    $.ajax({ 
        url: '/update_ranking',
        type: 'POST',
        contentType: 'application/json', 
        data: JSON.stringify({ 'user_id': user_id, 'ranking_id': ranking_id, 'id': song_id, 'amount': amount }), 
        success: function(response) {
            location.reload();
        },
        error: function(error) { 
            console.log(error); 
        } 
    });
}

function loading() {
    $("#loading").show();
    $("#content").hide();
}

function sortTable(table,sort) {
    $.ajax({ 
        url: '/update_table_sort',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ 'table': table, 'sort': sort }), 
        success: function(response) {
            document.location.href = 'ranking_hub'
        },
        error: function(error) { 
            console.log(error); 
        } 
    }); 
}

function sendData() {
    let value = document.getElementById('input').value; 
    $.ajax({ 
        url: '/process', 
        type: 'POST', 
        contentType: 'application/json', 
        data: JSON.stringify({ 'value': value }), 
        success: function(response) { 
            document.getElementById('output').innerHTML = response.result; 
        }, 
        error: function(error) { 
            console.log(error); 
        } 
    }); 
} 
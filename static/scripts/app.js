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

function changeToLibrary(user_id, library_name) {
    document.location.href = '/'+user_id+'/library/'+library_name
}

function changeToRanking(user_id, rank_id) {
    document.location.href = '/'+user_id+'/ranking_results/'+rank_id
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
    let queryParams = new URLSearchParams(window.location.search);
    let table_sort = table+'_sort';
    let table_reverse = table+'_reverse';
    let reverse = false;
    if (queryParams.get(table_sort) === sort) {
        if (queryParams.get(table_reverse) === 'false') {
            reverse = 'true';
        } else {
            reverse = 'false';
        }
    }
    queryParams.set(table_sort, sort);
    queryParams.set(table_reverse, reverse);
    document.location.href = window.location.origin + window.location.pathname + '?' + queryParams
    /*
    let data = {}
    data[table] = sort
    $.ajax({
        url: document.URL,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data), 
        success: function(response) {
            location.reload();
        },
        error: function(error) { 
            console.log(error); 
        } 
    });*/
}
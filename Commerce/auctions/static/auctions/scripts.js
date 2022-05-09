//shows and hides the comments section when clicked
function Comments(a) { // a == number of comments
    var el = document.getElementById('c'); // == comment form
    var el2 = document.getElementById('b'); // == button
    if (el.className == 'hidden') {
        el.className = 'shown';
        el2.innerHTML = 'Comments ◭';
    } else {
        el.className = 'hidden';
        el2.innerHTML = 'Comments (' + a + ') ⧩';
    }
}

//shows and hides the 'add comment' section
function Add() {
    var but = document.getElementById('addb');
    var form = document.getElementById('form');
    but.className = '';
    form.className = 'hidden';
}

//hides the 'bid' button and displays the bid form with the correct values
function Bid(a) { // a == listing price
    form = document.getElementById("bid");
    button = document.getElementById("bidbutton");
    input = document.getElementById("amount");
    form.style = "display: auto;";
    button.style = "display: none;";
    input.setAttribute('placeholder', a + 1);
    input.setAttribute('min', a + 1)
}

//hides all listings with the given category (cat) and switches the color of the button
function Category(cat) {
    var el = document.getElementsByClassName(cat);
    var bt = document.getElementById(cat);
    if (bt.className == 'cat-show') {
        bt.className = 'cat-hide';
        var len = el.length;
        for (var i = len - 1; i >= 0; i--) {
            el[i].className = 'item' + ' ' + cat + ' hidden';
        }
    } else {
        var len = el.length;
        bt.className = 'cat-show';
        for (var i = len - 1; i >= 0; i--) {
            el[i].className = 'item' + ' ' + cat;
        }
    }
}

//hides all listings and turns all filter buttons red
function HideAll() {
    var cat = ['Misc.', 'Community', 'Housing', 'Services', 'Goods', 'Gigs'];
    for (var j = cat.length - 1; j >= 0; j--) {
        var el = document.getElementsByClassName(cat[j]);
        var bt = document.getElementById(cat[j]);
        bt.className = 'cat-hide';
        var len = el.length;
        for (var i = len - 1; i >= 0; i--) {
            if (el[i].className.search('hidden') == -1) {
                el[i].className = el[i].className + ' hidden';
            }
        }
    }
}
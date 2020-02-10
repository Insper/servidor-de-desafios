$(function () {
    var slideDeck = $('.slidedeck');
    slideDeck.focus();
    slideDeck.keydown(function (event) {
        if (event.keyCode === 37) {  // Left
            $('.back-btn')[0].click();
        }
        else if (event.keyCode === 39) {  // Right
            $('.forward-btn')[0].click();
        }
    });
});

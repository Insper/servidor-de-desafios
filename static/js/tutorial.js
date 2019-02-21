function updateArrows() {
    if (curSlideIdx <= 0) $('.back-btn').addClass('disabled');
    else $('.back-btn').removeClass('disabled');
    if (curSlideIdx >= slideIds.length - 1) $('.forward-btn').addClass('disabled');
    else $('.forward-btn').removeClass('disabled');
}

function moveSlide(distance) {
    $('#' + curSlide).hide();
    curSlideIdx += distance;
    if (curSlideIdx < 0) curSlideIdx = 0;
    if (curSlideIdx >= slideIds.length) curSlideIdx = slideIds.length - 1;
    curSlide = slideIds[curSlideIdx];
    $('#' + curSlide).show();
    window.location.hash = curSlide;

    updateArrows();
}

$(function() {
    curSlide = window.location.hash;
    slideIds = [];
    slides = $('.slide');
    var slideDeck = $('.slidedeck');
    slides.each(function(i, slide) {
        slideIds.push(slide.id);
    });
    if (slideIds.length === 0) return;
    if (!curSlide) {
        curSlide = slideIds[0];
        window.location.hash = curSlide;
    }
    else {
        curSlide = curSlide.substr(1);
    }
    curSlideIdx = slideIds.indexOf(curSlide);
    if (curSlideIdx < 0) {
        curSlideIdx = 0;
        curSlide = slideIds[0];
    }
    slides.hide();
    $('#' + curSlide).show();
    updateArrows();
    $('.back-btn').click(function(event) {
        event.preventDefault();
        moveSlide(-1);
    });
    $('.forward-btn').click(function(event) {
        event.preventDefault();
        moveSlide(1);
    });
    slideDeck.focus();
    slideDeck.keydown(function(event) {
        console.log(event.keyCode);
        if (event.keyCode === 37) {  // Left
            moveSlide(-1);
        }
        else if (event.keyCode === 39) {  // Right
            moveSlide(1);
        }
    });
    $('#toggleSlide').click(function(event) {
        event.preventDefault();
        var SHOW_ALL = 'Mostrar tudo';
        var SHOW_SLIDE = 'Mostrar somente slide';
        if ($(this).text() === SHOW_ALL) {
            slides.show();
            $(this).text(SHOW_SLIDE);
        }
        else {
            slides.hide();
            $(this).text(SHOW_ALL);
            moveSlide(0);
        }
    });
    if (slideIds.length <= 1) {
        $('.slide-ctrl').hide();
    }
});
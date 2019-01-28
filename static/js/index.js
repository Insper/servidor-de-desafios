var visibleTags = [];
var enabledClass = 'badge-primary';
var disabledClass = 'badge-secondary';

function updateVisible() {
    $('.challenge-tag').each(function(index, element) {
        $(element).removeClass(enabledClass);
        $(element).removeClass(disabledClass);
        if (visibleTags.indexOf(element.innerHTML) < 0) {
            $(element).addClass(disabledClass);
        }
        else {
            $(element).addClass(enabledClass);
        }
    });
    $('.challenge-row').each(function(index, element) {
        var tags = $(element).find('.challenge-tags').children();
        var visible = false;
        for (var i = 0; i < tags.length; i++) {
            if (visibleTags.indexOf(tags[i].innerHTML) >= 0) {
                visible = true;
                break;
            }
        }
        if (visible) $(element).show();
        else $(element).hide();
    });
}

$(document).ready(function() {
    $('.filter-challenge-tag').click(function(event) {
        event.preventDefault();
        var tagName = this.innerHTML;
        var index = visibleTags.indexOf(tagName);
        if (index < 0) {
            visibleTags.push(tagName);
        }
        else {
            visibleTags.splice(index, 1);
        }
        updateVisible();
    });

    var urlParams = new URLSearchParams(window.location.search);
    var tag = urlParams.get('tag');
    visibleTags = [];
    if (tag != null) visibleTags = [tag];
    else {
        $('.filter-challenge-tag').each(function(index, element) {
            visibleTags.push(element.innerHTML);
        });
    }
    updateVisible();
});
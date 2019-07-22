function serializeBlockList() {
    var newBlockList = [];
    var cards = document.querySelectorAll(".challengeblock");
    for (var j = 0; j < cards.length; j++) {
        var card = cards[j];
        var name = card.getElementsByClassName("challengeblock-name")[0].value;
        var releaseDate = card.getElementsByClassName("challengeblock-releasedate")[0].value;
        var challengesUL = card.getElementsByClassName("challengeblock-challenges")[0];
        var challengeLIs = challengesUL.getElementsByClassName("challenge");
        var challenges = [];
        for (var k = 0; k < challengeLIs.length; k++) {
            var li = challengeLIs[k];
            challenges.push(li.value);
        }
        newBlockList.push({
            "name": name,
            "release_date": releaseDate,
            "challenges": challenges,
        });
    }
    return JSON.stringify(newBlockList);
}

function initSortable(blocks) {
    sortable('.sortable-list', 'destroy');
    var list = sortable('.sortable-list', {
        acceptFrom: '.sortable-list'
    });
}

window.onload = function(){

    var addBlock = document.getElementById("add-block");
    var blockContainer = document.getElementById("block-container");
    var blocks = document.getElementsByName("blocks")[0];
    blocks.value = serializeBlockList();

    initSortable(blocks);

    addBlock.onclick = function() {
        var newBlock = document.getElementById("block-template").content.cloneNode(true);

        // Create
        blockContainer.insertBefore(newBlock, addBlock);

        initSortable(blocks);

        // We can't use newBlock, because it is a fragment that is not connected to its parents
        var allCards = blockContainer.querySelectorAll(".card");
        var insertedBlock = allCards[allCards.length - 1];
        DateTimeShortcuts.addCalendar(insertedBlock.querySelector(".vDateField"));
    }

    django.jQuery('#class_form').submit(function() {
        blocks.value = serializeBlockList();
        return true;
    });
}

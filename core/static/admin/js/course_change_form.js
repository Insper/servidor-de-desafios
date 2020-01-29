function serializeBlockList() {
    var newBlockList = [];
    var cards = document.querySelectorAll(".bloco");
    for (var j = 0; j < cards.length; j++) {
        var card = cards[j];
        var inicio = card.getElementsByClassName("bloco-inicio")[0].value;
        var fim = card.getElementsByClassName("bloco-fim")[0].value;
        var challengesUL = card.getElementsByClassName("bloco-exercicios")[0];
        var challengeLIs = challengesUL.getElementsByClassName("exercicio");
        var challenges = [];
        for (var k = 0; k < challengeLIs.length; k++) {
            var li = challengeLIs[k];
            challenges.push(li.value);
        }
        newBlockList.push({
            "inicio": inicio,
            "fim": fim,
            "exercicios": challenges,
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

window.onload = function () {

    var addBlock = document.getElementById("adiciona-bloco");
    var blockContainer = document.getElementById("bloco-container");
    var blocks = document.getElementsByName("blocos")[0];
    blocks.value = serializeBlockList();

    initSortable(blocks);

    addBlock.onclick = function () {
        var newBlock = document.getElementById("bloco-template").content.cloneNode(true);

        // Create
        blockContainer.insertBefore(newBlock, addBlock);

        initSortable(blocks);

        // We can't use newBlock, because it is a fragment that is not connected to its parents
        var allCards = blockContainer.querySelectorAll(".card");
        var insertedBlock = allCards[allCards.length - 1];
        insertedBlock.querySelectorAll(".vDateField").forEach(function (e) {
            DateTimeShortcuts.addCalendar(e);
        });
    }

    django.jQuery('#turma_form').submit(function () {
        blocks.value = serializeBlockList();
        return true;
    });
}

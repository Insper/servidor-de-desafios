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

let blocoAtual = null;
function toggleExercicios() {
    let novoBloco = django.jQuery(this).parents('.bloco');
    let ativa;
    if (novoBloco.hasClass("selected")) {
        novoBloco.removeClass("selected");
        novoBloco.find(".adicionar-exercicios").attr("value", "Adicionar Exercícios")
        ativa = false;
    }
    else {
        if (blocoAtual != null) {
            blocoAtual.removeClass("selected");
            blocoAtual.find(".adicionar-exercicios").attr("value", "Adicionar Exercícios")
        }
        novoBloco.addClass("selected");
        novoBloco.find(".adicionar-exercicios").attr("value", "Esconder Exercícios")
        ativa = true;
    }

    let exerciciosDisponiveis = django.jQuery(".exercicios-disponiveis");
    let adicionarExercicios = django.jQuery("#adicionar-exercicios");
    if (ativa) {
        exerciciosDisponiveis.removeClass("hidden");
        adicionarExercicios.removeAttr("disabled");
    }
    else {
        exerciciosDisponiveis.addClass("hidden");
        adicionarExercicios.attr("disabled", true);
    }

    blocoAtual = novoBloco;
}

function reordenaExercicios(bloco) {
    exercicios = bloco.find(".exercicio");
    exercicios.sort(function (a, b) {
        return parseInt(a.value) - parseInt(b.value)
    });
    exercicios.detach().appendTo(bloco);
}

window.onload = function () {

    var addBlock = document.getElementById("adiciona-bloco");
    var blockContainer = document.getElementById("bloco-container");
    var blocks = document.getElementsByName("blocos")[0];
    blocks.value = serializeBlockList();

    let collapser = document.getElementById("fieldsetcollapser1");
    collapser.click();

    // Toggle exercícios
    django.jQuery(".adicionar-exercicios").click(toggleExercicios);
    django.jQuery("#adicionar-exercicios").click(function () {
        let selecionados = django.jQuery(".sem-bloco input[type='checkbox']:checked");
        let novaLista = blocoAtual.find(".bloco-exercicios");
        let lis = selecionados.parents(".sem-bloco");
        lis.appendTo(novaLista);
        lis.removeClass("sem-bloco");
        lis.addClass("em-bloco");
        selecionados.prop("checked", false);
        reordenaExercicios(novaLista);
    });
    django.jQuery("#remover-exercicios").click(function () {
        let selecionados = django.jQuery(".em-bloco input[type='checkbox']:checked");
        let novaLista = django.jQuery("#lista-disponiveis");
        let lis = selecionados.parents(".em-bloco");
        lis.appendTo(novaLista);
        lis.removeClass("em-bloco");
        lis.addClass("sem-bloco");
        selecionados.prop("checked", false);
        reordenaExercicios(novaLista);
    });

    // Toggle tags
    django.jQuery(".select-tag").click(function () {
        let tag = django.jQuery(this).text();
        django.jQuery(".sem-bloco .tag-" + tag).prop("checked", true);
        return false;
    });
    django.jQuery("#desseleciona-tudo").click(function () {
        django.jQuery(".sem-bloco input[type=checkbox]").prop("checked", false);
        return false;
    });

    // Cria bloco
    addBlock.onclick = function () {
        var newBlock = document.getElementById("bloco-template").content.cloneNode(true);

        // Create
        blockContainer.insertBefore(newBlock, addBlock);

        // We can't use newBlock, because it is a fragment that is not connected to its parents
        var allCards = blockContainer.querySelectorAll(".card");
        var insertedBlock = allCards[allCards.length - 1];
        insertedBlock.querySelectorAll(".vDateField").forEach(function (e) {
            DateTimeShortcuts.addCalendar(e);
        });

        django.jQuery(django.jQuery(insertedBlock).find(".adicionar-exercicios")).click(toggleExercicios);
    }

    django.jQuery('#turma_form').submit(function () {
        blocks.value = serializeBlockList();
        return true;
    });
}

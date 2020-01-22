$(function() {
    $(".ativa-contexto").click(function() {
        let ativo = $(this).prop("checked");
        let box = $("#box-" + $.escapeSelector($(this).prop("id")));
        if (ativo) {
            box.removeClass("box-inativo");
            box.find("input[type='text']").attr("disabled", false)
        }
        else {
            box.addClass("box-inativo");
            box.find("input[type='text']").attr("disabled", true)
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById("mostrar-nomes").addEventListener('change', (event) => {
        let classAntiga;
        let classNova;
        if (event.target.checked) {
            classAntiga = 'esconde';
            classNova = 'mostra';
        } else {
            classAntiga = 'mostra';
            classNova = 'esconde';
        }
        let nomes = document.getElementsByClassName("nome-aluno");
        for (let i = 0; i < nomes.length; i++) {
            nomes[i].classList.remove(classAntiga);
            nomes[i].classList.add(classNova);
        }
    });
});

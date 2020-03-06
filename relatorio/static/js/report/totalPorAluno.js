document.addEventListener('DOMContentLoaded', function () {
    Plotly.newPlot('plotHere', [{
        y: submissoes, type: 'bar', marker: {
            color: 'rgb(158,202,225)',
            opacity: 0.6,
            line: {
                color: 'rgb(8,48,107)',
                width: 1.5
            }
        }
    }]);
});

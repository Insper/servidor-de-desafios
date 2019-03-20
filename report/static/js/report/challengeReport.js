document.addEventListener('DOMContentLoaded', function(){
    var data = [];
    for (var key in challengeData) {
        data.push({
            y: challengeData[key],
            type: 'box',
            name: key
        })
    }

    Plotly.newPlot('plotHere', data);
});
document.addEventListener('DOMContentLoaded', function(){
    var data = [];
    for (var key in submissionData) {
        data.push({
            x: submissionDates[key],
            y: submissionData[key],
            type: 'scatter',
            name: key
        })
    }

    Plotly.newPlot('plotHere', data);
});
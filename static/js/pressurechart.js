



function createPressureChart(chartElement) {
    /*
    Create a pressure chart using Chart.js, return the following functions: addDatapoint, reset, getJSON.
    */
    var pChart = new Chart(chartElement, {
    type: 'scatter',
    data: {
      datasets: [{
      borderColor: ['rgba(0, 0, 209, 1)'],
      backgroundColor: ['rgba(0, 0, 209, 0.2)'],
      data: []  //array element format: {x: int, y: int}
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 2,
      animation: false,
      legend: {
        display: false,
        labels: {
          usePointStyle: true,
        },
        position: 'right',
        onClick: (e) => e.stopPropagation()
      },
      title: {
        display: false,
        text: 'Instrument reading',
        position: 'bottom',
        fontSize: 16,
        },
      scales: {
        yAxes: [{
          ticks : {
            min: 0
          },
          scaleLabel: {
            display: true,
            labelString: "Pressure (psig)",
            fontSize: 15,
          }
        }],
        xAxes: [{
          gridLines: {
            display: false
          },
          ticks : {
            min: 0
          },
          scaleLabel: {
            display: true,
            labelString: "Time (s)",
            fontSize: 15,
          }
        }]
      },
    }
    });
  
    const addDatapoint = (seconds, pressure) => {
      pChart.data.datasets[0]["data"].push({"x": seconds, "y": pressure});
      pChart.update();   
    }
  
    const reset = () => {
      pChart.data.datasets[0]["data"] = [];
      pChart.update();   
    }
  
    const getJSON = () => {
      return JSON.stringify(pChart.data.datasets[0]["data"])
    }
  
    return {addDatapoint: addDatapoint, reset: reset, getJSON: getJSON}
  }
  
  
  
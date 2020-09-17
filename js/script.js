
const chart_data = {
    idx:0,
    labels:[],
    rss_dataset:[],
    peak_dataset:[],
    data_dataset:[],
    is_limit_on:0,
    printIntroduction: function() {
        console.log(`My name is ${this.name}. Am I human? ${this.isHuman}`);
    }
};

const LIM_HIST_DEP = 30;

g_is_limit_on_1 = 1;
g_is_limit_on_2 = 1;

files = ['air4971.local.json', 'air4971-2.local.json'];

async function draw_chart(cd)
{
    var ctx = $(`#chart-${cd.idx}`).get(0).getContext("2d");

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: cd.labels,
            datasets: [
                {
                    label: 'RSS',
                    backgroundColor: 'rgb(0, 255, 0)',
                    borderColor: 'rgb(0, 255, 0)',
                    data: cd.rss_dataset,
                    fill: false,
                    pointRadius: 2,
					pointHoverRadius: 5
                },
                {
                    label: 'Peak',
                    backgroundColor: 'rgb(255, 0, 0)',
                    borderColor: 'rgb(255, 0, 0)',
                    data: cd.peak_dataset,
                    fill: false,
                    pointRadius: 2,
					pointHoverRadius: 5
                },
                {
                    label: 'Data',
                    backgroundColor: 'rgb(0, 0, 255)',
                    borderColor: 'rgb(0, 0, 255)',
                    data: cd.data_dataset,
                    fill: false,
                    pointRadius: 2,
					pointHoverRadius: 5
                }
            ]
        },

        options: {
            responsive: true,
            animation: {
                duration: 0
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'timestamp'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: ''
                    }
                }]
            }
        }
    });
}

async function update_chart()
{
    await fetch_data();

    for (i = 0; i < 2; i++)  {
        $(`#chart-${i + 1}`).replaceWith(`<canvas id="chart-${i + 1}"></canvas>`);
        //$('.chartjs-size-monitor').remove();
        draw_chart(chartdata_list[i]);
    }
    
    setTimeout (update_chart, 1000);
}

$(document).ready(function() {
    update_chart();

    $('#limit-1').prop("checked", true);
    $('#limit-2').prop("checked", true);

    $('#limit-1').change(function() {
        if(this.checked) {
            g_is_limit_on_1 = 1;
        } else {
            g_is_limit_on_1 = 0;
        }
    });

    $('#limit-2').change(function() {
        if(this.checked) {
            g_is_limit_on_2 = 1;
        } else {
            g_is_limit_on_2 = 0;
        }   
    });
});

function convertEpochToSpecificTimezone(epoch, offset){
    var d = new Date(epoch);
    var utc = d.getTime() + (d.getTimezoneOffset() * 60000);  //This converts to UTC 00:00
    var nd = new Date(utc + (3600000*offset));
    return nd.toLocaleString();
}

async function fetch_data() {
    chartdata_list = []

    for (i = 0; i < 2; i++) {
        const cd = Object.create(chart_data);

        const response = await fetch(files[i]);
        const data = await response.json();
        const start = data.length - LIM_HIST_DEP;

        cd.idx = i + 1;

        cd.labels = []
        cd.rss_dataset = []
        cd.peak_dataset = []
        cd.data_dataset = []

        j = 0;
        data.forEach(obj => {
            if ((i == 0 && g_is_limit_on_1) || (i == 1 && g_is_limit_on_2)) {
                if (j++ < start) {
                    return;
                }
            }
    
            Object.entries(obj).forEach(([key, value]) => {
    
                if (key === 'timestamp') {
                    cd.labels.push(value);
                }
    
                if (key === 'rss') {
                    cd.rss_dataset.push(value);
                } else if (key === 'peak') {
                    cd.peak_dataset.push(value);
                } else if (key === 'data') {
                    cd.data_dataset.push(value);
                }
            });
        });

        chartdata_list.push(cd);
    }

    return 0;
}
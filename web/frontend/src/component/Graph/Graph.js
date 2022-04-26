import h337 from "heatmap.js";

import "heatmap.js";

import React, { Component, useRef, useEffect } from "react";
import Layout from "../../Layout/Layout";
import "./Graph.css";
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
  Title,
} from 'chart.js';
import { Bubble, Bar, Pie, Line } from 'react-chartjs-2'
import ChartDataLabels from 'chartjs-plugin-datalabels';
import {CategoryScale} from 'chart.js';
import Chart from 'chart.js/auto'


ChartJS.register(LinearScale, PointElement, Tooltip, Legend,Title, ChartDataLabels);
const Graph = () => {
  // 추출한 데이터의 x, y좌표와 그려줄 x, y좌표 변환 필요
  // 추출했을 당시 세로, 그려줄 좌표는 가로
  // width: 450, height: 271
  const points = [];
  const jsonData = require("../../tempData/playerCoords.json");
  // console.log(jsonData[0]);
  // console.log(typeof jsonData[0]);
  jsonData.forEach((data) => {
    const point = {
      x: parseInt(data.y_0),
      y: parseInt(data.x_0),
      value: 1,
    };
    points.push(point);
  });

  const max = 50;
  const playerData = {
    max: max,
    data: points,
  };

  const frontPoint = [];
  const backPoint = [];
  // const bounceJsonData = require("../../tempData/bounces.json");
  const bounceJsonData = [[452, 1191,'front_dueceside_right', 27 ], [494, 397,'back_adside_left', 119], [376, 1304,'front_dueceside_center', 184], [312, 546,'back_adside_center', 257], [628, 1285,'front_adside_center', 366], [676, 471,'back_dueceside_center', 431], [403, 720,'back_adside_left', 591], [511, 789,'back_dueceside_right', 739], [514, 889,'front_adside_left', 894]];
  bounceJsonData.forEach((data,i)=>{
    const point = {
      x: parseInt(data[1]),
      y: parseInt(data[0]) + data[3]*0.1,
      r: 10,
    };
    if(data[2].includes('front')){
      point.x += 0.1*(Object.keys(frontPoint).length + 1)
      frontPoint.push(point);
    }else{
      point.x += 0.1*(Object.keys(backPoint).length + 1)
      backPoint.push(point);
    }
  })
  
  const charData = {
    datasets:[
      {
        label:'back',
        type: 'bubble',
        backgroundColor:'rgb(100, 1, 93)',
        data: frontPoint,
      },
      {
        label:'front',
        type: 'bubble',
        backgroundColor:'rgb(54, 162, 235)',
        data: backPoint,
      },
      
    ],
  }

  const options = {
    scales:{
     y:{
       display:false,
     },
     x:{
       display:false,
     }
    },     
    plugins:{
      // title:{
      //   display:true,
      //   text:'hihihi',
      //   color:'#000',
      // },
      legend:{
        display:false,
      },
      tooltip:{
        callbacks: {
          label: function(context) {
              let label = context.dataset.label || '';
              if (label) {
                  label += ': ';
                  label += `(${parseInt(context.parsed.x)}, ${parseInt(context.parsed.y)})`
              }
              return label;
          },
          // footer: function(context) {
          //   return `${context[0].dataIndex+1}`
          // },
        }
      },
      datalabels: {
        display: true,
        color: "white",
        align: "center",
        // padding: {
        //   right: 2
        // },
        labels: {
          // padding: { top: 10 },
          title: {
            font: {
              weight: "bold"
            }
          },
          // value: {
          //   color: "red"
          // }
        },
        formatter: function (value) {
          console.log(value)
          return (value.x % 1).toFixed(1)*10;
        }
      },
      
      
    },
    
  }

  useEffect(() => {
    const playerHeatmapInstance = h337.create({
      container: document.querySelector(".player-heatmap"),
      opacity: "0.3",
    });
    // console.log(playerData);
    // console.log(playerHeatmapInstance);
    playerHeatmapInstance.setData(playerData);

  }, []);

  //-----------------------------------------------------------------------------------------게임정보 bar chart-------------------------------------------------------------------------
  const barChartData = { 
    labels: ["역대 전적 승률", "서브 평균속도", "총 점수", "서브 성공률", "역대 이동거리"],
    datasets: [//임시로 넣은 데이터 상대와 나 비교해서 넣을방법 구색
        {
        label: "나",
        stack: "Stack 0",
        backgroundColor: "#d41111",
        data: [56, 98, 250, 87, 1435],
        },
        {
        label: "상대",
        stack: "Stack 0",
        backgroundColor: "#3765b0",
        data: [44, 103, 150, 13, 1503].map((k) => -k),
        },
    ],
};
const  Gameoptions = {
indexAxis : 'y',
legend: { display: false },
title: {
display: true,
text: '경기 스텟 비교 분석'
}
}

  //-----------------------------------------------------------------------------------------승률 pie chart-------------------------------------------------------------------------
const WinPointOptions = {
  legend: { display: false },
title: {
display: true,
text: '승패 비율'
}
}
  const pieChartData = {
    labels:['ME','Other'],
    datasets:[{
      data: [64, 36],
      backgroundColor:[
        'rgb(225, 99, 132)',
        'rgb(225,205,86)'
      ]}
    ]
  }
  
  //-----------------------------------------------------------------------------------------활동량 line chart-------------------------------------------------------------------------
  const distanceonfig = {
    type: 'line',
    labels: ['1경기', '2경기', '3경기'],
    datasets: [{
      label : 'ME',
      data : [142, 536, 314],
      borderColor:"rgb(222, 99, 132)",
      backgroundColor:"rgb(222, 99, 132)",
      file:true,
      lineTension: 0
    },
    {
      label : 'Other',
      data : [416, 875, 222],
      borderColor:"rgb(222, 205, 86)",
      backgroundColor:"rgb(222, 205, 86)",
      file:true,
      lineTension: 0

    }],
  }
  const distanceOptions= {
    options: {
      responsive: true,

        title: {
            display: true,
            text: '라인 차트 테스트'
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
                    labelString: 'x축'
                }
            }],
            yAxes: [{
                display: true,
                ticks: {
                    suggestedMin: 0,
                },
                scaleLabel: {
                    display: true,
                    labelString: 'y축'
                }
            }]
        }
      }
    }


return (
  <Layout>
    <div className="graph">
      <div className="player-heatmap"></div>
      <div className="graph-info">
        <div>
          <h2>총 이동 거리</h2>
          <p>000m</p>
        </div>
        <div>
          <h2>총 000</h2>
          <p>000</p>
        </div>
      </div>
      <div className="bounce">
        <Bubble options={options} data = {charData} width={450} height={271}/>
      </div>
      <div>
          <Bar data={barChartData} width={450} height={271} options={Gameoptions}/>
    </div>
    <div>
          <Pie data={pieChartData} width={450} height={271} options={WinPointOptions}/>
    </div>
    <div>
          <Line data={distanceonfig} width={450} height={271} options={distanceOptions}/>
    </div>
    </div>
  </Layout>
);
};

export default Graph;

const MONTHS=['May','Jun','Jul','Ago','Sep','Oct','Nov','Dic','Ene','Feb','Mar','Abr'];

const DATA={
totals:[257,16994,64495,51312,50145,26895,28729,195085,137409,190802,135104,249700],
recesa:[0,0,0,0,700,4910,4357,0,0,10115,40038,121815],
redelsa:[0,16994,64495,51312,49445,21985,24372,195085,137409,180687,95066,127885],
};

const PRODUCTS=[
{name:'Perno S/Muestra',val:265074},
{name:'Barra lisa GR55 25mm',val:45865},
{name:'Tornillo lámina 14×1½',val:30940},
{name:'Tornillo hex. A325 1×3½',val:30906},
{name:'Tuerca hex. A325 1.3/8',val:26250},
];

const YELLOW='#F5C400';
const BLACK='#1a1a1a';

let lineChart;
let barChart;
let donutChart;

function initLine(filteredIndex=null){

const labels=filteredIndex!==null?[MONTHS[filteredIndex]]:MONTHS;
const totals=filteredIndex!==null?[DATA.totals[filteredIndex]]:DATA.totals;

if(lineChart){
lineChart.destroy();
}

lineChart=new Chart(document.getElementById('lineChart'),{
type:'line',
data:{
labels:labels,
datasets:[{
data:totals,
borderColor:YELLOW,
backgroundColor:'rgba(245,196,0,.10)',
fill:true,
tension:.35
}]
},
options:{
responsive:true,
maintainAspectRatio:false,
plugins:{legend:{display:false}}
}
});

}

function initBar(filteredIndex=null){

const labels=filteredIndex!==null?[MONTHS[filteredIndex]]:MONTHS;

const recesa=filteredIndex!==null?[DATA.recesa[filteredIndex]]:DATA.recesa;

const redelsa=filteredIndex!==null?[DATA.redelsa[filteredIndex]]:DATA.redelsa;

if(barChart){
barChart.destroy();
}

barChart=new Chart(document.getElementById('barChart'),{
type:'bar',
data:{
labels:labels,
datasets:[
{
label:'RECESA',
data:recesa,
backgroundColor:BLACK
},
{
label:'REDELSA',
data:redelsa,
backgroundColor:YELLOW
}
]
},
options:{
responsive:true,
maintainAspectRatio:false,
plugins:{legend:{display:false}}
}
});

}

function initDonut(){

if(donutChart){
donutChart.destroy();
}

donutChart=new Chart(document.getElementById('donutChart'),{
type:'doughnut',
data:{
labels:['RECESA','REDELSA'],
datasets:[{
data:[181935,964992],
backgroundColor:[BLACK,YELLOW]
}]
},
options:{
responsive:true,
maintainAspectRatio:false,
plugins:{legend:{display:false}}
}
});

}

function renderProducts(){

const container=document.getElementById('products');

container.innerHTML='';

PRODUCTS.forEach(p=>{

const item=document.createElement('div');

item.className='prod-item';

item.innerHTML=`
<div>${p.name}</div>
<div>Q${Math.round(p.val/1000)}k</div>
`;

container.appendChild(item);

});

}

document.addEventListener('DOMContentLoaded',()=>{

initLine();
initBar();
initDonut();
renderProducts();

const monthFilter=document.getElementById('monthFilter');

monthFilter.addEventListener('change',(e)=>{

const value=e.target.value;

if(value==='all'){
initLine();
initBar();
}else{
initLine(Number(value));
initBar(Number(value));
}

});

});

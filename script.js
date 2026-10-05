const root=document.documentElement;
const navLinks=[...document.querySelectorAll('.nav-link')];
const sections=[...document.querySelectorAll('[data-section]')];
const progress=document.querySelector('.reading-progress');
const dots=[...document.querySelectorAll('.section-dots a')];

function updateNavigation(){
  const max=Math.max(1,document.documentElement.scrollHeight-innerHeight);
  progress.style.transform=`scaleX(${Math.min(1,scrollY/max)})`;
  let current=sections[0];
  const activation=scrollY+innerHeight*.3;
  sections.forEach(section=>{if(section.offsetTop<=activation)current=section});
  const id=current.id==='overview'?'home':current.id;
  navLinks.forEach(link=>link.classList.toggle('is-active',link.hash===`#${id}`));
  dots.forEach(dot=>dot.classList.toggle('is-current',dot.hash===`#${current.id}`));
}

addEventListener('scroll',updateNavigation,{passive:true});
addEventListener('resize',updateNavigation);
updateNavigation();

const observer=new IntersectionObserver(entries=>{
  entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('is-visible');observer.unobserve(entry.target)}});
},{threshold:.13});
document.querySelectorAll('.reveal').forEach(el=>observer.observe(el));

const themeButton=document.querySelector('[data-theme]');
const savedTheme=localStorage.getItem('sc-theme');
if(savedTheme==='dark'||(!savedTheme&&matchMedia('(prefers-color-scheme: dark)').matches))root.classList.add('dark');
themeButton.addEventListener('click',()=>{
  root.classList.toggle('dark');
  localStorage.setItem('sc-theme',root.classList.contains('dark')?'dark':'light');
});

const dialog=document.querySelector('.search-dialog');
const searchInput=document.querySelector('#site-search');
const results=document.querySelector('.search-results');
const pages=[
  ['Home','#home'],['Overview','#overview'],['Dataset','#dataset'],['Demo & Visualization','#demo'],['Research Paper','#paper'],['About','#about']
];
function renderResults(query=''){
  const matches=pages.filter(([name])=>name.toLowerCase().includes(query.toLowerCase()));
  results.innerHTML=matches.map(([name,href])=>`<a class="search-result" href="${href}">${name}</a>`).join('')||'<p>No matching section.</p>';
  results.querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>dialog.close()));
}
document.querySelector('[data-search]').addEventListener('click',()=>{renderResults();dialog.showModal();setTimeout(()=>searchInput.focus(),30)});
searchInput.addEventListener('input',event=>renderResults(event.target.value));

const chartPaths={
  time:'M0 100L12 94 24 104 36 88 48 109 60 96 72 102 84 67 96 112 108 86 120 101 132 91 144 107 156 81 168 101 180 97 192 72 204 116 216 94 228 103 240 86 252 109 264 92 276 98 288 51 300 130 312 90 324 105 336 82 348 112 360 93 372 100 384 63 396 118 408 91 420 105 432 84 444 108 456 95 468 101 480 76 492 113 504 89 516 102 528 92 540 107 552 96 560 100',
  frequency:'M0 150L20 149 40 147 60 142 80 132 100 118 120 96 140 72 160 45 180 22 200 57 220 108 240 139 260 148 280 150 300 148 320 139 340 111 360 54 380 26 400 65 420 119 440 143 460 149 480 150 500 149 520 147 540 145 560 144',
  spectrogram:'M0 128L40 112 80 126 120 86 160 116 200 62 240 105 280 42 320 98 360 55 400 113 440 72 480 121 520 91 560 114'
};
document.querySelectorAll('[data-chart]').forEach(button=>button.addEventListener('click',()=>{
  document.querySelectorAll('[data-chart]').forEach(item=>item.classList.toggle('is-selected',item===button));
  const line=document.querySelector('[data-chart-line]');
  const area=document.querySelector('[data-chart-area]');
  const d=chartPaths[button.dataset.chart];
  line.setAttribute('d',d);
  area.setAttribute('d',`${d}V190H0Z`);
}));

const root=document.documentElement;
document.querySelectorAll('[data-resource]').forEach(link=>{
  const url=window.FARSCAD_LINKS?.[link.dataset.resource];
  if(url&&/^https?:\/\//i.test(url)){
    link.href=url;link.target='_blank';link.rel='noopener noreferrer';
    link.removeAttribute('aria-disabled');link.removeAttribute('tabindex');
    link.querySelector('span').textContent='↗';
  }else{link.addEventListener('click',event=>event.preventDefault())}
});
const navLinks=[...document.querySelectorAll('.nav-link')];
const sections=navLinks.map(link=>document.querySelector(link.hash)).filter(Boolean);
const progress=document.querySelector('.reading-progress');

function updateNavigation(){
  const max=Math.max(1,document.documentElement.scrollHeight-innerHeight);
  progress.style.transform=`scaleX(${Math.min(1,scrollY/max)})`;
  let current=sections[0];
  const activation=scrollY+parseFloat(getComputedStyle(root).getPropertyValue('--nav-height'))+40;
  sections.forEach(section=>{if(section.offsetTop<=activation)current=section});
  const id=current.id;
  navLinks.forEach(link=>link.classList.toggle('is-active',link.hash===`#${id}`));
}

addEventListener('scroll',updateNavigation,{passive:true});
addEventListener('resize',updateNavigation);
updateNavigation();

const observer=new IntersectionObserver(entries=>{
  entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('is-visible');observer.unobserve(entry.target)}});
},{threshold:.13});
document.querySelectorAll('.reveal').forEach(el=>observer.observe(el));

const themeButton=document.querySelector('[data-theme]');
// Anonymous hosting uses an opaque-origin sandbox: storage may throw SecurityError.
// Theme persistence is optional and must not prevent dataset controls initializing.
let savedTheme=null;
try{savedTheme=localStorage.getItem('sc-theme')}catch{}
if(savedTheme==='dark'||(!savedTheme&&matchMedia('(prefers-color-scheme: dark)').matches))root.classList.add('dark');
themeButton.addEventListener('click',()=>{
  root.classList.toggle('dark');
  try{localStorage.setItem('sc-theme',root.classList.contains('dark')?'dark':'light')}catch{}
});

const dialog=document.querySelector('.search-dialog');
const searchInput=document.querySelector('#site-search');
const results=document.querySelector('.search-results');
const pages=[
  ['Home','#home'],['Overview','#overview'],['Implementation','#implementation'],['Dataset','#dataset'],['Research Paper','#paper'],['About','#about']
];
function renderResults(query=''){
  const matches=pages.filter(([name])=>name.toLowerCase().includes(query.toLowerCase()));
  results.innerHTML=matches.map(([name,href])=>`<a class="search-result" href="${href}">${name}</a>`).join('')||'<p>No matching section.</p>';
  results.querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>dialog.close()));
}
document.querySelector('[data-search]').addEventListener('click',()=>{renderResults();dialog.showModal();setTimeout(()=>searchInput.focus(),30)});
searchInput.addEventListener('input',event=>renderResults(event.target.value));

const carousel=document.querySelector('.algorithm-carousel');
const slideButtons=[...document.querySelectorAll('[data-slide]')];
const previous=document.querySelector('[data-slide-prev]');
const next=document.querySelector('[data-slide-next]');
let slideIndex=0;
const algorithmSlides=[...carousel.querySelectorAll('.algorithm-slide')];
algorithmSlides.forEach(slide=>{
  const column=document.createElement('div');
  column.className='dataset-right-column';
  const card=slide.querySelector('.flip-card');
  card.before(column);column.append(card);
});
function syncSlides(){
  algorithmSlides.forEach((slide,index)=>{slide.hidden=index!==slideIndex});
  slideButtons.forEach((button,index)=>button.setAttribute('aria-pressed',String(index===slideIndex)));
  previous.disabled=slideIndex===0;next.disabled=slideIndex===2;
  document.querySelector('[data-slide-status]').textContent=`${slideIndex+1} / 3`;
}
function showSlide(index){slideIndex=Math.max(0,Math.min(algorithmSlides.length-1,index));syncSlides()}
slideButtons.forEach(button=>button.addEventListener('click',()=>showSlide(Number(button.dataset.slide))));
previous.addEventListener('click',()=>showSlide(slideIndex-1));next.addEventListener('click',()=>showSlide(slideIndex+1));
carousel.addEventListener('keydown',event=>{if(event.key==='ArrowRight'||event.key==='ArrowLeft'){event.preventDefault();showSlide(slideIndex+(event.key==='ArrowRight'?1:-1))}});
// Keep existing Home navigation links working without changing the accepted hero.
document.querySelectorAll('a[href="#demo"]').forEach(link=>link.addEventListener('click',event=>{event.preventDefault();document.querySelector('#dataset').scrollIntoView({behavior:'smooth'});carousel.focus({preventScroll:true})}));
syncSlides();

document.querySelectorAll('.flip-card').forEach(card=>{
  const front=card.querySelector('.flip-face-front');
  const back=card.querySelector('.flip-face-back');
  const trigger=card.querySelector('.flip-front');
  const close=card.querySelector('.flip-back');
  function flip(open){
    card.classList.toggle('is-flipped',open);
    front.inert=open;back.inert=!open;
    front.setAttribute('aria-hidden',String(open));back.setAttribute('aria-hidden',String(!open));
    trigger.setAttribute('aria-expanded',String(open));
    (open?close:trigger).focus({preventScroll:true});
  }
  trigger.addEventListener('click',()=>flip(true));
  close.addEventListener('click',()=>flip(false));
  card.addEventListener('keydown',event=>{if(event.key==='Escape'&&card.classList.contains('is-flipped')){event.preventDefault();flip(false)}});
});

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

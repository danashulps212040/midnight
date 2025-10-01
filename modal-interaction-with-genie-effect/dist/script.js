var element = document.querySelector("#element"),
    wrapper = document.querySelector("#modal-with-genie-effect"),
    close = document.querySelector("#close"),
    word = document.querySelector("#word"),
    open = document.querySelector("#open-modal-ctr"),
    step0 = "#step-0",
    step2 = "#step-2",
    step3 = "#step-3";

var tl = new TimelineMax();

close.addEventListener("click", function(){

  wrapper.classList.add("active");

  tl
    .to(element, .3, {
      delay: .7,
      y: "-15px",
      scaleY: .9
    })
    .to(element, .3, {
      morphSVG: step2
    })
    .to(element, .3, {
      morphSVG: step3,
    }, "-=.15")
    .to(element, .3, {
      y: "0",
      scaleY: 1,
      onComplete: function(){
        open.classList.add("active");
      }
    }, "-=.15")

});

open.addEventListener("click", function(){
  this.classList.remove("active");

  tl
    .to(element, .3, {
      delay: .45,
      y: "10px",
    })
    .to(element, .3, {
      morphSVG: step2,
    })
    .to(element, .3, {
      morphSVG: step0
    }, "-=.15")
    .to(element, .3, {
      y: "0",
      onComplete: function(){
        wrapper.classList.remove("active");
      }
    }, "-=.3")
});
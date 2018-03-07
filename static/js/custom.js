"use strict";

// Instantiate the Bootstrap carousel
$('.multi-item-carousel').carousel({
  interval: false
});

// for every slide in carousel, copy the next slide's item in the slide.
// Do the same for the next, next item.
$('.multi-item-carousel .item').each(function(){
  var next = $(this).next();
  if (!next.length) {
    next = $(this).siblings(':first');
  }
  next.children(':first-child').clone().appendTo($(this));
  
  if (next.next().length>0) {
    next.next().children(':first-child').clone().appendTo($(this));
  } else {
    $(this).siblings(':first').children(':first-child').clone().appendTo($(this));
  }
});


// function showLoginResult(result) {
//   ("submit").click(function(){
//     $("#user-menu").toggle();
//   });
//   alert("logged in")
// }

// function submitLogin (evt) {
//   evt.preventDefault();

//   let formInputs = {
//     "email" : $("#email-field").val(),
//     "password" : $("#password-field").val(),
//   };

//   $.post( "/login", 
//       formInputs, 
//       showLoginResult
//       );
// }

// $("#login-form").on("submit", submitLogin);


 
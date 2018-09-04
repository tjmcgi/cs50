document.addEventListener('DOMContentLoaded', () => {

  
  if(!localStorage.getItem('username')) {
    var username = prompt("Please enter a username", "username");
  }

  localStorage.setItem('username', username);
  document.querySelector('#user-greeting').innerHTML = localStorage.getItem('username');

})
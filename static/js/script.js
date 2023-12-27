document.addEventListener('DOMContentLoaded', function () {
    let searchBtn = document.querySelector('#search-btn');
    let searchBar = document.querySelector('.search-bar-container');
    let menu = document.querySelector('#menu-bar');
    let navbar = document.querySelector('.navbar');

    let addBtn = document.querySelector('#add-btn');
    let addForm = document.querySelector('.ingredientAdd-container');
    let addClose = document.querySelector('#form-add-close');

    let dropBtn = document.querySelector('#drop-btn');
    let dropForm = document.querySelector('.ingredientDrop-container');
    let dropClose = document.querySelector('#form-drop-close');

    window.onscroll = () => {
        searchBtn.classList.remove('fa-times');
        searchBar.classList.remove('active');
        menu.classList.remove('fa-times');
        navbar.classList.remove('active');
    }


    menu.addEventListener('click', () => {
        menu.classList.toggle('fa-times');
        navbar.classList.toggle('active');
    });


    searchBtn.addEventListener('click', () => {
        searchBtn.classList.toggle('fa-times');
        searchBar.classList.toggle('active');
    });


    addBtn.addEventListener('click', () => {
        addForm.classList.add('active');
    });

    dropBtn.addEventListener('click', () => {
        dropForm.classList.add('active');
    });

    addClose.addEventListener('click', () => {
        addForm.classList.remove('active');
    });

    dropClose.addEventListener('click', () => {
        dropForm.classList.remove('active');
    });

    let decreaseBttns = document.querySelectorAll('.decrease-btn')
    decreaseBttns.forEach(button => {
        button.addEventListener('click', function (event) {
            event.preventDefault();
            let number = this.parentElement.querySelector('.number');
            let currentNum = parseInt(number.innerHTML);
            if (currentNum > 0) {
                number.innerHTML = currentNum - 1;
            }
        });
    });
});
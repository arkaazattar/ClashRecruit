const form = document.getElementById("required_league");
const print = document.getElementById("result")
form.addEventListener("submit", async function(event){
    event.preventDefault();
    const entered = document.getElementById("leagues");
    console.log(entered.value);
    
    print.textContent = entered.value;
    datatosend.requirements[0] = Number(entered.value);
    console.log(datatosend.requirements);
    
})

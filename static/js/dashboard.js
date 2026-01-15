// document.getElementById("result").innerText =
//       "able to recruit: " + result.recruit_status ;

const button = document.getElementById("recruit");
const button2 = document.getElementById("findClan");

button.addEventListener("click", () => {
    window.location.href ="/recruiter";
});


button2.addEventListener("click", () => {
    window.location.href ="/recruitee";
});
const form = document.getElementById("clanForm");
let after = null;
form.addEventListener("submit", async function (event) {
    event.preventDefault();
    const formData = new FormData(form);
    const filters = {};

    if(after) {
        filters.after = after;
    }

    for (const [key, value] of formData.entries()) {
        if (value !== "") {
            filters[key] = value;
        }
    }

    const response = await fetch("/search_clans", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(filters)
    });

    const data = await response.json();
    after = data.after
    console.log(data)
});
saveBtn = document.querySelector("#save-btn");
selectChecks = document.querySelectorAll(".form-check-input");

saveBtn.addEventListener('click', saveGarden);

function saveGarden() {
    selectedPlants = [];
    selectChecks.forEach(check => {
        if (check.checked) selectedPlants.push(check.id);
    });

    fetch("")

    console.log(selectedPlants);
    // Make a PUT call to edit the garden in the database.
    fetch('/planner', {
        method: 'PUT',
        body: JSON.stringify({
            selectedPlants: selectedPlants,
        }),
    })
        .then(response => response.json())
        .then(result => {
            console.log(result)
        })

    return false;
}
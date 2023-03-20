selectChecks = document.querySelectorAll(".form-check-input");

selectChecks.forEach(selectCheck => selectCheck.addEventListener('change', e => togglePlant(e)));

function togglePlant(e) {
    // Make a PUT call to edit the plant state in the database

    fetch('/toggle_plant', {
        method: 'PUT',
        body: JSON.stringify({
            id: e.target.id,
            newState: e.target.checked
        }),
    })
        .then(response => response.json())
        .then(result => {
            console.log(result)
        })

}
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

plantsData = document.querySelectorAll(".plants_data");
plantsData.forEach(activity => activity.addEventListener('click', e => editActivity(e)));

function editActivity(e) {
    classes = e.target.classList;
    let newActivity;

    if (classes.contains("N")) {
        classes.remove("N");
        newActivity = "S";
    } else if (classes.contains("S")) {
        classes.remove("S");
        newActivity = "Pi";
    } else if (classes.contains("Pi")) {
        classes.remove("Pi");
        newActivity = "Pr";
    } else if (classes.contains("Pr")) {
        classes.remove("Pr");
        newActivity = "R";
    } else if (classes.contains("R")) {
        classes.remove("R");
        newActivity = "P";
    } else if (classes.contains("P")) {
        classes.remove("P");
        newActivity = "N";
    }

    classes.add(newActivity);

    fetch('/edit_activity', {
        method: 'PUT',
        body: JSON.stringify({
            id: e.target.dataset.id,
            month: e.target.dataset.month,
            newActivity: newActivity,
        }),
    })
        .then(response => response.json())
        .then(result => {
            console.log(result)
        })


}
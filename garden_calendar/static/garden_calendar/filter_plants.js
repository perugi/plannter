plantFilter = document.querySelector('#plant-filter');
plantFilter.addEventListener('input', filterPlants);

function filterPlants() {
    plantRows = document.querySelectorAll('.plants_row');
    plantRows = Array.from(plantRows).slice(1);

    filterString = plantFilter.value.toLowerCase();

    plantRows.forEach(plantRow => {
        plant = plantRow.querySelector('.plants_name');

        if (plant.textContent.toLowerCase().includes(filterString)) {
            plantRow.hidden = false;
        } else {
            plantRow.hidden = true;
        }
    });

}

plantFilter = document.querySelector('#plant-filter');
plantFilter.addEventListener('input', filterPlants);

function filterPlants() {
    console.log('filter')
    plants = document.querySelectorAll('.plants_row');
    plants = Array.from(plants).slice(1);
    console.log(plants);

    filterString = plantFilter.value.toLowerCase();

    plants.forEach(plant => {
        if (plant.firstElementChild.textContent.toLowerCase().includes(filterString)) {
            plant.hidden = false;
        } else {
            plant.hidden = true;
        }
    });

}

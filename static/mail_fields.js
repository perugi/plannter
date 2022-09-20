function addMailField(id) {
    
    const MAX_MAILS = 5

    id = Number(id)

    if (id < MAX_MAILS + 1) {
        // Remove the -/+ button from the previous input field.
        document.getElementById("add_email").remove();
        // The first element does not have a - button.
        if (id != 2) {
            document.getElementById("remove_email").remove();
        }

        // Get the container which houses the mail fields, in order to append a new input field.
        var container = document.getElementById("mail_fields");
        
        // Create the elements needed for a new mail field.
        var input_group = document.createElement("div");
        input_group.setAttribute("class", "input-group mb-3");
        input_group.id = "mail_group_" + id;

        var input = document.createElement("input");
        input.autocomplete = "off";
        input.setAttribute("class", "form-control");
        input.id = "email_" + id;
        input.name = "email_" + id;
        input.placeholder = "name@example.com";
        input.type = "email";

        var remove_button = document.createElement("button")
        remove_button.setAttribute("class", "btn btn-outline-secondary");
        remove_button.setAttribute("onclick", "removeMailField(" + id + ")");
        remove_button.type = "button";
        remove_button.id = "remove_email";
        remove_button.textContent = "-";

        if (id < MAX_MAILS) {
            var add_button = document.createElement("button")
            add_button.setAttribute("class", "btn btn-outline-secondary");
            add_button.setAttribute("onclick", "addMailField(" + (id + 1) + ")");
            add_button.type = "button";
            add_button.id = "add_email";
            add_button.textContent = "+";
        }

        // Generate a new input field.
        input_group.appendChild(input);
        input_group.appendChild(remove_button);
        if (id < MAX_MAILS) {
            input_group.appendChild(add_button);
        }
        container.appendChild(input_group);

    }
}

function removeMailField(id) {
    // Remove the current mail field from the page.
    document.getElementById("mail_group_" + id).remove();

    // Get the previous mail field, in order to append the -/+ buttons.
    var previous_group = document.getElementById("mail_group_" + (id - 1));

    var remove_button = document.createElement("button")
    remove_button.setAttribute("class", "btn btn-outline-secondary");
    remove_button.setAttribute("onclick", "removeMailField(" + (id - 1) + ")");
    remove_button.type = "button";
    remove_button.id = "remove_email";
    remove_button.textContent = "-";

    var add_button = document.createElement("button")
    add_button.setAttribute("class", "btn btn-outline-secondary");
    add_button.setAttribute("onclick", "addMailField(" + id + ")");
    add_button.type = "button";
    add_button.id = "add_email";
    add_button.textContent = "+";

    // Append the -/+ buttons, except for the first field, where there is no - button.
    if (id != 2) {
        previous_group.appendChild(remove_button);
    }
    previous_group.appendChild(add_button);
}
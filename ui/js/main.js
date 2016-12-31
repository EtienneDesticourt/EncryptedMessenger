function register() {
    accountName = document.getElementById('account-name').value;
    result = wrapper.register(accountName);
    if (result == "OK") {
        wrapper.load_index();
    }
    else {
        errorMessage = document.getElementById('error');
        errorMessage.innerText = result;
        errorMessage.style.visibility='visible';
    }
}

function fill_contact_list() {
    list = document.getElementById("contact-list");
    numContacts = wrapper.get_num_contacts();

    for(i = 0; i < numContacts; i++) {
        name = wrapper.get_contact_name(i);
        var listElement = document.createElement("li");
        var contactLink = document.createElement("a");

        var icon = document.createElement("img");
        icon.className = "icon";
        icon.src = "images/icon_small.png";

        var contactName = document.createElement("div");
        contactName.className = "text";
        var nameNode = document.createTextNode(name);
        contactName.appendChild(nameNode);

        contactLink.appendChild(icon);
        contactLink.appendChild(contactName);

        listElement.appendChild(contactLink);

        list.appendChild(listElement);
    }
}

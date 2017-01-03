function showError(message) {
    errorMessage = document.getElementById('error');
    errorMessage.innerText = message;
    errorMessage.style.visibility='visible';
}

function addFriend() {
    accountName = document.getElementById('account-name').value;
    result = wrapper.add_friend(accountName);
    if (result == "OK") {
        wrapper.load_index();
    }
    else {
        showError(result);
    }
}

function register() {
    accountName = document.getElementById('account-name').value;
    result = wrapper.register(accountName);
    if (result == "OK") {
        wrapper.load_index();
    }
    else {
        showError(result);
    }
}

function createContactElement(name) {
    var listElement = document.createElement("li");
    var contactLink = document.createElement("a");

    var icon = document.createElement("img");
    icon.className = "icon";
    icon.src = "../images/icon_small.png";

    var contactName = document.createElement("div");
    contactName.className = "text";
    var nameNode = document.createTextNode(name);
    contactName.appendChild(nameNode);

    contactLink.appendChild(icon);
    contactLink.appendChild(contactName);

    listElement.appendChild(contactLink);
    return listElement;
}

function fillContactList() {
    list = document.getElementById("contact-list");

    // Loop through friends and add one li for each
    numContacts = wrapper.get_num_contacts();
    for(i = 0; i < numContacts; i++) {
        name = wrapper.get_contact_name(i);
        var listElement = createContactElement(name);
        list.appendChild(listElement);
    }
}

/*
 *  CONTACT LIST
 */

 function createContactElement(name) {
    var listElement = document.createElement("li");
    var contactLink = document.createElement("a");
    contactLink.onclick = function () { activateContact(listElement, name); };

    var icon = document.createElement("img");
    icon.id = "contact-icon-".concat(name)
    icon.className = "icon";
    if (wrapper.is_online(name)) {
        icon.src = "../images/icon_small.png";
    }
    else {
        icon.src = "../images/icon_small_offline.png";
    }

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
    list.innerHtml = "";

    // Loop through friends and add one li for each
    numContacts = wrapper.get_num_contacts();
    for(i = 0; i < numContacts; i++) {
        name = wrapper.get_contact_name(i);
        var listElement = createContactElement(name);
        list.appendChild(listElement);
    }
}

function updateStatus() {
    numContacts = wrapper.get_num_contacts();
    for(i = 0; i < numContacts; i++) {
        name = wrapper.get_contact_name(i);
        online = wrapper.is_online(name);
        setStatus(name, online);
    }
}

function setStatus(name, online) {
    icon = document.getElementById("contact-icon-".concat(name));
    online_src = "../images/icon_small.png";
    offline_src = "../images/icon_small_offline.png"
    if (online) {
        if (icon.src.indexOf("offline") !== -1) {
            icon.src = online_src;
            wrapper.display_online_notification();
        }
    }
    else {
        if (icon.src.indexOf("offline") == -1) {
            icon.src = offline_src;
            wrapper.display_offline_notification();
            desactivateContact(name);
        }
    }
}

function activateContact(contactElement, name) {
    online = wrapper.is_online(name);
    if (!online) {
        return;
    }

    desactivateContact("");
    contactElement.className = "active";

    document.getElementById("entry-section").style.visibility = "visible";
    wrapper.activate_contact(name);
}

function desactivateContact(name) {
    list = document.getElementById("contact-list");
    var children = list.children;
    for (var i = 0; i < children.length; i++) {
      var child = children[i];
      if (child.className == "active") {
        child.className = "";
      }
    }

    active_name = wrapper.get_active_contact_name();
    if (active_name == name) {
        document.getElementById("entry-section").style.visibility = "hidden";
    }
}

setInterval(updateStatus, 5000);

/*
 * OTHER
 */

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

/*
 * REGISTER
 */

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

/*
 * MESSAGES
 */

function postMessage() {
    input = document.getElementById("message-input");
    message = input.value;
    wrapper.post_message(message);
    input.value = "";
    name = wrapper.get_username();
    var today = new Date();
    date = today.toISOString();
    addMessage(name, date, message);
}

function handleInputKeypress(event) {
    if (event.keyCode == 13) {
        postMessage();
    }
}

function createMessageElement(name, date, content) {
    var divElement = document.createElement("div");
    divElement.className = "message";

    var titleElement = document.createElement("h3");
    titleElement.className = "contact-name";
    var titleNode = document.createTextNode(name);
    titleElement.appendChild(titleNode);


    var dateElement = document.createElement("p");
    dateElement.className = "message-date";
    var dateNode = document.createTextNode(date);
    dateElement.appendChild(dateNode);

    var contentElement = document.createElement("p");
    contentElement.className = "message-content";
    var contentNode = document.createTextNode(content);
    contentElement.appendChild(contentNode);


    divElement.appendChild(titleElement);
    divElement.appendChild(dateElement);
    divElement.appendChild(contentElement);
    return divElement;
}

function addMessage(name, date, content) {
    list = document.getElementById("message-list");
    messageElement = createMessageElement(name, date, content);
    list.appendChild(messageElement);
    list.scrollTop = list.scrollHeight;
}

function addNewMessages() {
    var numMessages = wrapper.get_active_contact_num_messages();
    for(i = 0; i < numMessages; i++) {
        message = wrapper.get_active_contact_latest_message();
        name = wrapper.get_active_contact_name();
        var today = new Date();
        date = today.toISOString().substring(0, 10);
        addMessage(name, date, message);
    }
}

function addNotConnectedMessage() {
    var today = new Date();
    date = today.toISOString().substring(0, 10);
    addMessage("NOT CONNECTED", date, "----------------------------------------------");
}


function updateMessages() {
    addNewMessages();
}

setInterval(updateMessages, 1000);

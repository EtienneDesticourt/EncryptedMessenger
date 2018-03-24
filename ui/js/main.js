/*
 * TITLE BAR
 */

window.channel = new QWebChannel(qt.webChannelTransport, function (channel) {

    channel.objects.wrapper.user_connected.connect(onUserConnected);
    channel.objects.wrapper.contact_loaded.connect(onContactLoaded);
    channel.objects.wrapper.contact_added.connect(onContactAdded);
    channel.objects.wrapper.contact_connected.connect(onContactConnected);
    channel.objects.wrapper.contact_disconnected.connect(onContactDisconnected);
    channel.objects.wrapper.connected_to_contact.connect(OnConnectedToContact);
    channel.objects.wrapper.message_received.connect(onMessageReceived); 

    channel.objects.settings.settings_loaded.connect(onSettingsLoaded);
    channel.objects.settings.settings_saved.connect(onSettingsSaved);

    // Let the application know we're all ready to listen
    channel.objects.wrapper.on_callbacks_defined();
});

function closeWindow() {
    channel.objects.title_bar.custom_close();
}

function minimizeWindow() {
    channel.objects.title_bar.minimize();
}

function maximizeWindow() {
    channel.objects.title_bar.maximize();
}

/*
 *     USER INFO
 */

 function onUserConnected(username) {
    usernameElement = document.getElementById("username");
    usernameElement.innerHTML = username;
 }

/*
 *  CONTACT LIST
 */

// NEW CONTACT
function addContact() {
    accountName = document.getElementById('account-name').value;
    channel.objects.wrapper.add_friend(accountName);
}

function onContactAdded() {
    channel.objects.wrapper.load_index();
}

// CONTACT LOADED
function findActiveContactElement() {
    list = document.getElementById("contact-list");
    var children = list.children;
    for (var i = 0; i < children.length; i++) {
        var child = children[i];
        if (child.className == "active") {
            return child;
        }
    }
}

function findContactElementByName(name) {
    list = document.getElementById("contact-list");
    var children = list.children;
    for (var i = 0; i < children.length; i++) {
        var child = children[i];
        contactLink = child.childNodes[0];
        currentName = contactLink.childNodes[1].innerText;
        if (currentName == name) {
            return child;
        }
    }
}

function desactivateContact() {
    activeContactElement = findActiveContactElement();
    if (activeContactElement != null) {
            activeContactElement.className = "";
    }    
    list = document.getElementById("message-list");
    list.innerHTML = "";
    document.getElementById("entry-section").style.visibility = "hidden";
}

function activateContact(contactElement, name) {
    if (contactElement.className == "active") {
        return;
    }
    desactivateContact();
    contactElement.className = "active";
    document.getElementById("entry-section").style.visibility = "visible";
}

function createContactElement(name) {
    var listElement = document.createElement("li");
    var contactLink = document.createElement("a");
    contactLink.id = "contact-link";
    contactLink.onclick = function () { activateContact(listElement, name); };

    var icon = document.createElement("div");
    icon.id = "contact-icon-".concat(name)
    icon.className = "contact-offline-icon";
    channel.objects.wrapper.debug_print(icon.className);


    var contactName = document.createElement("div");
    contactName.className = "text";
    contactName.id = "contact-name";
    var nameNode = document.createTextNode(name);
    contactName.appendChild(nameNode);

    contactLink.appendChild(icon);
    contactLink.appendChild(contactName);

    listElement.appendChild(contactLink);
    return listElement;
}

function onContactLoaded(name) {    
    var list = document.getElementById("contact-list");
    var listElement = createContactElement(name);
    list.appendChild(listElement);
}

// MESSAGING SESSION


// CONTACT CONNECTION STATUS CHANGE
function onContactConnected(name) {
    icon = document.getElementById("contact-icon-".concat(name));
    icon.className = "contact-online-icon";
}

function onContactDisconnected(name) {
    icon = document.getElementById("contact-icon-".concat(name));    
    icon.className = "contact-offline-icon";
}

function OnConnectedToContact(name) {
    onContactConnected(name);
}

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
    result = channel.objects.wrapper.add_friend(accountName);
    if (result == "OK") {
        channel.objects.wrapper.load_index();
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

function onMessageReceived(name, message) {
    activeContact = findActiveContactElement();
    if (activeContact != null) {
        contactLink = activeContact.childNodes[0];
        activeName = contactLink.childNodes[1].innerText;
        if (activeName == name) {
            onMessageAdded(name, message);
        }
        else {
            messagingContact = findContactElementByName(name);
            contactLink = messagingContact.childNodes[0];
            contactLink.childNodes[1].style.backgroundColor = "yellow"; 
        }
    }
    // activeContact.childNodes[1].text; 
    // icon = document.getElementById("contact-icon-".concat(name));
    // icon.className = "contact-online-icon";

}

function onMessageAdded(name, message) {
    var today = new Date();
    date = today.toISOString().substring(0, 10);
    addMessageElement(name, date, message);
}

function onMessageSent() {

}


function addMessageElement(name, date, content) {
    list = document.getElementById("message-list");
    messageElement = createMessageElement(name, date, content);
    list.appendChild(messageElement);
    list.scrollTop = list.scrollHeight;
}

function sendMessage() {
    // Get message field contents
    input = document.getElementById("message-input");
    message = input.value;
    input.value = "";

    // Get username from username label
    usernameElement = document.getElementById("username");
    name = usernameElement.innerHTML;

    // Add message with current date
    var today = new Date();
    date = today.toISOString();
    addMessageElement(name, date, message);

    // Pass message to wrapper

}

// NEW CONTACT IFRAME
// -> ON LOAD FINISHED
// -> CALL EMITTER 
// -> EMIT message added for each message

// OR
// LOAD FROM FILE
// ADD NEW SESSION MESSAGES




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
        sendMessage();
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


function addNewMessages() {
    var numMessages = channel.objects.wrapper.get_active_contact_num_messages();
    for(i = 0; i < numMessages; i++) {
        message = channel.objects.wrapper.get_active_contact_latest_message();
        name = channel.objects.wrapper.get_active_contact_name();
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


/*
 *       SETTINGS
 */


 function onSettingsLoaded(runAsClient, peerUrl, port) {    
    runAsClientCheckbox = document.getElementById("client-only");
    runAsClientCheckbox.checked = runAsClient;

    peerUrlField = document.getElementById("peer-registry");
    peerUrlField.value = peerUrl;
    
    portField = document.getElementById("connection-port");
    portField.value = port;

    usernameElement = document.getElementById("username");
    usernameCombo = document.getElementById("username-select");
    var option = document.createElement('option');
    option.text = option.value = usernameElement.innerHTML;
    usernameCombo.add(option, 0);
 }

 function onSettingsSaved() {
    savedMessage = document.getElementById("saved-callback");
    var clonedMessage = savedMessage.cloneNode(true);
    savedMessage.parentNode.replaceChild(clonedMessage, savedMessage);    
    clonedMessage.style.visibility = "visible";
 }

 function saveSettings() {
    runAsClientCheckbox = document.getElementById("client-only");
    checked = runAsClientCheckbox.checked;

    peerUrlField = document.getElementById("peer-registry");
    peerUrl = peerUrlField.value;

    portField = document.getElementById("connection-port");
    port = portField.value;

    channel.objects.settings.save_settings(checked, peerUrl, port);
 }

/*
 *       SIMULATED EVENTS
 */

    // channel.objects.wrapper.user_connected.connect(onUserConnected);
    // channel.objects.wrapper.contact_loaded.connect(onContactLoaded);
    // channel.objects.wrapper.contact_added.connect(onContactAdded);
    // channel.objects.wrapper.contact_connected.connect(onContactConnected);
    // channel.objects.wrapper.contact_disconnected.connect(onContactDisconnected);

function simulateContactConnected() {
    onContactConnected("hello");
}

function simulateContactDisconnected() {
    onContactDisconnected("hello");
}

function simulateMessageReceived() {
    channel.objects.wrapper.contact_connected.emit("hello");
}

function simulateMessageAdded() {
    onMessageAdded("username", "This is my message.");
}

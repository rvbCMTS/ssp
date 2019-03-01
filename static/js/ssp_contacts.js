$(document).ready(function() {
    $.get($('#idContactsUrl').html(), function( data ) {
        let contacts = '';

        for (let ind in data.ContactInformation){
            let contact = data.ContactInformation[ind];
            contacts = contacts +
                '<dt>' + contact.Name  + '</dt><dd><a class="text-white" href="mailto:' +
                contact.Email + '">' + contact.Email + '</a></dd>';
        }

        $('#idContacts').html(contacts);
    });
});
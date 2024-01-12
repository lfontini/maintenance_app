// Select all buttons with the id 'button_test'



// this routine below get core id and send to backend to check in database and perform a close ticket 

const buttons_cancel = document.querySelectorAll('#button_cancel');
console.log("incluiu cancel js ")


const Cancel_zendesk_ticket = async (id) => {
    const url = '/cancel_tickets_zendesk/';
    const data = new FormData();
    var resposta = window.confirm("Are you sure that you want to cancel the zendesk tickets?");
    if (resposta) {
        data.append('id', id);
        $('#spinner').addClass('show');

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                body: data
            });

            if (response.ok) {
                const responseData = await response.json();
                alert(responseData['success'])
                $('#spinner').removeClass('show');

            }


            else {
                alert("An Error has occurred during the fetch data");
                $('#spinner').removeClass('show');

            }

        } catch (error) {

        }
    } else {
        alert("Operation cancelled ");
    }


}


buttons_cancel.forEach(button => {
    // Add a click event listener to each button
    button.addEventListener('click', () => {
        const id = button.value;
        Cancel_zendesk_ticket(id)

    });
});


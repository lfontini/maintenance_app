// when Dom is loaded some function are performed 

document.addEventListener('DOMContentLoaded', function () {


    // get the element to hide it 
    const ignEngineerlabelField_id = document.querySelector('label[for="id_ign_engineer"]');
    const ignEngineerField = document.getElementById('id_ign_engineer');

    const id_internet_id = document.getElementById('id_internet_id');
    const id_internet_id_label = document.querySelector('label[for="id_internet_id"]');

    const id_network_link = document.getElementById('id_network_link');
    const id_network_link_label = document.querySelector('label[for="id_network_link"]');

    const id_pop = document.getElementById('id_pop');
    const id_pop_label = document.querySelector('label[for="id_pop"]');

    // Add attribute  "hidden" 
    ignEngineerField.setAttribute('hidden', 'true', 'disable', 'true');
    ignEngineerlabelField_id.setAttribute('hidden', 'true', 'disable', 'true');

    id_internet_id_label.setAttribute('hidden', 'true');
    id_internet_id.setAttribute('hidden', 'true');

    id_network_link.setAttribute('hidden', 'true');
    id_network_link_label.setAttribute('hidden', 'true');

    id_pop.setAttribute('hidden', 'true');
    id_pop_label.setAttribute('hidden', 'true');


});

const activity_type_field = document.getElementById('id_activity_type');
const ign_engineer_field = document.getElementById('id_ign_engineer');
const ignEngineerlabelField_id = document.querySelector('label[for="id_ign_engineer"]');
const id_activity_related_to_field = document.getElementById('id_activity_related_to');
const id_internet_id = document.getElementById('id_internet_id');
const id_internet_id_label = document.querySelector('label[for="id_internet_id"]');

const id_network_link = document.getElementById('id_network_link');
const id_network_link_label = document.querySelector('label[for="id_network_link"]');

const id_pop = document.getElementById('id_pop');
const id_pop_label = document.querySelector('label[for="id_pop"]');

function show_field(fields) {
    for (const element of fields) {
        element.removeAttribute("hidden");
    }
}

function hide_field(fields) {
    for (const element of fields) {
        element.setAttribute("hidden", "true");
    }
}


activity_type_field.addEventListener('change', function (event) {
    if (activity_type_field.value === "from_ign") {
        show_field([ign_engineer_field, ignEngineerlabelField_id]);

    } else {
        hide_field([ign_engineer_field, ignEngineerlabelField_id]);
    }
});

id_activity_related_to_field.addEventListener('change', function (event) {
    if (id_activity_related_to_field.value === "internet_service") {
        show_field([id_internet_id_label, id_internet_id]);
        hide_field([id_network_link_label, id_network_link])
    } else if (id_activity_related_to_field.value === "network_link") {
        show_field([id_network_link, id_network_link_label]);
        hide_field([id_internet_id_label, id_internet_id, id_pop, id_pop_label])
    } else if (id_activity_related_to_field.value === "pop") {
        show_field([id_pop, id_pop_label]);
        hide_field([id_network_link, id_network_link_label, id_internet_id_label, id_internet_id])
    } else if (id_activity_related_to_field.value === "pop") {
        hide_field([id_network_link, id_network_link_label, id_internet_id_label, id_internet_id, id_pop, id_pop_label])
    }
});





const pop = document.getElementById('id_pop');
pop.addEventListener('change', function (event) {
    // this pop value get id of the pop 
    const popValue = document.getElementById('id_pop').value;

    // this var get pop name and it will get the devices inside this pop 
    var poptext = pop.options[pop.selectedIndex].text;

    console.log(poptext);

    // create a from data 
    const formData = new FormData();
    formData.append('data', poptext);

    // Opções da solicitação, incluindo o método POST, cabeçalhos e corpo da solicitação
    const requestOptions = {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken // Adicione o token CSRF ao cabeçalho
        },
        body: formData // Use o objeto FormData como corpo da solicitação
    };

    // Fazendo a solicitação POST usando fetch
    fetch('/get_device_list_pop/', requestOptions)
        .then(response => {
            // Verifica se a resposta da solicitação foi bem-sucedida (código de status 2xx)
            if (response.ok) {
                return response.json();
            } else {
                // Caso contrário, rejeita a promessa com uma mensagem de erro
                throw new Error('Erro na solicitação da API');
            }
        })
        .then(data => {
            const checkboxContainer = document.getElementById('checkboxContainer');
            checkboxContainer.innerHTML = ''; // Limpa o conteúdo anterior

            data.services.forEach(device => {
                // Crie um <div> para cada checkbox e rótulo
                const checkboxDiv = document.createElement('div');
                checkboxDiv.style.marginBottom = '10px';

                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.setAttribute('class', 'form-check-input');
                checkbox.id = `${device}`;
                checkbox.name = device;
                checkbox.value = device;
                checkbox.checked = device.selected;

                const label = document.createElement('label');
                label.setAttribute('class', 'form-check-label');
                label.textContent = device;
                label.setAttribute('for', `${device}`);

                checkboxDiv.appendChild(checkbox);
                checkboxDiv.appendChild(label);

                checkboxContainer.appendChild(checkboxDiv);
            });

            // Abra o modal
            $('#optionsModal').modal('show');
        })
        .catch(error => {
            // Lida com erros, como falha na rede, erro na API ou erro de análise JSON
            console.error('Erro:', error);
        });
});



const id_affected_services = document.getElementById('id_affected_services');
const checkboxContainer = document.getElementById("checkboxContainer");
checkboxContainer.addEventListener('change', function (event) {
    // this event target get the checkbox clicked and send this data to backend and receive the services affected who will be 
    //fullfilled into textbox services affected 
    const clickedCheckbox = event.target;
    const isChecked = clickedCheckbox.checked;
    const id = clickedCheckbox.id;
    const formData = new FormData();
    formData.append('data', id);

    if (isChecked) {

        const requestOptions = {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken // Adicione o token CSRF ao cabeçalho
            },
            body: formData // Use o objeto FormData como corpo da solicitação

        };

        fetch('/get_service_list/', requestOptions)
            .then(response => {
                // Verifica se a resposta da solicitação foi bem-sucedida (código de status 2xx)
                if (response.ok) {
                    return response.json();
                } else {
                    // Caso contrário, rejeita a promessa com uma mensagem de erro
                    throw new Error('Erro na solicitação da API');
                }
            })
            .then(data => {
                const results = data.services.replace(/[\[\],'']/g, " ");
                console.log(results)
                id_affected_services.value += ` ${results}`;


            });


        console.log(id);
    } else {
        console.log(`O checkbox com id '${id}' foi desmarcado.`);
    }

});


$(document).ready(function () {
    // Exibe o alerta
    $(".dialog-box").fadeIn();

    // Define um temporizador para ocultar o alerta após 3 segundos (3000 milissegundos)
    setTimeout(function () {
        $(".dialog-box").fadeOut();
    }, 3000);
});




//// this routine will get the network link name and perform a fetch to get all paths and services 
const id_network_link_field = document.getElementById('id_network_link');
id_network_link_field.addEventListener('change', function (event) {

    const id_network_link = document.getElementById('id_network_link').value;
    console.log(id_network_link);

    // Crie um objeto FormData para enviar os dados
    const formData = new FormData();
    formData.append('data', id_network_link);

    // Opções da solicitação, incluindo o método POST, cabeçalhos e corpo da solicitação
    const requestOptions = {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken // Adicione o token CSRF ao cabeçalho
        },
        body: formData // Use o objeto FormData como corpo da solicitação
    };

    // Fazendo a solicitação POST usando fetch
    fetch('/get_device_list_paths/', requestOptions)
        .then(response => {
            // Verifica se a resposta da solicitação foi bem-sucedida (código de status 2xx)
            if (response.ok) {
                return response.json();
            } else {
                // Caso contrário, rejeita a promessa com uma mensagem de erro
                throw new Error('Erro na solicitação da API');
            }
        })
        .then(data => {
            const checkboxContainer = document.getElementById('checkboxContainer');
            checkboxContainer.innerHTML = ''; // Limpa o conteúdo anterior

            data.services.forEach(path => {
                // Crie um <div> para cada checkbox e rótulo
                const checkboxDiv = document.createElement('div');
                checkboxDiv.style.marginBottom = '10px';

                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.setAttribute('class', 'form-check-input');
                checkbox.id = `${path}`;
                checkbox.name = path;
                checkbox.value = path;
                checkbox.checked = path.selected;

                const label = document.createElement('label');
                label.setAttribute('class', 'form-check-label');
                label.textContent = path;
                label.setAttribute('for', `${path}`);

                checkboxDiv.appendChild(checkbox);
                checkboxDiv.appendChild(label);

                checkboxContainer.appendChild(checkboxDiv);
            });

            // Abra o modal
            $('#optionsModal').modal('show');
        })
        .catch(error => {
            // Lida com erros, como falha na rede, erro na API ou erro de análise JSON
            console.error('Erro:', error);
        });
});


/// rotina dia 

id_internet_id_field = document.getElementById("id_internet_id");

id_internet_id_field.addEventListener('change', function (event) {
    DIA_ID = id_internet_id_field.value;
    var dia_text = id_internet_id_field[id_internet_id_field.selectedIndex].text

    console.log(dia_text)
    const formData = new FormData();
    formData.append('data', dia_text);

    const requestOptions = {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        body: formData
    };

    fetch('/get_device_list_pop/', requestOptions)
        .then(response => {
            // Verifica se a resposta da solicitação foi bem-sucedida (código de status 2xx)
            if (response.ok) {
                return response.json();
            } else {
                // Caso contrário, rejeita a promessa com uma mensagem de erro
                throw new Error('Erro na solicitação da API');
            }
        })
        .then(data => {
            const checkboxContainer = document.getElementById('checkboxContainer');
            checkboxContainer.innerHTML = ''; // Limpa o conteúdo anterior

            data.services.forEach(device => {
                // Crie um <div> para cada checkbox e rótulo
                const checkboxDiv = document.createElement('div');
                checkboxDiv.style.marginBottom = '10px';

                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.setAttribute('class', 'form-check-input');
                checkbox.id = `${device}`;
                checkbox.name = device;
                checkbox.value = device;
                checkbox.checked = device.selected;

                const label = document.createElement('label');
                label.setAttribute('class', 'form-check-label');
                label.textContent = device;
                label.setAttribute('for', `${device}`);

                checkboxDiv.appendChild(checkbox);
                checkboxDiv.appendChild(label);

                checkboxContainer.appendChild(checkboxDiv);
            });

            // Abra o modal
            $('#optionsModal').modal('show');
        });


});




// calcula hora 

const end_date_field = document.getElementById("id_end_date");
end_date_field.addEventListener('change', function (event) {
    const start_date = new Date(document.getElementById("id_start_date").value);
    const end_date = new Date(document.getElementById("id_end_date").value);
    const durationField = document.getElementById("id_duration");

    const millisecondOutcome = end_date - start_date;
    const seconds = millisecondOutcome / 1000;

    function segundosParaHora(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);

        if (hours < 0 || minutes < 0) {
            alert("Invalid duration, it cannot be negative number");
            durationField.value = "00:00";
            return "00:00";
        }

        const formattedHours = hours < 10 ? `0${hours}` : hours;
        const formattedMinutes = minutes < 10 ? `0${minutes}` : minutes;

        return `${formattedHours}:${formattedMinutes}`;
    }

    const Formated_duration = segundosParaHora(seconds);

    console.log(`Duration in sec : ${seconds}`);
    console.log(`Duration in  date form : ${Formated_duration}`);
    durationField.value = Formated_duration;
});


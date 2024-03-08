// clear the localstoragem when the page is refresed



document.addEventListener('DOMContentLoaded', function () {
    localStorage.clear();
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

const headers = {
    'QB-Realm-Hostname': 'ignetworks.quickbase.com',
    'Authorization': 'QB-USER-TOKEN b2hjmh_w4i_b2ytd7mdi8jjrpdg8khp8cmwkm6n',
    'Content-Type': 'application/json'
};



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
            if (response.ok) {
                return response.json();
            } else {
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


var services = "";
const checkboxContainer = document.getElementById("checkboxContainer");
const load_services = document.getElementById("load_services");

load_services.addEventListener('click', async function (event) {
    var selectedServices = [];
    var checkboxes = checkboxContainer.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(function (checkbox) {
        if (checkbox.checked) {
            selectedServices.push(checkbox.id);
        }
    });

    const fetchPromises = [];

    selectedServices.forEach(function (serviceId) {
        const formData = new FormData();
        formData.append('data', serviceId);
        const requestOptions = {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            body: formData
        };

        const fetchPromise = fetch('/get_service_list/', requestOptions)
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    alert("error to get services from gogs , NOTE: services are selected from devices`s backup in gogs")
                    throw new Error('Erro na solicitação da API');
                }
            })
            .then(data => {
                services += data.services;
            })
            .catch(error => {
                console.error('Erro durante a requisição:', error);
            });

        fetchPromises.push(fetchPromise);
    });

    // Aguarda todas as promessas fetch serem resolvidas
    await Promise.all(fetchPromises);

    // Após todas as requisições serem concluídas, execute a função getServicesInfo com os serviços acumulados
    console.log(services);
    getServicesInfo(services);
    $('#optionsModal').modal('hide');
});



$(document).ready(function () {
    // Exibe o alerta
    $(".dialog-box").fadeIn();

    // Define um temporizador para ocultar o alerta após 3 segundos (3000 milissegundos)
    setTimeout(function () {
        $(".dialog-box").fadeOut();
    }, 10000);
});




//// this routine will get the network link name and perform a fetch to get all paths and services 
const id_network_link_field = document.getElementById('id_network_link');
id_network_link_field.addEventListener('change', function (event) {

    const id_network_link = document.getElementById('id_network_link')

    var selectedIndex = id_network_link.selectedIndex;

    var selectedText = id_network_link.options[selectedIndex].text;

    const formData = new FormData();
    formData.append('data', selectedText);

    // Opções da solicitação, incluindo o método POST, cabeçalhos e corpo da solicitação
    const requestOptions = {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken // Adicione o token CSRF ao cabeçalho
        },
        body: formData // Use o objeto FormData como corpo da solicitação
    };

    // list all path from a network link 
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
            alert.error('An error to get the service from gogs error code', error);
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
                alert.error('An error to get the service from gogs error code', error);
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


const div_feedback = document.getElementById("feedback_create_core");

async function CreateCore(event) {
    event.preventDefault();

    // gerar core com o form = receber core id + criar zabbix maintenance receber o id do zabbix /create core 
    // pegar prefixos e enviar junto com a core id /create_ticket receber o ticket id 
    // + criar calendario com circuitos afetados

    async function sendPostRequest(data, url) {
        try {
            const response = await axios.post(url, data, {
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json' // Definindo o tipo de conteúdo como JSON
                }
            });
            return response.data
        } catch (error) {
            console.error(error)
            return error
        }
    }


    // obs this form has to match with forms.py in backend for a goog match  use the same key in forms and here  below for a better form.valid() method :)
    const form_core = {
        "activity_type": document.getElementById("id_activity_type").value,
        "activity_related_to": document.getElementById("id_activity_related_to").value,
        "ign_engineer": document.getElementById("id_ign_engineer").value,
        "network_link": document.getElementById("id_network_link").value,
        "internet_id": document.getElementById("id_internet_id").value,
        "pop": document.getElementById("id_pop").value,
        "status": document.getElementById("id_status").value,
        "duration": document.getElementById("id_duration").value,
        "downtime": document.getElementById("id_downtime").value,
        "start_date": document.getElementById("id_start_date").value,
        "end_date": document.getElementById("id_end_date").value,
        "Description": document.getElementById("id_Description").value,
        "Description_to_customers": document.getElementById("id_Description_to_customers").value,
        "location": document.getElementById("id_location").value,
        "remote_hands_information": document.getElementById("id_remote_hands_information").value,
    };


    // this part exclude all services Cancelled
    for (const key in serviceGroups) {
        const services = serviceGroups[key].attributes;

        for (const serviceKey in services) {
            const service = services[serviceKey];
            if (service.status === "Cancelled") {
                // Remover serviço cancelado
                delete serviceGroups[key].attributes[serviceKey];
            }
        }
    }

    // essa parte trata de diversidade dos circuitos que se tiverem nao podem estar na mesma janela 
    const diverseServicesMap = {};

    for (const key in serviceGroups) {
        const services = serviceGroups[key].attributes;

        for (const serviceKey in services) {
            const service = services[serviceKey];

            // Check if the service has diversity
            if (service.diversidade.toLowerCase() === "yes") {
                const relatedService = service.servicoDiversoRelacionado;

                // If the related diverse service appears as a key in the map, generate an alert
                if (diverseServicesMap[relatedService]) {
                    const serviceInfo = `Service: ${serviceKey}, Related Diverse Service: ${relatedService}`;
                    alert("Duplicate related diverse services found: " + serviceInfo);
                }

                // Add the service as key and its related diverse service as value to the map
                diverseServicesMap[serviceKey] = relatedService;
            }
        }
    }


    var tickets = []
    var affected_services = []
    const my_div = document.createElement("div");
    my_div.textContent = `Generating core ...`;
    div_feedback.appendChild(my_div);
    div_feedback.style.display = "block";
    const result_core = await sendPostRequest(form_core, '/create_core/');
    console.log("result_core", result_core)
    if ('core_id' in result_core || 'id' in result_core) {
        const core_id = result_core.core_id
        const id = result_core.id
        my_div.textContent = `Generated core ${core_id};`

        console.log(serviceGroups)
        for (var groupName in serviceGroups) {
            if (Object.keys(serviceGroups[groupName].attributes).length !== 0) {
                const my_div = document.createElement("div");
                my_div.textContent = `Inserting into core services ${groupName}... and generating tickets`;
                const data = { 'services': serviceGroups[groupName], 'core_id': core_id }
                await sendPostRequest(data, '/insert_services/');
                div_feedback.appendChild(my_div);
                let data_ticket = { 'form_core': form_core, 'services': serviceGroups[groupName], 'core_id': core_id, 'id': id, 'prefix': groupName }
                result = await sendPostRequest(data_ticket, '/create_tickets/');
                console.log('result', result)
                my_div.textContent = result.result
                tickets.push(result.ticket_id)
                console.log("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", serviceGroups[groupName].ids)
                var service_temp = serviceGroups[groupName].ids
                // prepare the services to backend
                if (service_temp) {
                    service_temp.forEach(element => {
                        affected_services.push(element);
                    });
                }

            }
        }

        console.log("services afetesss", affected_services)
        console.log("services afetesss", typeof (affected_services))


        if (tickets) {
            const my_div = document.createElement("div");
            my_div.textContent = `Sending email to noc ... `;
            let data_ticket = { 'core_id': core_id, 'tickets': tickets, 'start_date': form_core['start_date'] }
            console.log("enviando dados para criar email ", data_ticket)
            result = await sendPostRequest(data_ticket, '/send_email/');
            console.log('result', result)
            my_div.textContent = result.result
            div_feedback.appendChild(my_div);

        }
        if (core_id) {
            if (serviceGroups) {
                const my_div = document.createElement("div");
                my_div.textContent = `Creating event in google calendar ... `;

                let data_ticket = { 'core_id': core_id, 'start_date': form_core['start_date'], 'end_date': form_core['end_date'], 'affected_services': affected_services }
                result = await sendPostRequest(data_ticket, '/create_event_calendar/');
                console.log('result', result)
                my_div.textContent = result.result
                div_feedback.appendChild(my_div);
            }
            else {
                const my_div = document.createElement("div");
                my_div.textContent = `Creating event in google calendar ... `;
                let data_ticket = { 'core_id': core_id, 'start_date': form_core['start_date'], 'end_date': form_core['end_date'], 'affected_services': null }
                result = await sendPostRequest(data_ticket, '/create_event_calendar/');
                console.log('result', result)
                my_div.textContent = result.result
                div_feedback.appendChild(my_div);
            }
        }

        if (tickets) {
            const my_div = document.createElement("div");
            my_div.textContent = `Creating zabbix Maintenance  ... `;
            let data_ticket = { 'id': id, 'core_id': core_id, 'tickets': tickets, 'end_date': form_core['end_date'], 'start_date': form_core['start_date'], 'services': affected_services }
            result = await sendPostRequest(data_ticket, '/create_zabbix_maintenance/');
            console.log('result', result)
            my_div.textContent = result.result
            div_feedback.appendChild(my_div);
        }




    } else {
        alert(`Error to generate core id  ${result_core.response.data.result[1]}`)
    }
}





const button_create_core = document.getElementById("btn-create_core");
button_create_core.addEventListener('click', function (event) {
    CreateCore(event);
});

function IdentifyServicesNni(service_list) {
    let raw_data = service_list.join(' ');
    if (!raw_data) {
        return []; // return null 
    }
    let regex_nni = /[A-Z]{3,}\.[0-9]{3,}\.N[0-9]{3,}/g;
    let nnis = raw_data.match(regex_nni);
    return nnis || [];
}


function IdentifyServices(service_list) {
    let raw_data = service_list.join(' ');
    if (!raw_data) {
        return []; // return null 
    }
    let regex = /[A-Z]{3,}\.[0-9]{3,}\.[A-Z[0-9]{3,}/g;
    let serviceIds = raw_data.match(regex);
    return serviceIds || [];
}





var serviceGroups = {};
var services_list = []
// this function will receive a string with all services and filter services and get info from quickbase 
async function getServicesInfo(newServices) {
    console.log('services', newServices)
    services_list.push(newServices + " ")
    console.log('services', services)
    const nnis = IdentifyServicesNni(services_list)

    if (nnis !== null) {
        const promises = nnis.map(async nni => {
            console.log("nni encontrado ", nni);
            let services_attached_nni = await get_service_attached_nnis(nni);
            console.log("services_attached_nni ", services_attached_nni);
            if (services_attached_nni !== null) {
                services_list.push(services_attached_nni.join(' ') + " ");
            }
        });
        await Promise.all(promises);
    }

    const serviceIds = IdentifyServices(services_list);

    const url = 'https://api.quickbase.com/v1/records/query';

    const serviceDataElement = document.getElementById('serviceData');
    serviceDataElement.innerHTML = '';

    serviceGroups = {};
    let totalCircuits = 0;

    const uniqueServiceIds = [...new Set(serviceIds)];

    for (const serviceId of uniqueServiceIds) {
        const prefix = serviceId.split('.')[0];

        if (!serviceGroups[prefix]) {
            serviceGroups[prefix] = {
                ids: new Set(),
                attributes: {},
                contacts: null // Inicializando como null
            };
        }

        serviceGroups[prefix].ids.add(serviceId);
        totalCircuits++;
    }


    const totalCircuitsElement = document.createElement('h6');
    totalCircuitsElement.id = "all_services"
    totalCircuitsElement.textContent = `All Services: ${totalCircuits}`;
    serviceDataElement.appendChild(totalCircuitsElement);

    const progressBar = document.createElement('div');
    progressBar.className = 'progress-container';
    const progressInner = document.createElement('div');
    progressInner.className = 'progress-bar';
    progressInner.id = 'progressBar';
    progressInner.textContent = '0%';
    progressBar.appendChild(progressInner);
    serviceDataElement.appendChild(progressBar);

    let progress = 0;

    for (const prefix in serviceGroups) {
        const { ids, attributes } = serviceGroups[prefix];
        const contacts = await get_customers_contact(prefix); // Aguardando a obtenção dos contatos
        serviceGroups[prefix].contacts = contacts; // Atualizando os contatos no objeto

        const serviceGroup = document.createElement('div');
        serviceGroup.className = 'service-group';
        const groupHeader = document.createElement('h6');
        groupHeader.textContent = `${prefix} - Services: ${ids.size}`;
        groupHeader.addEventListener('click', function () {
            this.nextElementSibling.classList.toggle('hidden');
        });
        serviceGroup.appendChild(groupHeader);

        const table = document.createElement('table');
        table.className = 'service-table hidden';

        for (const serviceId of ids) {
            const body = {
                from: "bfwgbisz4",
                select: [465, 467, 337, 36, 25, 3, 511, 700],
                where: "{7.CT.'" + serviceId + "'}"
            };

            try {
                const response = await axios.post(url, body, { headers: headers });
                if (response.status === 200) {
                    const result = response.data;
                    if (result.data.length > 0) {
                        const field = result.data[0];
                        const status = field['36'].value;
                        attributes[serviceId] = {
                            id: field['3'].value,
                            endereco: field['25'].value,
                            clienteFinal: field['337'].value,
                            cidade: field['465'].value,
                            pais: field['467'].value,
                            status: field['36'].value,
                            diversidade: field['511'].value,
                            servicoDiversoRelacionado: field['700'].value
                        };
                        const atributosString = JSON.stringify(attributes[serviceId]);
                        const statusClass = field['36'].value.toLowerCase() === 'cancelled' ? 'cancelled' : '';
                        const tableRow = `
                            <tr>
                                <td title='${atributosString}' class="${statusClass}">
                                    ${serviceId} - ${status} <button class="delete_button" value="${field['3'].value}" onclick="ExcludeDataFromDatble()"> Delete <button>
                                </td>
                            </tr>
                            `;
                        table.innerHTML += tableRow;
                    } else {
                        console.log(`Nenhum dado encontrado para o ID do serviço ${serviceId}`);
                    }
                } else {
                    console.log(`Falha na solicitação para o ID do serviço ${serviceId}. Status code: ${response.status}`);
                }
            } catch (error) {
                console.error("Erro:", error);
                alert(`Ocorreu um erro ao processar a solicitação para o ID do serviço ${serviceId}. Consulte o console para mais detalhes.`);
            }

            // Atualizar a barra de progresso
            progress++;
            const percentProgress = Math.round((progress / totalCircuits) * 100);
            progressInner.style.width = percentProgress + '%';
            progressInner.textContent = percentProgress + '%';
        }

        const tableFooter = `
                </tbody>
            `;
        table.innerHTML += tableFooter;
        serviceGroup.appendChild(table);
        serviceDataElement.appendChild(serviceGroup);

    }
}




// this function retrive the customer contact from quickbase  

async function get_customers_contact(customer_prefix) {

    const body = {
        "from": "bgvi3a68b",
        "select": [20, 64, 65, 64, 69, 70, 17, 55],
        "where": `{65.CT.'${customer_prefix}'}OR{70.CT.'${customer_prefix}'}OR{7.CT.'${customer_prefix}'}AND{55.CT.'NOC'}`
    };

    try {
        const response = await axios.post('https://api.quickbase.com/v1/records/query', body, { headers });

        if (response.status === 200 && response.data.data && response.data.data.length > 0) {
            const { '69': { value: request_ids_zendesk }, '20': { value: customer_name } } = response.data.data[0];
            return [request_ids_zendesk, customer_name]; // Retornando os dados como uma lista
        } else {
            return null;
        }
    } catch (error) {
        console.error(`Error fetching customer data: ${error}`);
        return null;
    }
}




// this button close the result core modal 
document.getElementById('close_button').addEventListener('click', function () {
    document.getElementById('feedback_create_core').style.display = 'none';
});



// this function retrive services attached to nni this data is from quickbase field 7 table bmeeuqk9d
async function get_service_attached_nnis(service) {
    try {


        const body = {
            "from": "bmeeuqk9d",
            "select": [7],
            "where": `{21.CT.'${service}'}AND{18.CT.'Delivered'}`
        };

        const url = 'https://api.quickbase.com/v1/records/query';
        const response = await axios.post(url, body, { headers });

        const responseJson = response.data;
        // extract data from list 
        const servicesList = responseJson.data.map(record => record['7'].value);
        return servicesList;
    } catch (error) {
        console.error('An error has occurred :', error.message);
        return null;
    }
}



// This function will get off the service when delete button were pressed, and it also delete from the array and update the service count

function ExcludeDataFromDatble() {
    let all_services = 0;
    const counter_all_services = document.getElementById('all_services')
    document.querySelectorAll('.delete_button').forEach(function (button) {
        button.addEventListener('click', function (event) {
            event.preventDefault();
            if (this.value) {
                let id_service = this.value;
                for (const prefix in serviceGroups) {
                    const services = serviceGroups[prefix].attributes;

                    for (const serviceprefix in services) {
                        const service = services[serviceprefix];
                        if (service.id == id_service) {
                            // Remove the canceled service
                            delete serviceGroups[prefix].attributes[serviceprefix];
                            serviceGroups[prefix].ids.delete(serviceprefix);
                            var headers = document.querySelectorAll('.service-group h6');
                            for (let i = 0; i < headers.length; i++) {
                                if (headers[i].textContent.includes(prefix)) {
                                    // update the prefix counter  
                                    headers[i].textContent = `${prefix} - Services: ${serviceGroups[prefix].ids.size}`;
                                }

                            }
                        }

                    }
                    console.log(serviceGroups[prefix].ids.size)
                    all_services += serviceGroups[prefix].ids.size;
                }
                // update the main counter for all services 
                counter_all_services.textContent = `All services: ${all_services}`
            }
            // Remove the row (tr) containing the clicked button
            var row = this.closest('tr');
            if (row) {
                row.remove();
            }
        });
    });
}



const add_service = document.getElementById('add_services')
add_service.addEventListener('click', function (event) {
    event.preventDefault();
    const input_add_service = document.querySelector('input[name="add_service_input"]');
    let service_ids_raw = input_add_service.value;
    getServicesInfo(service_ids_raw)
});

// Function to color rows of a table based on the content of the second cell
function Paint_table() {
    var table = document.getElementsByClassName('table');
    console.log("chamou paint funcion")
    // Get all rows of the table, excluding the header
    var rows = table[0].getElementsByTagName('tbody')[0].getElementsByTagName('tr');

    // Iterate over the rows and apply the coloring logic
    for (var i = 0; i < rows.length; i++) {
        var ping = rows[i].getElementsByTagName('td')[1];
        var status = rows[i].getElementsByTagName('td')[2];// Assumes that the condition is in the second cell (index 1)
        if (ping.innerHTML.includes("DOWN") || status.innerHTML.includes("DOWN")) {
            console.log("entrou aqui down")
            // If the text is 'DOWN', color the row red
            rows[i].style.backgroundColor = 'gray';
            rows[i].style.color = 'white';
        } else {


            rows[i].style.backgroundColor = 'rgba(38, 223, 116, 0.56)';
            rows[i].style.color = 'white';
        }
    }
}

// Select all buttons with the id 'button_test'
const buttons = document.querySelectorAll('#button_test');

// Async function to send services to be tested
const Send_services_to_be_tested = async (id) => {
    const url = '/test_services/';
    const modal = document.getElementById('optionsModal');
    const resultsContainer = document.getElementById('results');
    var spinner = document.getElementById("spinner");
    var load = document.getElementById("load");
    spinner.style.display = "block";
    load.style.display = "block";
    const data = new FormData();
    data.append('id', id);
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            body: data
        });

        if (response.ok) {
            spinner.style.display = "none";
            load.style.display = "none";
            const responseData = await response.json();
            console.log(responseData.services);

            // Clear previous results
            resultsContainer.innerHTML = '';

            // Create a table to display the results
            const table = document.createElement('table');
            table.classList.add('table'); // Add Bootstrap classes if using Bootstrap

            // Add table header
            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            const headers = [];

            responseData.services.forEach(data => {
                spinner.style.display = "none";
                load.style.display = "none";
                console.log(data);
                console.log(typeof (data))
                if (data) {  // Check if data is not null or undefined
                    Object.keys(data).forEach(key => {
                        if (!headers.includes(key)) {
                            headers.push(key);
                        }
                    });
                }
            });

            headers.forEach(header => {
                const th = document.createElement('th');
                th.textContent = header;
                headerRow.appendChild(th);
            });

            thead.appendChild(headerRow);
            table.appendChild(thead);

            // Add table rows
            const tbody = document.createElement('tbody');
            responseData.services.forEach(data => {
                if (data) {  // Check if there is data before adding to the table
                    const row = document.createElement('tr');
                    headers.forEach(header => {
                        console.log('header', header)
                        const td = document.createElement('td');
                        const cellValue = data[header]; // Access the property directly
                        td.textContent = cellValue;
                        row.appendChild(td);

                    });
                    tbody.appendChild(row);
                }
            });

            table.appendChild(tbody);
            resultsContainer.appendChild(table);

            // Show the modal
            const modalInstance = new bootstrap.Modal(modal);
            modalInstance.show();
            Paint_table();
        } else {
            console.log("An Error has occurred during the fetch data");
        }
    } catch (error) {
        console.log("An Error has occurred during the fetch data", error);
    }
};

// Attach click event listeners to each button
buttons.forEach(button => {
    button.addEventListener('click', (event) => {
        const id = button.value;
        console.log(id);
        Send_services_to_be_tested(id);
    });
});

// Function to create and populate a table based on the selected core ID
function createTable(tableId) {
    select_core_id.addEventListener('change', async () => {
        const data1 = new FormData();
        data1.append('id', select_core_id.value);
        const table_element = document.getElementById(tableId);

        try {
            const response = await fetch("/compare_tests/", {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                body: data1,
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const responseData = await response.json();

            // Clear the table before adding new data
            table_element.innerHTML = '';

            // Add table header
            const headerRow = table_element.insertRow();
            Object.keys(responseData.tests[0]).forEach(key => {
                const headerCell = headerRow.insertCell();
                headerCell.textContent = key;
            });

            // Add rows to the table
            responseData.tests.forEach(test => {
                const row = table_element.insertRow();
                let hasDown = false;  // Flag to check if "DOWN" is present in any cell of the row

                Object.values(test).forEach(value => {
                    const cell = row.insertCell();
                    cell.textContent = value;

                    if (value.includes("DOWN") || value.includes("None")) {
                        console.log("contains down ");
                        hasDown = true;
                    }
                });

                // Set the row color based on the presence of "DOWN"
                if (hasDown) {
                    row.style.backgroundColor = 'rgb(108, 117, 125, 0.59)';
                    row.style.color = 'white';
                } else {
                    row.style.backgroundColor = 'rgb(108, 500, 125, 0.59)';
                    row.style.color = 'white';
                }
            });

            // Add the table to the document (if needed)
            // document.body.appendChild(table_element);

        } catch (error) {
            // Handle errors
            console.error('Fetch error:', error);
        }
    });
}

const select_core_id = document.getElementById('core_test1');

// Call the function with different table IDs
createTable('table_1');
createTable('table_2');

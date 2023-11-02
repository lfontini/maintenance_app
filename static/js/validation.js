$(function () {
    // progress bar config 
    var $feedbackValidacao = $("#feedback-validacao");
    var $progressBar = $feedbackValidacao.find(".progress-bar");
    var $feedbackMensagem = $feedbackValidacao.find("#feedback-mensagem");
    var $feedbackErro = $feedbackValidacao.find("#feedback-erro");


    // clear textbox
    $("#input-circuitos").on("input", function () {
        if ($(this).val()) {
            $("#btn-limpar").show();
        }
        else {
            $("#btn-limpar").hide();
        }
    });


    $("#btn-limpar").on("click", function () {
        $("#input-circuitos").val("").trigger("input");
        $("#form-validacao").validate().resetForm();
        $feedbackValidacao.hide();
        $feedbackMensagem.empty();
        $feedbackErro.empty();
        $progressBar.css("width", "0%");
    });

    function identify_services(data) {
        const pattern = /[a-zA-Z0-9]{3}\.[0-9]{3,6}\.[a-zA-Z][0-9]{3}/g;
        const matches = data.matchAll(pattern);
        const results = [];

        for (const match of matches) {
            circuito = match[0]
            if (results.indexOf(circuito) === -1) {
                console.log("adicionado " + circuito)
                results.push(match[0]);
            }

        }

        return results;
    }

    // Send form
    $("#form-validacao").on("submit", function (event) {
        event.preventDefault();
        $feedbackValidacao.show();
        $feedbackMensagem.text("Validando circuitos...");
        $progressBar.css("width", "0%");
        $feedbackErro.empty();

        var circuitos = identify_services($("#input-circuitos").val());

        var table = $("<table>").addClass("table");
        var thead = $("<thead>");
        var tr = $("<tr>");
        tr.append($("<th>").text("Circuito"));
        tr.append($("<th>").text("Trafego RX"));
        tr.append($("<th>").text("Trafego TX"));
        tr.append($("<th>").text("Ping"));
        tr.append($("<th>").text("Status"));
        tr.append($("<th>").text("Status Quick Base"));

        thead.append(tr);
        table.append(thead);
        var tbody = $("<tbody>");
        circuitos.forEach(circuito => {
            setTimeout(5000)
            $.ajax({
                url: "/circuito_validacao",
                method: "POST",
                data: { circuitos: circuito },
                success: function (response) {
                    console.log("RESULTADO  :" + response)
                    console.log(response)
                    var resultado = response['results'][0][0]
                    console.log("RAW RESULT :", resultado)
                    // Add a new row for each circuit
                    for (var i = 0; i < resultado.length; i++) {
                        console.log(resultado[i]['circuito']);
                        var circuito = resultado[i]['circuito'];
                        var trafego_rx = resultado[i]['interfacestatus']['Download'];
                        var trafego_tx = resultado[i]['interfacestatus']['Upload'];
                        if (trafego_rx == undefined || trafego_tx == undefined) {
                            trafego_rx = "None data retrived";
                            trafego_tx = "None data retrived";
                        }
                        var ping = resultado[i]['resultadoping'];
                        var status = resultado[i]['status'];
                        var QB = resultado[i]
                        ['statusquickbase'];
                        var tr = $("<tr>");

                        tr.append($("<td>").text(circuito));
                        tr.append($("<td>").text(trafego_rx));
                        tr.append($("<td>").text(trafego_tx));
                        tr.append($("<td>").text(ping));
                        tr.append($("<td>").text(status));
                        tr.append($("<td>").text(QB));
                        tbody.append(tr);
                    }




                    $feedbackValidacao.empty().append(table.append(tbody)).show();
                    $feedbackMensagem.empty();
                    $progressBar.css("width", "0%");
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    $feedbackMensagem.empty();
                    $progressBar.css("width", "0%");
                    $feedbackErro.text(`An Error has occured to validate the services CODE:  ${errorThrown}`);
                    console.error(textStatus, errorThrown);
                }
            });
        });
        $("#counter").text("Services Identified: " + circuitos.length);
    });


    // Atualizar a barra de progresso durante a validação
    $(document).on("ajaxSend", function (event, xhr, settings) {
        if (settings.url == "/circuito_validacao") {
            $progressBar.css("width", "70%");
        }
    });

    $(document).on("ajaxComplete", function (event, xhr, settings) {
        if (settings.url == "/circuito_validacao") {
            $progressBar.css("width", "100%");
        }
    });


});

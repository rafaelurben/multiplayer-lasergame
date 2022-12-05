var socket;

function connect(name) {
    let prot = location.protocol === "http:" ? "ws://" : "wss://";
    let ws = new WebSocket(prot + location.host + "/ws");

    ws.onopen = function (e) {
        console.log("[WS] Connection established, sending name...");
        ws.send(name)
    };

    ws.onmessage = function (event) {
        console.log(`[WS] Data received from server: ${event.data}`);
        alert("Data received from server: " + event.data);
    };

    ws.onclose = function (event) {
        if (event.wasClean) {
            console.log(`[WS] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
        } else {
            // e.g. server process killed or network down
            // event.code is usually 1006 in this case
            console.warn('[WS] Connection died', event);
            alert('[close] Connection died');
        }
    };

    ws.onerror = function (error) {
        alert(`Error: ${error.message}`);
    };

    return ws;
}

function ws_sendjson(data) {
    socket.send(JSON.stringify(data));
}

function ws_setname() {
    let nameinput = document.getElementById("nameinput");
    let name = nameinput.value;

    if (name == "") {
        alert("Bitte gib einen Namen ein!");
        return;
    }

    nameinput.value = "";
    document.getElementById("nameinputsubmit").innerText = "Name ändern";

    if (socket === undefined || socket.readyState != WebSocket.OPEN) {
        socket = connect(name);
    } else {
        ws_sendjson({ "action": "setname", "name": name });
    }
}

class GameSocket {
    constructor() {
        this.socket = undefined;
        this.mode = undefined;
        this._isSetup = false;

        this.connect();
    }

    connect() {
        let newthis = this;

        let prot = location.protocol === "http:" ? "ws://" : "wss://";
        this.socket = new WebSocket(prot + location.host + "/ws");

        this.socket.onopen = function (event) {
            console.log("[WS] Connection established!");
        };

        this.socket.onmessage = function (event) {
            let json = JSON.parse(event.data);
            console.debug("[WS] Data received:", json);
            newthis.onreceive(json);
        };

        this.socket.onclose = function (event) {
            if (event.wasClean) {
                console.log(`[WS] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
            } else {
                // e.g. server process killed or network down
                // event.code is usually 1006 in this case
                console.warn('[WS] Connection died', event);
                alert('[Error] Connection died');
            }
        };

        this.socket.onerror = function (error) {
            alert(`Error: ${error.message}`);
        };
    }

    onreceive(json) {
        let action = json.action;
    }

    send(json) {
        this.socket.send(JSON.stringify(json));
        console.debug(`[WS] Sent:`, json);
    }

    setupPlayer(name) {
        if (this._isSetup) {
            console.error("[WS] Cannot setup twice!");
            return;
        }
        this.send({"action": "setup", "mode": "player", "name": name})
        this._isSetup = true;
    }

    setupSpectator() {
        if (this._isSetup) {
            console.error("[WS] Cannot setup twice!");
            return;
        }
        this.send({"action": "setup", "mode": "spectator"})
        this._isSetup = true;
    }
}

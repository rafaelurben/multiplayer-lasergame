TEAMNAMES = ["Team\xa0Red", "Team\xa0Blue"];
TEAMNAME_NONE = "No\xa0team";

class Game {
    constructor() {
        this.client = {
            mode: undefined,
            id: undefined,
        }
        this.player = {
            name: undefined,
            team: undefined,
            id: undefined,
        }

        this.__state = undefined;
        
        this.joining_allowed = undefined;
        this.players = {};

        this.canvas = undefined;

        this.public_url = undefined;

        // On page load: add team select buttons
        window.addEventListener('load', () => {
            let teamselectcontainer = $("#teamselectcontainer");
            for (let team in TEAMNAMES) {
                teamselectcontainer.append($(`<button class="btn t${team}-bg fs-2" onclick="sock.selectTeam(${team})">${TEAMNAMES[team]}</button>`))
            }
        })
    }

    get state() { return this.__state; }
    set state(value) { this.__state = value; this.handleStateUpdate(); }

    updateUi() {
        $(`.modeblock:not(#mode_${this.client.mode})`).addClass("hidden");
        $(`.modeblock.mode_${this.client.mode}`).removeClass("hidden");
        $(`.stateblock:not(#state_${this.state})`).addClass("hidden");
        $(`.stateblock.state_${this.state}`).removeClass("hidden");

        if (this.player.team === undefined || this.player.team === null) {
            $("#header_team").attr('class', 'hidden');
        } else {
            $("#header_team").attr('class', `ms-2 t${this.player.team}-fg`); 
        }

        if (this.client.mode === "connected") {
            $("#header_status").text(`Connected (#${this.client.id})`);

            if (this.joining_allowed) {
                $("#lobby_join_player_form").removeClass("hidden");
                $("#lobby_join_player_disabled_message").addClass("hidden");
            } else {
                $("#lobby_join_player_form").addClass("hidden");
                $("#lobby_join_player_disabled_message").removeClass("hidden");
            }
        } else
        if (this.client.mode === "player") {
            $("#header_status").text(`Playing as ${this.player.name}\xa0(#${this.client.id})`);
        } else
        if (this.client.mode === "spectator" || this.client.mode === "master") {
            if (this.client.mode === "master") {
                $("#header_status").text(`Hosting (#${this.client.id})`);
            } else {
                $("#header_status").text(`Spectating (#${this.client.id})`);
            }

            if (this.state.startsWith('lobby')) this.renderSpectatorLobby();
        }
    }

    handleStateUpdate() {
        this.updateUi();

        if (this.state !== "ingame" && this.canvas !== undefined) {
            this.canvas.stage.destroy();
            this.canvas = undefined;
        } else if (this.state === "ingame" && this.canvas === undefined && this.client.mode === "spectator" || this.client.mode === "master") {
            this.canvas = new GameCanvas('spectatorcanvascontainer', 30, 15);
        }
    }

    renderSpectatorLobby() {
        let playerlistelem = $("#playerlist");
        for (let team of [null, 0, 1]) {
            // Create a new team element if it doesn't exist
            let teamelem = $(`#playerlist_team${team}`);
            if (teamelem.length === 0) {
                teamelem = $(`<div id="playerlist_team${team}" class="col playerlist_team rounded-3"></div>`);
                playerlistelem.append(teamelem);
            }

            teamelem.off('dragover');
            teamelem.off('drop');
            if (this.client.mode === "master") {
                teamelem.on('dragover', (e) => {
                    e.preventDefault();
                    e.currentTarget.classList.add("dragover");
                });
                teamelem.on('dragleave', (e) => {
                    e.preventDefault();
                    e.currentTarget.classList.remove("dragover");
                });
                teamelem.on('drop', (e) => {
                    e.preventDefault();
                    e.currentTarget.classList.remove("dragover");
                    let playerid = e.originalEvent.dataTransfer.getData("playerId");
                    window.sock.action("change_player_team", {id: playerid, team: team})
                });
            }

            teamelem.empty();
            teamelem.append(`<div class="playerlist_teamname mb-3 mt-2 fw-bold">${TEAMNAMES[team] || TEAMNAME_NONE}<span class="t${team}-fg ms-2">■</span></div>`)

            // Update the team members
            for (let playerid in this.players) {
                let player = this.players[playerid];
                if (player.team === team) {
                    let playerelem = $(`<div class="playerlist_player">${player.name} (${playerid})</div>`);

                    if (this.client.mode === "master") {
                        playerelem.attr("draggable", "true");
                        playerelem.on('dragstart', (e) => {
                            e.originalEvent.dataTransfer.setData("playerId", playerid);
                        });
                    }

                    teamelem.append(playerelem);
                }
            }
        }

        if (this.client.mode === "master") {
            if (this.state === "lobby_teamlock") {
                $("#toggle_teamlock").attr("class", 'btn btn-danger');
                $("#toggle_teamlock").text("Team change disabled");
            } else {
                $("#toggle_teamlock").attr("class", 'btn btn-success');
                $("#toggle_teamlock").text("Team change enabled");
            }
            if (this.joining_allowed) {
                $("#toggle_joining").attr("class", 'btn btn-success');
                $("#toggle_joining").text("Joining enabled");
            } else {
                $("#toggle_joining").attr("class", 'btn btn-danger');
                $("#toggle_joining").text("Joining disabled");
            }
        }

        if (this.public_url) {
            $("#toggle_qrcode").removeClass("hidden");
            let apibase = "https://api.qrserver.com/v1/create-qr-code/?format=svg&qzone=1&size=500x500&color=fff&bgcolor=212529&data="
            let url = apibase + encodeURIComponent(this.public_url);
            $("#qrcode").attr("src", url);
        }
    }
}

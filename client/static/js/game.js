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

        this.state = undefined;
        this.players = {};
    }

    updateUi() {
        $(`.modeblock:not(#mode_${this.client.mode})`).addClass("hidden");
        $(`.modeblock.mode_${this.client.mode}`).removeClass("hidden");
        $(`.stateblock:not(#state_${this.state})`).addClass("hidden");
        $(`.stateblock.state_${this.state}`).removeClass("hidden");

        if (this.player.team === undefined) {
            $("#header_team").attr('class', 'hidden');
        } else {
            $("#header_team").attr('class', `ms-2 t${this.player.team}-fg`); 
        }

        if (this.client.mode === "connected") {
            $("#header_status").text(`Connected (${this.client.id})`);
        } else
        if (this.client.mode === "player") {
            $("#header_status").text(`Joined as player ${this.player.name} (${this.client.id})`);
        } else
        if (this.client.mode === "spectator" || this.client.mode === "master") {
            $("#header_status").text(`Joined as ${this.client.mode} (${this.client.id})`);

            if (this.state === "lobby") this.renderSpectatorLobby();
        }
    }

    renderSpectatorLobby() {
        let playerlistelem = $("#playerlist");
        for (let team of [0, 1]) {
            // Create a new team element if it doesn't exist
            let teamelem = $(`#playerlist_team${team}`);
            if (teamelem.length === 0) {
                teamelem = $(`<div id="playerlist_team${team}" class="col playerlist_team"></div>`);
                playerlistelem.append(teamelem);
            }
            teamelem.empty();
            teamelem.append(`<div class="playerlist_teamname mb-3 fw-bold">Team ${team}</div>`)

            // Update the team members
            for (let playerid in this.players) {
                let player = this.players[playerid];
                if (player.team === team) {
                    teamelem.append(`<div class="playerlist_player">${player.name} (${playerid})</div>`);
                }
            }
        }
    }
}

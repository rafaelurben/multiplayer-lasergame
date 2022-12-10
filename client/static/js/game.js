TEAMNAMES = ["Team Red", "Team Blue"];
TEAMNAME_NONE = "No team";

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
        this.joining_allowed = undefined;
        this.players = {};

        // On page load: add team select buttons
        window.addEventListener('load', () => {
            let teamselectcontainer = $("#teamselectcontainer");
            for (let team in TEAMNAMES) {
                teamselectcontainer.append($(`<button class="btn t${team}-bg fs-2" onclick="sock.selectTeam(${team})">${TEAMNAMES[team]}</button>`))
            }
        })
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

        if (this.state === undefined) {
            if (this.joining_allowed) {
                $("#lobby_join_player_form").removeClass("hidden");
                $("#lobby_join_player_disabled_message").addClass("hidden");
            } else {
                $("#lobby_join_player_form").addClass("hidden");
                $("#lobby_join_player_disabled_message").removeClass("hidden");
            }
        }

        if (this.client.mode === "connected") {
            $("#header_status").text(`Connected (${this.client.id})`);
        } else
        if (this.client.mode === "player") {
            $("#header_status").text(`Joined as player ${this.player.name}\xa0(${this.client.id})`);
        } else
        if (this.client.mode === "spectator" || this.client.mode === "master") {
            $("#header_status").text(`Joined as ${this.client.mode} (${this.client.id})`);

            if (this.state === "lobby") this.renderSpectatorLobby();
        }
    }

    renderSpectatorLobby() {
        let playerlistelem = $("#playerlist");
        for (let team of [null, 0, 1]) {
            // Create a new team element if it doesn't exist
            let teamelem = $(`#playerlist_team${team}`);
            if (teamelem.length === 0) {
                teamelem = $(`<div id="playerlist_team${team}" class="col playerlist_team"></div>`);
                playerlistelem.append(teamelem);
            }
            teamelem.empty();
            teamelem.append(`<div class="playerlist_teamname mb-3 fw-bold">${TEAMNAMES[team] || "No team"}</div>`)

            // Update the team members
            for (let playerid in this.players) {
                let player = this.players[playerid];
                if (player.team === team) {
                    teamelem.append(`<div class="playerlist_player">${player.name} (${playerid})</div>`);
                }
            }
        }

        if (this.client.mode === "master") {
            if (this.joining_allowed) {
                $("#toggle_joining").attr("class", 'btn btn-success');
                $("#toggle_joining").text("Joining enabled");
            } else {
                $("#toggle_joining").attr("class", 'btn btn-danger');
                $("#toggle_joining").text("Joining disabled");
            }
        }
    }
}

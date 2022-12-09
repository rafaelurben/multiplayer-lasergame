class Game {
    constructor() {
        this.client = {
            mode: "connect",
            id: undefined,
        }
        this.player = {
            name: undefined,
            team: undefined,
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

        if (this.client.mode === "player") {
            $("#header_status").text(`Connected as player ${this.player.name} (${this.client.id})`);
        } else
        if (this.client.mode === "spectator" || this.client.mode === "master") {
            $("#header_status").text(`Connected as ${this.client.mode} (${this.client.id})`);
        }
    }
}

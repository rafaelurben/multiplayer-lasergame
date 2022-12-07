class Game {
    constructor() {
        this.client = {
            mode: undefined,
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
        if (this.state === undefined) {
            document.getElementById("block_connect").classList.remove("hidden");
        } else {
            document.getElementById("block_connect").classList.add("hidden");
        }
    
        if (this.state === "lobby") {
            if (this.client.mode === "player") {
                document.getElementById("header_status").innerText = `Connected as player ${this.player.name} (${this.client.id})`;
                document.getElementById("block_teamselect").classList.remove("hidden");
                if (this.player.team !== undefined) {
                    document.getElementById("header_team").classList = `ms-2 t${this.player.team}-fg`;
                }
            } else {
                document.getElementById("block_teamselect").classList.add("hidden");
                document.getElementById("header_status").innerText = `Connected as ${this.client.mode} (${this.client.id})`;
                document.getElementById("header_team").classList = "hidden";
            }
        }
    }
}

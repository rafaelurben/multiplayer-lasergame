// Constants

TEAMNAMES = ["Team\xa0Red", "Team\xa0Blue"];
TEAMNAME_NONE = "No\xa0team";

BLOCKNAMES = [
    "Empty",    // 0
    "Wall",     // 1
    "Emitter",  // 2
    "Receiver", // 3
    "Wood",     // 4
    "Mirror",   // 5
    "Glass",    // 6
];

ROTATABLE_BLOCKS = [5];

// Page load

window.addEventListener('load', () => {
    // Add team select buttons

    let teamselectcontainer = $("#teamselectcontainer");
    for (let team in TEAMNAMES) {
        teamselectcontainer.append($(`<button class="btn t${team} t${team}-bg fs-2" onclick="sock.selectTeam(${team})">${TEAMNAMES[team]}</button>`))
    }
})

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

        this.params = { mapWidth: undefined, mapHeight: undefined };

        this.game_inventory_selected_id = null;
        this.game_inventory = [];
        this.game_map = [];

        this.__state = undefined;
        
        this.joining_allowed = undefined;
        this.joining_allowed_reason = undefined;
        this.players = {};

        this.canvas = undefined;

        this.public_url = undefined;
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
                $("#lobby_join_player_disabled_message > span").text(this.joining_allowed_reason == 'master' ? 'The host has disabled joining.' : 'The game has already started.');
            }
        } else
        if (this.client.mode === "player") {
            $("#header_status").text(`Playing as ${this.player.name}\xa0(#${this.client.id})`);

            if (this.state === 'lobby') this.renderPlayerLobby();
        } else
        if (this.client.mode === "spectator" || this.client.mode === "master") {
            if (this.client.mode === "master") {
                $("#header_status").text(`Hosting (#${this.client.id})`);
            } else {
                $("#header_status").text(`Spectating (#${this.client.id})`);
            }

            if (this.state.startsWith('lobby')) this.renderSpectatorLobby();
        }

        if (this.public_url !== undefined && this.public_url !== null) {
            $("#show_qrcode").removeClass("hidden");
            let apibase = "https://api.qrserver.com/v1/create-qr-code/?format=svg&qzone=1&size=500x500&color=fff&bgcolor=212529&data="
            let url = apibase + encodeURIComponent(this.public_url);
            $("#qrcode_image").attr("src", url);
            $("#qrcode_link").attr("href", this.public_url);
        }
    }

    handleStateUpdate() {
        this.updateUi();

        if (this.state !== "ingame" && this.canvas !== undefined) {
            this.canvas.stage.destroy();
            this.canvas = undefined;
        } else if (this.state === "ingame" && this.canvas === undefined) {
            if (this.client.mode === "spectator" || this.client.mode === "master") {
                this.canvas = new SpectatorCanvas(this, 'spectatorcanvascontainer', this.params.mapWidth, this.params.mapHeight);
            } else if (this.client.mode === "player") {
                this.canvas = new PlayerCanvas(this, 'playercanvascontainer', this.params.mapWidth, this.params.mapHeight);
            }
        }
    }

    renderPlayerLobby() {
        for (let team in TEAMNAMES) {
            let selectbtn = $(`#teamselectcontainer > button.t${team}`);
            selectbtn.toggleClass("selected", this.player.team === parseInt(team));
        }
    }

    renderSpectatorLobby() {
        let kickplayerelem = $("#kick_player");
        let playerlistelem = $("#playerlist");
        for (let team of [null, 0, 1]) {
            // Create a new team element if it doesn't exist
            let teamelem = $(`#playerlist_team${team}`);
            if (teamelem.length === 0) {
                teamelem = $(`<div id="playerlist_team${team}" class="col playerlist_team rounded-3"></div>`);
                playerlistelem.append(teamelem);
            }

            teamelem.off('dragover');
            teamelem.off('dragleave');
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
                            kickplayerelem.attr('class', 'btn btn-outline-danger');
                        });
                        playerelem.on('dragend', (e) => {
                            kickplayerelem.attr('class', 'd-none');
                        });
                    }

                    teamelem.append(playerelem);
                }
            }
        }

        kickplayerelem.off('dragover');
        kickplayerelem.off('dragleave');
        kickplayerelem.off('drop');
        if (this.client.mode === "master") {
            if (this.state === "lobby_teamlock") {
                $("#toggle_teamlock").attr("class", 'btn btn-danger');
                $("#toggle_teamlock").html("<u>T</u>eam change disabled");
            } else {
                $("#toggle_teamlock").attr("class", 'btn btn-success');
                $("#toggle_teamlock").html("<u>T</u>eam change enabled");
            }
            if (this.joining_allowed) {
                $("#toggle_joining").attr("class", 'btn btn-success');
                $("#toggle_joining").html("<u>J</u>oining enabled");
            } else {
                $("#toggle_joining").attr("class", 'btn btn-danger');
                $("#toggle_joining").html("<u>J</u>oining disabled");
            }


            kickplayerelem.on('dragover', (e) => {
                e.preventDefault();
                kickplayerelem.attr('class', 'btn btn-danger');
            });
            kickplayerelem.on('dragleave', (e) => {
                e.preventDefault();
                kickplayerelem.attr('class', 'btn btn-outline-danger');
            });
            kickplayerelem.on('drop', (e) => {
                e.preventDefault();
                kickplayerelem.attr('class', 'd-none');
                let playerid = e.originalEvent.dataTransfer.getData("playerId");
                window.sock.action("kick_player", { id: playerid })
            });
        }
    }

    renderLeaderboard(winning_team_id, winning_team_players) {
        let elem_team = $("#leaderboard-winning-team");
        let elem_players = $("#leaderboard-winning-players");

        let team_name = TEAMNAMES[winning_team_id] || TEAMNAME_NONE;

        elem_team.text(team_name);   

        let player_names = [];
        for (let player of winning_team_players) {
            player_names.push(player.name);
        }
        elem_players.text(player_names.join(", "));     
    }

    // Player inventory

    playerInventoryRender() {
        let inventoryelem = $("#player-inventory");
        inventoryelem.empty();

        this.game_inventory.forEach(block => {
            let blockelem;

            if (this.game_inventory_selected_id === block.id) {
                // Selected element
                blockelem = $(`<button class="btn btn-primary"></button>`);
            } else {
                // Unselected element
                blockelem = $(`<button class="btn btn-outline-primary"></button>`);
            }

            blockelem.html(BLOCKNAMES[block.type]+`&nbsp;(${block.id})`);

            blockelem.on('click', (e) => {
                this.playerInventorySelect(block);
            });
            inventoryelem.append(blockelem);
        });

        // Selected block
        if (this.game_inventory_selected_id !== undefined) {
            this.canvas.clearSelection();

            let block = this.playerInventoryGetSelectedBlock();
            this.playerControlsRender(block);
            if (block !== null) {
                this.canvas.drawSelection(block.pos.x, block.pos.y);
            }
        } else {
            this.canvas.clearSelection();
            this.playerControlsRender();
        }
    }

    playerInventorySelect(block) {
        if (!(block.owner === this.player.id)) return;
        
        if (this.game_inventory_selected_id === block.id) {
            // Deselect
            this.game_inventory_selected_id = null;
        } else {
            // Select
            this.game_inventory_selected_id = block.id;
        }
        this.playerInventoryRender();
    }

    playerInventoryGetSelectedBlock() {
        for (let block of this.game_inventory) {
            if (block.id === this.game_inventory_selected_id) {
                return block;
            }
        }
        return null;
    }

    // Player controls

    playerControlsPress(action) {
        // Handle player controls (move, rotate, etc.)

        window.sock.action("player_controls", {button: action, blockid: this.game_inventory_selected_id})
    }

    playerControlsRender(block) {
        $("#player-controls button").prop('disabled', true);

        if (!block || block === undefined) return;

        // Disable buttons if there is a block in the way
        $("#btn_move_up").prop('disabled', this.isBlockAt(block.pos.x, block.pos.y - 1));
        $("#btn_move_down").prop('disabled', this.isBlockAt(block.pos.x, block.pos.y + 1));
        $("#btn_move_left").prop('disabled', this.isBlockAt(block.pos.x - 1, block.pos.y));
        $("#btn_move_right").prop('disabled', this.isBlockAt(block.pos.x + 1, block.pos.y));

        // Disable buttons if the block is not a rotatable block
        $("#btn_rotate_left, #btn_rotate_right").prop('disabled', !ROTATABLE_BLOCKS.includes(block.type));
    }

    // Player map

    setMap(blocks) {
        this.game_map = blocks.sort((a, b) => a.id - b.id);
        
        if (this.client.mode === "player") {
            this.canvas.drawMap(this.game_map, this.player.id, this.player.team);
            this.game_inventory = blocks.filter(b => b.owner === this.player.id);
            this.playerInventoryRender();
            this.playerControlsRender(this.playerInventoryGetSelectedBlock());
        } else {
            this.canvas.drawMap(this.game_map);
        }
    }

    isInsideMap(x, y) {
        return x >= 0 && x < this.params.mapWidth && y >= 0 && y < this.params.mapHeight;
    }

    getBlockAt(x, y) {
        return this.game_map.find(b => b.pos.x === x && b.pos.y === y);
    }

    isBlockAt(x, y) {
        if (!this.isInsideMap(x, y)) return true;
        return this.game_map.some(b => b.pos.x === x && b.pos.y === y);
    }
}

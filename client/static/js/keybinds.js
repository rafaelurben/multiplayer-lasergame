// Keybinds

function setupKeybinds(socket) {
    document.addEventListener("keydown", function (event) {
        if (event.ctrlKey || event.altKey || event.metaKey) {
            // Ignore keybinds if ctrl/alt/meta is pressed
            return;
        }
        if ($("input").is(":focus")) {
            // Ignore keybinds if input is focused
            return;
        }

        if (socket.game.client.mode === 'master') {
            if (event.key === "s") {
                // s: Start/stop game
                event.preventDefault();
                if (socket.game.state === 'ingame' || socket.game.state === 'leaderboard') {
                    socket.action('end_game');
                } else {
                    socket.action('start_game');
                }
            } else if (event.key === "j") {
                // j: Toggle joining
                if (socket.game.state !== 'ingame') {
                    event.preventDefault();
                    socket.action('toggle_joining');
                }
            } else if (event.key === "t") {
                // t: Toggle teamlock
                if (socket.game.state !== 'ingame') {
                    event.preventDefault();
                    socket.action('toggle_teamlock');
                }
            } else if (event.key === "h") {
                // h: Shuffle teams
                if (socket.game.state !== 'ingame') {
                    event.preventDefault();
                    socket.action('shuffle_teams');
                }
            } else if (event.key === "c") {
                // c: Toggle controls
                if (socket.game.state !== 'ingame') {
                    event.preventDefault();
                    $('#master-controls').toggleClass('userhidden');
                    if (socket.game.canvas) socket.game.canvas.resize();
                }
            }
        } else if (socket.game.client.mode === 'player') {
            if (socket.game.state === 'ingame') {
                if (event.key === "i") {
                    // i: Toggle inventory
                    event.preventDefault();
                    $('#player-inventory').toggleClass('userhidden');
                    if (socket.game.canvas) socket.game.canvas.resize();
                } else if (event.key === "c") {
                    // c: Toggle controls
                    event.preventDefault();
                    $('#player-controls').toggleClass('userhidden');
                    if (socket.game.canvas) socket.game.canvas.resize();
                } else if (event.key === "ArrowUp" && $('#btn_move_up').is(':enabled')) {
                    event.preventDefault();
                    $('#btn_move_up').click();
                } else if (event.key === "ArrowDown" && $('#btn_move_down').is(':enabled')) {
                    event.preventDefault();
                    $('#btn_move_down').click();
                } else if (event.key === "ArrowLeft" && $('#btn_move_left').is(':enabled')) {
                    event.preventDefault();
                    $('#btn_move_left').click();
                } else if (event.key === "ArrowRight" && $('#btn_move_right').is(':enabled')) {
                    event.preventDefault();
                    $('#btn_move_right').click();
                } else if (event.key === "Home" && $('#btn_rotate_left').is(':enabled')) {
                    event.preventDefault();
                    $('#btn_rotate_left').click();
                } else if (event.key === "End" && $('#btn_rotate_right').is(':enabled')) {
                    event.preventDefault();
                    $('#btn_rotate_right').click();
                }
            }
        }

        if (event.key === "f") {
            // f: Toggle soft full screen (toggle menubar)
            event.preventDefault();
            $("#menubar").toggleClass("hidden");

            if (socket.game.canvas) {
                socket.game.canvas.resize();
            }
        } else if (event.key === "F") {
            // F: Toggle full screen
            event.preventDefault();
            if (document.fullscreenElement === null) {
                document.documentElement.requestFullscreen();
            } else {
                document.exitFullscreen();
            }

            if (socket.game.canvas) {
                socket.game.canvas.resize();
            }
        } else if (event.key === "l") {
            // l: Leave room
            event.preventDefault();
            socket.leave();
        } else if (event.key === "q") {
            // q: Show QR code
            event.preventDefault();
            $("#show_qrcode").click();
        }
    });
}
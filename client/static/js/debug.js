// This file is loaded if ?debug is in the URL.

console.warn("DEBUG MODE ENABLED!")
document.addEventListener('keydown', function (e) {
    console.log(e)
    if (e.shiftKey || e.ctrlKey || e.metaKey || e.altKey) return;

    if (e.key == '0') map0(window.game);
    if (e.key == '1') map1(window.game);
});

// Sample maps

function map0(game) {
    game.setMap([]);
    game.canvas.drawLasers([]);
}

function map1(game) {
    game.setMap([
        { id: 0, type: 2, pos: { x: 0, y: 4 }, team: 0 },
        { id: 1, type: 2, pos: { x: 29, y: 4 }, team: 1, rotation: 180 },
        { id: 2, type: 3, pos: { x: 0, y: 10 }, team: 1 },
        { id: 3, type: 3, pos: { x: 29, y: 10 }, team: 0, rotation: 180 },
        { id: 4, type: 4, pos: { x: 3, y: 3 }, owner: 0 },
        { id: 5, type: 4, pos: { x: 12, y: 8 }, owner: 1 },
        { id: 6, type: 5, pos: { x: 7, y: 6 }, owner: 2 },
        { id: 7, type: 5, pos: { x: 16, y: 13 }, rotation: 90, owner: 3 },
        { id: 8, type: 5, pos: { x: 4, y: 1 }, rotation: 270, owner: 4 },
        { id: 9, type: 5, pos: { x: 25, y: 4 }, rotation: 45, owner: 5 },
        { id: 10, type: 4, pos: { x: 16, y: 1 }, owner: 1 },
        { id: 11, type: 5, pos: { x: 11, y: 10 }, rotation: 315, owner: 2 },
        { id: 12, type: 5, pos: { x: 11, y: 0 }, rotation: 315, owner: 3 },
        { id: 13, type: 5, pos: { x: 25, y: 0 }, rotation: 45, owner: 4 },
    ])

    game.canvas.drawLasers([
        {
            team: 0,
            lines: [
                [[0.9, 4.5, 25.5, 4.5], 0.5],
                [[25.5, 4.5, 16.5, 13.5], 0.45],
                [[16.5, 13.5, 16.5, 2], 0.4],
            ]
        },
        {
            team: 1,
            lines: [
                [[25.5, 4.5, 29.1, 4.5], 0.5],
                [[25.5, 0.5, 25.5, 4.5], 0.45],
                [[11.5, 0.5, 25.5, 0.5], 0.4],
                [[11.5, 10.5, 11.5, 0.5], 0.35],
                [[0, 10.5, 11.5, 10.5], 0.3],
            ]
        }
    ])
}

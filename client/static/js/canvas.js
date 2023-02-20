class GameMapCanvas {
    constructor(game, containerId, mapWidth, mapHeight, baseCanvasWidth, baseCanvasHeight, mapOffsetX, mapOffsetY) {
        this.game = game;
        this.container = document.getElementById(containerId);

        this._mapCache = {};

        this.mapWidth = mapWidth;
        this.mapHeight = mapHeight;

        this.mapOffsetX = mapOffsetX;
        this.mapOffsetY = mapOffsetY;

        this.baseCanvasWidth = baseCanvasWidth;
        this.baseCanvasHeight = baseCanvasHeight;
        this.baseCanvasRatio = this.baseCanvasWidth / this.baseCanvasHeight;

        this.stage = new Konva.Stage({
            container: containerId,
            width: this.baseCanvasWidth,
            height: this.baseCanvasHeight
        })

        this.resize();
        window.addEventListener('resize', this.resize.bind(this));

        this.layer0 = new Konva.Layer();
        this.stage.add(this.layer0);
        this.layer1 = new Konva.Layer();
        this.stage.add(this.layer1);
        this.layer2 = new Konva.Layer();
        this.stage.add(this.layer2);
        
        // Main group
        this.grp_main = new Konva.Group({ x: mapOffsetX, y: mapOffsetY });
        this.layer1.add(this.grp_main);

        // Laser group
        this.grp_laser = new Konva.Group({ x: mapOffsetX, y: mapOffsetY });
        this.layer0.add(this.grp_laser);

        // Coordinate system group
        this.grp_coordsystem = new Konva.Group({ x: mapOffsetX, y: mapOffsetY });
        this.layer2.add(this.grp_coordsystem);
        this.drawCoordinateSystem();

        // Overlay group
        this.grp_overlay = new Konva.Group({ x: mapOffsetX, y: mapOffsetY });
        this.layer2.add(this.grp_overlay);
    }

    // Utils

    get containerSize() {
        // Set stage size to 0, get container size, reset stage size

        let oldwidth = this.stage.width();
        let oldheight = this.stage.height();
        this.stage.width(1);
        this.stage.height(1);
        let { width, height } = this.container.getBoundingClientRect();
        this.stage.width(oldwidth);
        this.stage.height(oldheight);
        return { width, height }
    }

    get stageWidth() {
        return this.stage.width();
    }

    get mapCanvasWidth() {
        return this.mapWidth * this.stage.scaleX();
    }

    // Resize

    resize() {
        // Get container size
        let { width, height } = this.containerSize;

        // Apply better orientation
        if (width / height >= this.baseCanvasRatio) {
            width = height * this.baseCanvasRatio;
        } else {
            height = width / this.baseCanvasRatio;
        }

        // Set stage size to container size and scale
        this.stage.width(width);
        this.stage.height(height);
        this.stage.scale({ x: width / this.baseCanvasWidth, y: height / this.baseCanvasHeight });
    }

    // Draw functions

    drawCoordinateSystem() {
        let c = 'rgba(255, 255, 255, 0.2)'; // color

        this.grp_coordsystem.destroyChildren();

        // Draw outline
        let outline = new Konva.Rect({
            x: 0,
            y: 0,
            width: this.mapWidth,
            height: this.mapHeight,
            stroke: 'white',
            strokeWidth: 0.1,
        });
        this.grp_coordsystem.add(outline);

        // Draw vertical lines
        for (let x = 1; x < this.mapWidth; x++) {
            let line = new Konva.Line({
                points: [x, 0, x, this.mapHeight],
                stroke: c,
                strokeWidth: 0.02,
            });
            this.grp_coordsystem.add(line);
        }
        // Draw horizontal lines
        for (let y = 1; y < this.mapHeight; y++) {
            let line = new Konva.Line({
                points: [0, y, this.mapWidth, y],
                stroke: c,
                strokeWidth: 0.02,
            });
            this.grp_coordsystem.add(line);
        }
    }

    drawBlock(block, isplayer, isowner, isowningteam) {
        // Check if the block is in cache

        if (this._mapCache[block.id] !== undefined) {
            let oldblock = this._mapCache[block.id].data;

            // Skip if the block hasn't changed
            if (JSON.stringify(oldblock) === JSON.stringify(block)) return;

            // Remove old block
            this._mapCache[block.id].konva.destroy();
            delete this._mapCache[block.id];
        }

        let url; // Image url
        let baseurl = '/static/graphics/';

        switch (block.type) {
            case 0: { // Empty
                break;
            } 
            case 1: { // Wall
                url = baseurl + 'wall.svg';
                break;
            }
            case 2: { // Emitter
                url = baseurl + `emitter_${block.team}.svg`;
                break;
            }
            case 3: { // Receiver
                url = baseurl + `receiver_${block.team}.svg`;
                break;
            }
            case 4: { // Wood
                url = baseurl + 'wood.svg';
                break;
            }
            case 5: { // Mirror
                url = baseurl + 'mirror.svg';
                break;
            }
            case 6: { // Glass
                url = baseurl + 'glass.svg';
                break;
            }
        }

        let rotation = -block.rotation || 0; // Rotation in radians

        // Create group to hold image and markers
        let group = new Konva.Group({
            position: block.pos,
            opacity: !isplayer || isowningteam ? 1 : 0.5,
        });
        this.grp_main.add(group);
        this._mapCache[block.id] = {
            data: block,
            konva: group,
        }

        Konva.Image.fromURL(url, (image) => {
            image.size({ width: 1, height: 1 });
            image.offset({ x: 0.5, y: 0.5 })
            image.move({ x: 0.5, y: 0.5 })
            image.rotation(rotation * 180 / Math.PI);
            group.add(image);

            // Draw markers after image is loaded
            if (isowner) {
                console.log('draw marker')
                let marker = new Konva.Rect({
                    width: .2,
                    height: .2,
                    fill: '#00ff00',
                    strokeWidth: 0.05,
                });
                group.add(marker);
            }
        });
    }

    drawMap(blocks, playerid, teamid) {
        for (let block of blocks) {
            this.drawBlock(block, playerid !== undefined, block.owner === playerid, block.team === teamid);
        }
    }

    drawLasers(lasers, isspectator) {
        let css = window.getComputedStyle(document.documentElement);

        let widthBase = 0.001; // Same as in server
        let widthMin = 0.05;
        let widthMax = 0.2;
        let widthScale = 1/(widthBase) * widthMax;

        this.grp_laser.destroyChildren();

        for (let laser of lasers) {
            let c = css.getPropertyValue(`--col-team-${laser.team}`)

            for (let line of laser.lines) {
                this.grp_laser.add(
                    new Konva.Line({
                        points: line[0],
                        stroke: c,
                        strokeWidth: Math.min(Math.max(line[1]*widthScale, widthMin), widthMax),
                        lineCap: 'round',
                        opacity: isspectator ? 1 : 0.25,
                    })
                );
            }
        }
    }
}

class SpectatorCanvas extends GameMapCanvas {
    constructor(game, containerId, mapWidth, mapHeight) {
        super(game, containerId, mapWidth, mapHeight, mapWidth+1, mapHeight+2.5, 0.5, 1.5);

        // Score group
        this.grp_score = new Konva.Group({ x: 0.5, y: 0.5 });
        this.layer0.add(this.grp_score);
        this.drawScore(0.5);
    }

    drawScore(score) {
        let css = window.getComputedStyle(document.documentElement);
        let c = 'black'; // stroke color

        this.grp_score.destroyChildren();

        let w = this.mapWidth;
        let h = 0.5;

        let team0poly = new Konva.Line({
            points: [
                0, 0,
                score * (w - 0.5) + 0.25, 0,
                score * (w - 0.5), h,
                0, h,
            ],
            fill: css.getPropertyValue('--col-team-0'),
            stroke: c,
            strokeWidth: 0.1,
            closed: true,
        })
        this.grp_score.add(team0poly);

        let team1poly = new Konva.Line({
            points: [
                w, 0,
                score * (w - 0.5) + 0.5, 0,
                score * (w - 0.5) + 0.25, h,
                w, h,
            ],
            fill: css.getPropertyValue('--col-team-1'),
            stroke: c,
            strokeWidth: 0.1,
            closed: true,
        })
        this.grp_score.add(team1poly);
    }
}

class PlayerCanvas extends GameMapCanvas {
    constructor(game, containerId, mapWidth, mapHeight) {
        super(game, containerId, mapWidth, mapHeight, mapWidth+1, mapHeight+1, 0.5, 0.5);

        // Draggable stage
        this.stage.draggable(true);
        this.stage.dragBoundFunc((pos) => {
            // Define the dragging boundaries
            return {
                // Prevent dragging the map out of view
                x: this.normalizeX(pos.x),
                // Disable vertical dragging
                y: this.stage.absolutePosition().y
            };
        });

        // Set default view position depending on team (only relevant for small devices)
        this.stage.x(this.normalizeX(this.game.player.team === 0 ? Infinity : -Infinity));

        // Block selection
        this.stage.on('click', (e) => {
            // Get the clicked block
            let pos = this.grp_main.getRelativePointerPosition();
            let { x, y } = { x: Math.floor(pos.x), y: Math.floor(pos.y) };
            let block = this.game.getBlockAt(x, y);

            if (block) {
                this.game.playerInventorySelect(block);
            }
        });
        this.stage.on('touchstart', (e) => {
            // Get the clicked block
            let pos = this.grp_main.getRelativePointerPosition();
            let { x, y } = { x: Math.floor(pos.x), y: Math.floor(pos.y) };
            let block = this.game.getBlockAt(x, y);

            if (block) {
                this.game.playerInventorySelect(block);
            }
        });
    }

    // Position

    normalizeX(x) {
        // Normalize x position to prevent dragging the map out of view
        let fullCanvasWidth = this.mapCanvasWidth * ((this.mapWidth+(2*this.mapOffsetX))/this.mapWidth);
        let containerWidth = this.containerSize.width;
        
        if (fullCanvasWidth > containerWidth) {
            // Small device (map is wider than screen)
            let min_x = containerWidth - fullCanvasWidth;
            return Math.min(Math.max(x, min_x), 0);
        } else {
            // Large device (map is smaller than screen)
            // Center map horizontally
            return ((containerWidth - fullCanvasWidth) / 2);
        }
    }

    resize() {
        // Get container size
        let { width, height } = this.containerSize;

        // Set stage size to container size
        this.stage.width(width);
        this.stage.height(height);

        // Scale stage to fit map vertically
        this.stage.scale({ x: height / this.baseCanvasHeight, y: height / this.baseCanvasHeight });

        // Normalize position (if needed)
        this.stage.x(this.normalizeX(this.stage.x()));
    }

    // Draw functions

    clearSelection() {
        this.grp_overlay.destroyChildren();
    }

    drawSelection(x, y) {
        let c = '#00ff00'; // stroke color
        let sw = 0.05 // stroke width

        let rect = new Konva.Rect({
            x: x+(sw/2),
            y: y+(sw/2),
            width: 1-sw,
            height: 1-sw,
            stroke: c,
            strokeWidth: sw,
        });
        this.grp_overlay.add(rect);
    }
}

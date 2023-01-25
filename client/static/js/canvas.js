class GameMapCanvas {
    constructor(game, containerId, mapWidth, mapHeight, baseCanvasWidth, baseCanvasHeight, mapOffsetX, mapOffsetY) {
        this.game = game;
        this.container = document.getElementById(containerId);

        this.mapWidth = mapWidth;
        this.mapHeight = mapHeight;

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
        
        // Main group
        this.grp_main = new Konva.Group({ x: mapOffsetX, y: mapOffsetY });
        this.layer0.add(this.grp_main);

        // Coordinate system group
        this.grp_coordsystem = new Konva.Group({ x: mapOffsetX, y: mapOffsetY });
        this.layer1.add(this.grp_coordsystem);
        this.drawCoordinateSystem();

        // Overlay group
        this.grp_overlay = new Konva.Group({ x: mapOffsetX, y: mapOffsetY });
        this.layer1.add(this.grp_overlay);
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

    drawBlock(block) {
        let url; // Image url
        let baseurl = '/static/graphics/';

        switch (block.type) {
            case 0: { // Empty
                break;
            } 
            case 1: { // Wall
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
                break;
            }
        }

        let rotation = block.rotation || 0; // Rotation in degrees

        Konva.Image.fromURL(url, (image) => {
            image.size({ width: 1, height: 1 });
            image.position(block.pos);
            image.offset({ x: 0.5, y: 0.5 })
            image.move({ x: 0.5, y: 0.5 })
            image.rotation(rotation);
            this.grp_main.add(image);
        });
    }

    drawMap(blocks) {
        this.grp_main.destroyChildren();

        for (let block of blocks) {
            this.drawBlock(block);
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
            let offset = 24;

            let min_x, max_x;

            if (this.mapCanvasWidth > this.stageWidth) {
                // Small device (map is wider than screen)
                min_x = this.stageWidth - this.mapCanvasWidth - offset;
                max_x = 0;
            } else {
                // Large device (map is smaller than screen)
                min_x = 0;
                max_x = this.stageWidth - this.mapCanvasWidth - offset;
            }

            return {
                // Prevent dragging outside of the map
                x: Math.min(Math.max(pos.x, min_x), max_x),
                // Disable vertical dragging
                y: this.stage.absolutePosition().y
            };
        });

        this.setInitialPosition();

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
    }

    // Position

    getInitialPositionX() {
        let offset = 24;

        if (this.mapCanvasWidth <= this.stageWidth) {
            // Center map horizontally
            return ((this.stageWidth - this.mapCanvasWidth - offset) / 2);
        } else if (this.game.player.team == 1) {
            // Show most right part of the map for team 1
            return (this.stageWidth - this.mapCanvasWidth - offset);
        }
    }

    setInitialPosition() {
        this.stage.x(this.getInitialPositionX());
    }

    resize() {
        // Get container size
        let { width, height } = this.containerSize;

        // Set stage size to container size
        this.stage.width(width);
        this.stage.height(height);

        // Scale stage to fit map vertically
        this.stage.scale({ x: height / this.baseCanvasHeight, y: height / this.baseCanvasHeight });

        // Set initial position
        if (this.mapCanvasWidth <= this.stageWidth) {
            this.setInitialPosition();
        }
    }

    // Draw functions

    clearSelection() {
        this.grp_overlay.destroyChildren();
    }

    drawSelection(x, y) {
        let c = '#00ff00'; // stroke color

        let rect = new Konva.Rect({
            x: x,
            y: y,
            width: 1,
            height: 1,
            stroke: c,
            strokeWidth: 0.05,
        });
        this.grp_overlay.add(rect);
    }
}

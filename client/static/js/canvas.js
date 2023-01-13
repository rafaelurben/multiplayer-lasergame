class GameMapCanvas {
    constructor(containerId, mapWidth, mapHeight, canvasWidth, canvasHeight, mapOffsetX, mapOffsetY) {
        this.container = document.getElementById(containerId);

        this.mapWidth = mapWidth;
        this.mapHeight = mapHeight;

        this.w = canvasWidth;
        this.h = canvasHeight;
        this.ratio = this.w / this.h;

        this.stage = new Konva.Stage({
            container: containerId,
            width: this.w,
            height: this.h
        })

        this.resize();
        window.addEventListener('resize', this.resize.bind(this));

        this.layer = new Konva.Layer();
        this.stage.add(this.layer);

        // Coordinate system group
        this.grp_coordsystem = new Konva.Group({ x: mapOffsetX, y: mapOffsetY });
        this.layer.add(this.grp_coordsystem);
        this.drawCoordinateSystem();

        // Main group
        this.grp_main = new Konva.Group({ x: mapOffsetX, y: mapOffsetY });
        this.layer.add(this.grp_main);
    }

    clear() {
        this.grp_main.destroyChildren();
    }

    resize() {
        // Reset stage size to get correct container size
        this.stage.width(1);
        this.stage.height(1);

        // Get container size
        let { width, height } = this.container.getBoundingClientRect();

        // Apply better orientation
        if (width / height >= this.ratio) {
            width = height * this.ratio;
        } else {
            height = width / this.ratio;
        }

        // Set stage size to container size and scale
        this.stage.width(width);
        this.stage.height(height);
        this.stage.scale({ x: width / this.w, y: height / this.h });
    }

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
                strokeWidth: 0.01,
            });
            this.grp_coordsystem.add(line);
        }
        // Draw horizontal lines
        for (let y = 1; y < this.mapHeight; y++) {
            let line = new Konva.Line({
                points: [0, y, this.mapWidth, y],
                stroke: c,
                strokeWidth: 0.01,
            });
            this.grp_coordsystem.add(line);
        }
    }
}

class SpectatorCanvas extends GameMapCanvas {
    constructor(containerId, mapWidth, mapHeight) {
        super(containerId, mapWidth, mapHeight, mapWidth+1, mapHeight+2.5, 0.5, 1.5);

        // Score group
        this.grp_score = new Konva.Group({ x: 0.5, y: 0.5 });
        this.layer.add(this.grp_score);
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

        this.layer.draw();
    }
}

class PlayerCanvas extends GameMapCanvas {
    constructor(containerId, mapWidth, mapHeight, player) {
        super(containerId, mapWidth, mapHeight, mapWidth+1, mapHeight+1, 0.5, 0.5);

        this.player = player;

        // Draggable stage
        this.stage.draggable(true);
        this.stage.dragBoundFunc((pos) => {
            // Define the dragging boundaries
            let offset = 24;

            let map_width = this.mapWidth * this.stage.scaleY();
            let min_x, max_x;

            if (map_width > this.stage.width()) {
                min_x = this.stage.width() - map_width - offset;
                max_x = 0;
            } else {
                min_x = 0;
                max_x = this.stage.width() - map_width - offset;
            }

            return {
                // Prevent dragging outside of the map
                x: Math.min(Math.max(pos.x, min_x), max_x),
                // Disable vertical dragging
                y: this.stage.absolutePosition().y
            };
        });

        this.setInitialPosition();
    }

    setInitialPosition() {
        let offset = 24;
        let map_width = this.mapWidth * this.stage.scaleY();

        if (map_width <= this.stage.width()) {
            // Center map horizontally
            this.stage.x((this.stage.width() - map_width - offset) / 2);
        } else if (this.player.team == 1) {
            // Show most right part of the map for team 1
            this.stage.x(this.stage.width() - map_width - offset);
        }
    }

    resize() {
        // Reset stage size to get correct container size
        this.stage.width(1);
        this.stage.height(1);

        // Get container size
        let { width, height } = this.container.getBoundingClientRect();

        // Set stage size to container size
        this.stage.width(width);
        this.stage.height(height);

        // Scale stage to fit map vertically
        this.stage.scale({ x: height / this.h, y: height / this.h });
    }
}

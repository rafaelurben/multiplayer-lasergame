class GameCanvas {
    constructor(containerId, mapWidth, mapHeight) {
        this.container = document.getElementById(containerId);

        this.mapWidth = mapWidth || 30;
        this.mapHeight = mapHeight || 15;

        this.w = this.mapWidth + 1;
        this.h = this.mapHeight + 2.5;
        this.ratio = this.w / this.h;

        this.stage = new Konva.Stage({
            container: containerId,
            width: this.w,
            height: this.h
        })

        this.resize();
        window.addEventListener('resize', this.resize.bind(this));
        
        // Score layer
        this.scorelayer = new Konva.Layer();
        this.stage.add(this.scorelayer);

        // Coordinate system layer
        this.coordlayer = this.getCoordinateSystemLayer();
        this.coordlayer.move({ x: 0, y: 1.5});
        this.stage.add(this.coordlayer);

        // Map layer
        this.maplayer = new Konva.Layer();
        this.maplayer.move({ x: 0.5, y: 2 });
        this.stage.add(this.maplayer);
    }

    clear() {
        this.maplayer.destroyChildren();
    }

    resize() {
        // Reset stage size to get correct container size
        this.stage.width(1);
        this.stage.height(1);

        // Get container size
        let { width, height } = this.container.getBoundingClientRect();

        // Apply better orientation
        if (width/height >= this.ratio) {
            width = height * this.ratio;
        } else {
            height = width / this.ratio;
        }
        
        // Set stage size to container size and scale
        this.stage.width(width);
        this.stage.height(height);
        this.stage.scale({ x: width / this.w, y: height / this.h });
    }

    drawScore(score) {
        let o = 0.5; // offset to avoid clipping outline
        let css = window.getComputedStyle(document.documentElement);

        this.scorelayer.destroyChildren();

        let w = this.mapWidth;

        let team0poly = new Konva.Line({
            points: [
                0, 0,
                score * (w - 0.5) + 0.25, 0,
                score * (w - 0.5), 1,
                0, 1,
            ],
            fill: css.getPropertyValue('--col-team-0'),
            stroke: 'black',
            strokeWidth: 0.1,
            closed: true,
        })
        team0poly.move({ x: o, y: o })
        this.scorelayer.add(team0poly);

        let team1poly = new Konva.Line({
            points: [
                w, 0,
                score * (w - 0.5) + 0.5, 0,
                score * (w - 0.5) + 0.25, 1,
                w, 1,
            ],
            fill: css.getPropertyValue('--col-team-1'),
            stroke: 'black',
            strokeWidth: 0.1,
            closed: true,
        })
        team1poly.move({ x: o, y: o })
        this.scorelayer.add(team1poly);

        this.scorelayer.draw();
    }

    getCoordinateSystemLayer() {
        let layer = new Konva.Layer();

        let o = 0.5; // offset to avoid clipping outline
        let c = 'rgba(255, 255, 255, 0.2)'; // color

        // Draw outline
        let outline = new Konva.Rect({
            x: 0,
            y: 0,
            width: this.mapWidth,
            height: this.mapHeight,
            stroke: 'white',
            strokeWidth: 0.1,
        });
        outline.move({ x: o, y: o });
        layer.add(outline);

        // Draw vertical lines
        for (let x = 1; x < this.mapWidth; x++) {
            let line = new Konva.Line({
                points: [x, 0, x, this.mapHeight],
                stroke: c,
                strokeWidth: 0.01,
            });
            line.move({ x: o, y: o });
            layer.add(line);
        }
        // Draw horizontal lines
        for (let y = 1; y < this.mapHeight; y++) {
            let line = new Konva.Line({
                points: [0, y, this.mapWidth, y],
                stroke: c,
                strokeWidth: 0.01,
            });
            line.move({ x: o, y: o });
            layer.add(line);
        }

        return layer;
    }
}

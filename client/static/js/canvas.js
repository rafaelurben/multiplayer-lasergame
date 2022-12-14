class GameCanvas {
    constructor(containerId, mapWidth, mapHeight) {
        this.container = document.getElementById(containerId);

        this.mapWidth = mapWidth || 30;
        this.mapHeight = mapHeight || 15;

        this.w = this.mapWidth + 1;
        this.h = this.mapHeight + 3;
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
        this.coordlayer.move({ x: 0, y: 2, width: this.mapWidth + 1, height: this.mapHeight + 1 });
        this.stage.add(this.coordlayer);

        // Map layer
        this.maplayer = new Konva.Layer();
        this.maplayer.move({ x: 0.5, y: 2.5 });
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

    getCoordinateSystemLayer() {
        let layer = new Konva.Layer();

        let o = 0.5; // offset to avoid clipping outline
        let c = 'rgba(255, 255, 255, 0.2)'; // color

        // Draw outline
        layer.add(new Konva.Rect({
            x: 0 + o,
            y: 0 + o,
            width: this.mapWidth,
            height: this.mapHeight,
            stroke: 'white',
            strokeWidth: 0.1,
        }));

        // Draw vertical lines
        for (let x = 1; x < this.mapWidth; x++) {
            layer.add(new Konva.Line({
                points: [x + o, 0 + o, x + o, this.mapHeight + o],
                stroke: c,
                strokeWidth: 0.01,
            }));
        }
        // Draw horizontal lines
        for (let y = 1; y < this.mapHeight; y++) {
            layer.add(new Konva.Line({
                points: [0 + o, y + o, this.mapWidth + o, y + o],
                stroke: c,
                strokeWidth: 0.01,
            }));
        }

        return layer;
    }
}

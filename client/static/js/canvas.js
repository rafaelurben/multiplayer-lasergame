class GameCanvas {
    constructor(canvas, container) {
        this.canvas = canvas;
        this.container = container;
        this.ctx = this.canvas.getContext('2d');

        // Virtual canvas size (in game units)
        this.v_width = 30;
        this.v_height = 15;

        window.addEventListener('load', () => this.resize());
        window.addEventListener('resize', () => this.resize());
    }

    clear() {
        // clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    resize() {
        // Reset canvas size so the container has the correct dimensions
        this.canvas.style.height = "1px";
        this.canvas.style.width = "1px";

        // Calculate real canvas size
        let { width, height } = this.container.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;

        // Apply better orientation
        if (width/height >= this.v_width/this.v_height) {
            width = height * this.v_width / this.v_height;
        } else {
            height = width * this.v_height / this.v_width;
        }

        // Apply device pixel ratio and round up
        width = Math.ceil(width);
        height = Math.ceil(height);
        
        // Set canvas size (in whole pixels)
        this.canvas.width = width;
        this.canvas.height = height;
        
        // Set canvas display size (in CSS pixels, can be fractional)
        this.canvas.style.width = `${width}px`;
        this.canvas.style.height = `${height}px`;

        // Set canvas scale
        //this.ctx.scale(dpr, dpr);

        // Cleanup
        this.clear();
        this.drawCoordinateSystem();
    }

    x(x) {
        // convert virtual x to canvas x
        return (this.canvas.width / this.v_width) * x;
    }

    y(y) {
        // convert virtual y to canvas y
        return (this.canvas.height / this.v_height) * y;
    }

    c(x, y) {
        // convert virtual (x,y) to canvas (x,y)
        return [this.x(x), this.y(y)];
    }

    drawLine(x1, y1, x2, y2, width, color) {
        this.ctx.lineWidth = width;
        this.ctx.strokeStyle = color;
        this.ctx.beginPath();
        this.ctx.moveTo(...this.c(x1, y1));
        this.ctx.lineTo(...this.c(x2, y2));
        this.ctx.stroke();
        this.ctx.closePath()
    }

    drawRect(x, y, width, height, fill_color, outline_color, outline_width) {
        let args = [...this.c(x, y), ...this.c(width, height)]
        if (fill_color) {
            this.ctx.fillStyle = fill_color;
            this.ctx.fillRect(...args);
        }
        if (outline_width && outline_color) {
            this.ctx.lineWidth = outline_width;
            this.ctx.strokeStyle = outline_color;
            this.ctx.strokeRect(...args);
        }
    }

    drawCoordinateSystem(line_width) {
        this.clear();

        let lw = line_width || 1; // line width
        let c = 'rgba(255, 255, 255, 0.2)'; // color

        for (let x = 1; x < this.v_width; x++) {
            this.drawLine(x, 0, x, this.v_height, lw, c);
        }
        for (let y = 1; y < this.v_height; y++) {
            this.drawLine(0, y, this.v_width, y, lw, c);
        }

        this.drawRect(0, 0, this.v_width, this.v_height, null, 'white', 1);
    }
}

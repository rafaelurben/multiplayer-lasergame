F = 100; // scale factor

class GameCanvas {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = this.canvas.getContext('2d');

        this.setSize();
        this.drawCoordinateSystem();
    }

    clear() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    setSize(width, height) {
        let w = width || 30;
        let h = height || 15;
        this.width = w;
        this.height = h;
        this.canvas.width = w * F;
        this.canvas.height = h * F;
    }

    drawLine(x1, y1, x2, y2, width, color) {
        this.ctx.beginPath();
        this.ctx.moveTo(x1*F, y1*F);
        this.ctx.lineTo(x2*F, y2*F);
        this.ctx.lineWidth = width*F;
        this.ctx.strokeStyle = color;
        this.ctx.stroke();
    }

    drawRect(x, y, width, height, fill_color, outline_width, outline_color) {
        this.ctx.beginPath();
        this.ctx.rect(x*F, y*F, width*F, height*F);
        if (fill_color) {
            this.ctx.fillStyle = fill_color;
            this.ctx.fill();
        }
        if (outline_width && outline_color) {
            this.ctx.lineWidth = outline_width*F;
            this.ctx.strokeStyle = outline_color;
            this.ctx.stroke();
        }
    }

    drawCoordinateSystem(line_width) {
        this.clear();

        let lw = line_width || 0.05; // line width
        let c = 'rgba(255, 255, 255, 0.2)'; // color

        for (let x = 1; x < this.width; x++) {
            this.drawLine(x, 0, x, this.height, lw, c);
        }
        for (let y = 1; y < this.height; y++) {
            this.drawLine(0, y, this.width, y, lw, c);
        }

        this.drawRect(0, 0, this.width, this.height, null, 0.2, 'white');
    }
}

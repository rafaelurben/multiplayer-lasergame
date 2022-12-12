F = 10; // scale factor

class GameCanvas {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = this.canvas.getContext('2d');

        this.setSize();
    }

    setSize(width, height) {
        this.canvas.width = (width || 40) * F;
        this.canvas.height = (height || 20) * F;
    }

    drawLine(x1, y1, x2, y2, color) {
        this.ctx.beginPath();
        this.ctx.moveTo(x1*F, y1*F);
        this.ctx.lineTo(x2*F, y2*F);
        this.ctx.strokeStyle = color;
        this.ctx.stroke();
    }
}

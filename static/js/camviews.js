



class camView {
    constructor(canvasElem) {
      this.canvasElem = canvasElem;
      this.ctx = canvasElem.getContext('2d');
    }
  
    convertCanvasToBase64() {
      return this.canvasElem.toDataURL("image/png").replace(/^data:image\/(png|jpg);base64,/, '');
    }
  
    clearCanvas() {
      // clear the canvas so we can draw a fresh gauge and needle at new position
      this.ctx.clearRect(0, 0, this.canvasElem.width, this.canvasElem.height);
    }
  
    updateDimensions(width, height){
      this.canvasElem.width = width;
      this.canvasElem.height = height;
    }
  
    getDimensions(){
      return {width: this.canvasElem.width, height: this.canvasElem.height}
    }
  
    getWidth(){
      return this.canvasElem.width;
    }
  
    getHeight(){
      return this.canvasElem.height;
    } 
}
  
  
  
class primaryCamView extends camView{
    constructor(canvasElem) {
      super(canvasElem);
    }
  
    drawGaugeAndNeedle(gauge) { 
      this.ctx.beginPath();
      this.ctx.moveTo(gauge.centerX, gauge.centerY);
      this.ctx.lineTo(gauge.centerX + (gauge.xUnit*gauge.radius), gauge.centerY+(gauge.yUnit*gauge.radius));
      this.ctx.lineWidth = 4;
      this.ctx.strokeStyle = '#0000ff';
      this.ctx.stroke();
      this.drawCircles(gauge);
    }
  
    drawCircles(gauge) {  
      this.ctx.beginPath();
      this.ctx.arc(gauge.centerX, gauge.centerY, gauge.radius, 0, 2 * Math.PI, false);
      this.ctx.lineWidth = 2;
      this.ctx.strokeStyle = '#ff0000';
      this.ctx.stroke();
      this.ctx.beginPath();
      this.ctx.arc(gauge.centerX, gauge.centerY, gauge.radius/20, 0, 2 * Math.PI, false);
      this.ctx.lineWidth = 2;
      //this.ctx.fillStyle = '#ff0000';
      //this.ctx.fill();
      this.ctx.strokeStyle = '#ff0000';
      this.ctx.stroke();
    }
}
  
  
class settingsCamView extends camView{
    constructor(canvasElem) {
      super(canvasElem);
      this.crop = null;
    }
  
    drawDetectedPixels(detectedPixels) { 
      this.ctx.beginPath();
      for (let i = 0; i < detectedPixels.pointsX.length; i++) {
        this.ctx.fillRect(detectedPixels.pointsX[i], detectedPixels.pointsY[i],5,5); 
      }
      this.ctx.stroke();
    }
  
    updateCrop(x1, y1, x2, y2){
      // for cropping the video feed into a square
      this.crop = {x1: x1, y1: y1, x2: x2, y2: y2}
    }
  
    displayCropped(videoPlayer) { 
     this.ctx.drawImage(videoPlayer, this.crop.x1, this.crop.y1, this.crop.x2, this.crop.y2, 0, 0, this.canvasElem.width, this.canvasElem.height);
    }
  

    drawCirclesInSettings(gauge) {  
      this.ctx.beginPath();
      this.ctx.arc( this.canvasElem.width/2, 
                    this.canvasElem.height/2, 
                    gauge.radius*this.canvasElem.height/this.canvasElem.height*r_factor, 
                    0, 2 * Math.PI, false);
      this.ctx.lineWidth = 1;
      this.ctx.strokeStyle = '#0000ff';
      this.ctx.stroke();
      this.ctx.beginPath();
      this.ctx.arc( this.canvasElem.width/2, 
                    this.canvasElem.height/2, 
                    gauge.radius*this.canvasElem.height/this.canvasElem.height*sm_r_factor, 
                    0, 2 * Math.PI, false);
      this.ctx.lineWidth = 1;
      this.ctx.strokeStyle = '#0000ff';
      this.ctx.stroke();
    }
  
}
  
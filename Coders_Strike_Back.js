/**
 * Auto-generated code below aims at helping you parse
 * the standard input according to the problem statement.
 **/
function Vector (x, y) {
    this.x = x || 0;
    this.y = y || 0;
}

Vector.prototype.add = function (vector) {
    return new Vector(this.x + vector.x, this.y + vector.y);
};

Vector.prototype.subtract = function (vector) {
    return new Vector(this.x - vector.x, this.y - vector.y);
};

Vector.prototype.multiply = function (vector) {
    return new Vector(this.x * vector.x, this.y * vector.y);
};

Vector.prototype.multiplyScalar = function (scalar) {
    return new Vector(this.x * scalar, this.y * scalar);
};

Vector.prototype.divide = function (vector) {
    return new Vector(this.x / vector.x, this.y / vector.y);
};

Vector.prototype.divideScalar = function (scalar) {
    return new Vector(this.x / scalar, this.y / scalar);
};

Vector.prototype.length = function () {
    return Math.sqrt(Math.pow(this.x, 2) + Math.pow(this.y, 2));
};

Vector.prototype.normalize = function () {
    return this.divideScalar(this.length());
};


function findIntersect (origin, radius, shipPose) {
    var v = shipPose.subtract(origin);
    var lineLength = v.length();    
    if (lineLength === 0) throw new Error("Length has to be positive");
    v = v.normalize();
    return origin.add(v.multiplyScalar(radius)); 
}

function abs(val){
    
    return Math.sqrt((val*val));
}

function p(txt){
    printErr(txt);
}
    var speed = 100;
    var speed2 = 100;
    var oldCheckpointDist = null;
    var speedManagement = 1;
// game loop
while (true) {

    var boost = 1;
    var rad = 380;
    var inputs = readline().split(' ');
    var x = parseInt(inputs[0]);
    var y = parseInt(inputs[1]);
    var nextCheckpointX = parseInt(inputs[2]); // x position of the next check point
    var nextCheckpointY = parseInt(inputs[3]); // y position of the next check point
    var nextCheckpointDist = parseInt(inputs[4]); // distance to the next checkpoint
    var nextCheckpointAngle = parseInt(inputs[5]); // angle between your pod orientation and the direction of the next checkpoint
    var inputs = readline().split(' ');
    var opponentX = parseInt(inputs[0]);
    var opponentY = parseInt(inputs[1]);
    var destX = 0;
    var destY = 0;
    var reduc = 300;
    var ship = new Vector(x,y);
    p(ship);
    var dest = new Vector(nextCheckpointX,nextCheckpointY);
    p(dest);
    
    if (oldCheckpointDist ===null){
        oldCheckpointDist=nextCheckpointDist;
    }
    
if(nextCheckpointAngle > 90 || nextCheckpointAngle < -90){
    
 speed = 10;
    
}else{
    speed = 100;
    
}
if(nextCheckpointDist > 8000 && nextCheckpointAngle > -5 && nextCheckpointAngle < 5 && boost === 1){
    
    
  speed = 'BOOST';
} 

var newDest = Vector();
newDest = findIntersect(dest,rad,ship);
    /*
    if(nextCheckpointX >= x  && nextCheckpointY >= y){
        //SE
    var destX = nextCheckpointX-reduc;
    var destY = nextCheckpointY-reduc;
    }else  if(nextCheckpointX < x  && nextCheckpointY >= y){
        //SW
           var destX = nextCheckpointX+reduc;
    var destY = nextCheckpointY-reduc;
    }else  if(nextCheckpointX < x  && nextCheckpointY < y){
         //NW
    var destX = nextCheckpointX+reduc;
    var destY = nextCheckpointY+reduc;
     }else if(nextCheckpointX >= x  && nextCheckpointY < y){
         //NE
    var destX = nextCheckpointX-reduc;
    var destY = nextCheckpointY+reduc;
     }
  */
if(speedManagement ==1 ){
if(nextCheckpointAngle >-10 || nextCheckpointAngle < -90){
  if( nextCheckpointDist < 1500){
       speed = 50;
        speed2 = 100;
  }
  
  
   if(abs(oldCheckpointDist-nextCheckpointDist) > 2000){
       
           
       speed = 60;
       speed2 = 80;
       
   }else{
       if(speed != 'BOOST'){
       speed = speed + 10;
        speed2 = speed2 + 10;
       }
}

}else if(nextCheckpointAngle >10 || nextCheckpointAngle < 90){
    
      if( nextCheckpointDist < 1500){
       speed = 100;
        speed2 = 50;
  }
  
  
   if(abs(oldCheckpointDist-nextCheckpointDist) > 2000){
       
       speed = 80;
       speed2 = 60;
       
   }else{
       if(speed != 'BOOST'){
       speed = speed + 10;
        speed2 = speed2 + 10;
       }
}
    
    
    
}
     
     if( speed > 100 ){
         
      speed  = 100;   
     }
         if( speed2 > 100 ){
         
      speed2 = 100;   
     }
}
    // Write an action using print()
    // To debug: printErr('Debug messages...');


    // You have to output the target position
    // followed by the power (0 <= thrust <= 100)
    // i.e.: "x y thrust"
    oldCheckpointDist = nextCheckpointDist;
  if(speed != 'BOOST'){
    print(Math.ceil(newDest.x) + ' ' +Math.ceil(newDest.y) + ' ' + speed + ' ' + speed2);
    
}else {
      print(Math.ceil(newDest.x) + ' ' +Math.ceil(newDest.y) + ' ' + speed );
    }
} 

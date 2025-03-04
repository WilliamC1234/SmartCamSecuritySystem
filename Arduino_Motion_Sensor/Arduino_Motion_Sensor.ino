int sensorPin = 2; // Define the pin connected to the motion sensor
int sensorState = LOW; // Variable to store the current sensor state (LOW = no motion, HIGH = motion) 

void setup() {
  pinMode(sensorPin, INPUT); // Set the sensor pin as input
  Serial.begin(9600); // Initialize serial communication
}

void loop() {
  int sensorState = digitalRead(sensorPin); // Read the sensor value
  
  if (sensorState == HIGH) { // If motion detected (transition from LOW to HIGH)
    Serial.println("Motion detected!");
    
    sensorState = HIGH; // Update state to reflect motion
    
  } else { // If no motion detected (transition from HIGH to LOW)
    Serial.println("No Motion."); 
    sensorState == LOW;
  }
  delay(250);
}
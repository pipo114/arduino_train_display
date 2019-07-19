// Adafruit SSD1306 Wemos Mini OLED - Version: Latest 
#include <Adafruit_SSD1306.h>

// Inspiré de : https://www.locoduino.org/spip.php?article205

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
#define OLED_RESET     1 // Reset pin # (or -1 if sharing Arduino reset pin)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
Adafruit_SSD1306 display2(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);


String inputString = "";
bool stringComplete = false;

  void setup () {
 
  Serial.begin(115200);
  inputString.reserve(500);
  
  display.begin(SSD1306_SWITCHCAPVCC, 0x3D);
  display.display();
  display.clearDisplay();

  display2.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display2.clearDisplay();

  Serial.println("Afficheur Pret."); 
}
 
void loop() {

  serialEvent();
  
  // print the string when a newline arrives:
  if (stringComplete) {

    display.clearDisplay();
    display.setTextSize(1);            
    display.setTextColor(WHITE);      
    display.setCursor(0,0);
    
    display2.clearDisplay();
    display2.setTextSize(1);            
    display2.setTextColor(WHITE);      
    display2.setCursor(0,0);

    // les départs et arrivees par un @
    String departs = getValue(inputString,'@',0);
    String arrivees = getValue(inputString,'@',1);

    Serial.println("Arrivees : ");
    Serial.println(arrivees);

    //arrivées
    // 8 lignes max séparées par des ;
    //récupération des ligne et écriture
    for (int i=0; i <= 8; i++){
        String ligne = getValue(arrivees,';',i);
        
        if(ligne != ""){
          Serial.println(ligne);
          display.println(ligne);
        }
      display.display();
    }


    Serial.println("Départs : ");
    Serial.println(departs);
    
    //departs
    //récupération des ligne et écriture
    // 8 lignes max séparées par des ;
    for (int i=0; i <= 8; i++){
        String ligne = getValue(departs,';',i);
        
        if(ligne != ""){
          Serial.println(ligne);
          display2.println(ligne);
        }
      display2.display();
    }
    

     // clear the string:
    inputString = "";
    stringComplete = false;
  } 
}

void serialEvent() {

    while (Serial.available()) {
      // get the new byte:
      char inChar = (char)Serial.read();
      // add it to the inputString:
      inputString += inChar;
        
      // if the incoming character is a newline, set a flag so the main loop can
      // do something about it:
      if (inChar == '\n') {
        Serial.println(inputString);
        stringComplete = true;
      }
    }
    
  
}


String getValue(String data, char separator, int index)
{
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length()-1;

  for(int i=0; i<=maxIndex && found<=index; i++){
    if(data.charAt(i)==separator || i==maxIndex){
        found++;
        strIndex[0] = strIndex[1]+1;
        strIndex[1] = (i == maxIndex) ? i+1 : i;
    }
  }

  return found>index ? data.substring(strIndex[0], strIndex[1]) : "";
}

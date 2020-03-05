#include "ADC-master/ADC.h"
#include "intobyte.hpp"
#include <array>
// ADC pin assignment for teensy 3.6:
// https://forum.pjrc.com/attachment.php?attachmentid=11811&d=1508341808
constexpr int pin_0 = A2; // A2 and A3 can either go to ADC0 or 1
constexpr int pin_1 = A3;

constexpr int parallel_pin = 14; // picked a random digital pin

ADC *adc = new ADC();

ADC::Sync_result result;
uint8_t digital_res = 0;
std::array<uint8_t, 64> output{}; // data to serial
auto iterator = output.begin();
elapsedMicros microseconds;

void setup()
{
  Serial.begin(9600);
  while (!Serial && (millis() < 10000))
    ;
  pinMode(pin_0, INPUT);
  pinMode(pin_1, INPUT);
  pinMode(parallel_pin, INPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  adc->adc0->setAveraging(8);
  adc->adc0->setResolution(12);
  adc->adc0->setConversionSpeed(ADC_CONVERSION_SPEED::HIGH_SPEED);
  adc->adc0->setSamplingSpeed(ADC_SAMPLING_SPEED::HIGH_SPEED);

  adc->adc1->setAveraging(8);
  adc->adc1->setResolution(12);
  adc->adc1->setConversionSpeed(ADC_CONVERSION_SPEED::HIGH_SPEED);
  adc->adc1->setSamplingSpeed(ADC_SAMPLING_SPEED::HIGH_SPEED);

  adc->startSynchronizedContinuous(pin_0, pin_1);
  delay(100);
  microseconds = 0;
}

uint32_t counter = 0;
void loop()
{
  while (microseconds < 100)
  {
  }
  microseconds = 0;
  digital_res = digitalReadFast(parallel_pin); // 1 byte
  result = adc->readSynchronizedContinuous();
  result.result_adc0 = result.result_adc0; // 2 bytes each
  result.result_adc1 = result.result_adc1; //
  intoByte(iterator, digital_res);
  intoByte(iterator, (uint16_t)result.result_adc0);
  intoByte(iterator, (uint16_t)result.result_adc1);
  counter += 1; // did a reading, add one
  if (counter >= 10)
  {
    //Serial.println(counter);
    Serial.write(output.data(), 64);
    Serial.send_now();
    iterator = output.begin();
    counter = 0;
    digitalWriteFast(LED_BUILTIN, !digitalReadFast(LED_BUILTIN));
  }
}
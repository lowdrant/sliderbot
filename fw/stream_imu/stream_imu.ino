/**
 * Stream MPU6050 to console. Code largely taken from Adafruit
 * example.
 */

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <string.h>

#define OUT_STR_LEN (100) /* should be sufficient to get all 6 floats */
#define FLOAT2INT(v) (((uint32_t)(v*1000)))
const int dtus = 10;

Adafruit_MPU6050 mpu;
char out[OUT_STR_LEN];
char fmt[] = "%d,%d,%d,%d,%d,%d\n";
sensors_event_t a, g, temp;

void setup(void) {
    Serial.begin(1000000);
    while (!Serial) delay(10);
    Serial.println("MPU6050 stream!");
    Serial.print("Fix pt=");
    Serial.println(FLOAT2INT(1));
    if (!mpu.begin()) {
        Serial.println("Failed to find MPU6050 chip");
        while (1) {
            delay(10);
        }
    }

    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    Serial.print("Accel range: ");
    switch (mpu.getAccelerometerRange()) {
    case MPU6050_RANGE_2_G:
        Serial.println("+-2G");
        break;
    case MPU6050_RANGE_4_G:
        Serial.println("+-4G");
        break;
    case MPU6050_RANGE_8_G:
        Serial.println("+-8G");
        break;
    case MPU6050_RANGE_16_G:
        Serial.println("+-16G");
        break;
    }
    mpu.setGyroRange(MPU6050_RANGE_500_DEG);
    Serial.print("Gyro range: ");
    switch (mpu.getGyroRange()) {
    case MPU6050_RANGE_250_DEG:
        Serial.println("+- 250 deg/s");
        break;
    case MPU6050_RANGE_500_DEG:
        Serial.println("+- 500 deg/s");
        break;
    case MPU6050_RANGE_1000_DEG:
        Serial.println("+- 1000 deg/s");
        break;
    case MPU6050_RANGE_2000_DEG:
        Serial.println("+- 2000 deg/s");
        break;
    }

    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    Serial.print("Bandwidth: ");
    switch (mpu.getFilterBandwidth()) {
    case MPU6050_BAND_260_HZ:
        Serial.println("260 Hz");
        break;
    case MPU6050_BAND_184_HZ:
        Serial.println("184 Hz");
        break;
    case MPU6050_BAND_94_HZ:
        Serial.println("94 Hz");
        break;
    case MPU6050_BAND_44_HZ:
        Serial.println("44 Hz");
        break;
    case MPU6050_BAND_21_HZ:
        Serial.println("21 Hz");
        break;
    case MPU6050_BAND_10_HZ:
        Serial.println("10 Hz");
        break;
    case MPU6050_BAND_5_HZ:
        Serial.println("5 Hz");
        break;
    }
    Serial.println("");
}

void loop() {
    mpu.getEvent(&a, &g, &temp);
    // Serial.println(a.acceleration.x);
    sprintf(out, fmt, FLOAT2INT(a.acceleration.x),
            FLOAT2INT(a.acceleration.y),
            FLOAT2INT(a.acceleration.z),
            FLOAT2INT(g.gyro.x), FLOAT2INT(g.gyro.y), FLOAT2INT(g.gyro.z)
        );
    Serial.print(out);
    delay(dtus);
}

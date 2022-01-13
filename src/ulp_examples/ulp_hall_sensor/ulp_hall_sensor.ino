#include "esp_sleep.h"
#include "soc/soc.h"
#include "soc/soc_ulp.h"
#include "driver/adc.h"
#include "esp32/ulp.h"
#include "ulp_main.h"
#include "ulptool.h"

extern const uint8_t ulp_main_bin_start[] asm("_binary_ulp_main_bin_start");
extern const uint8_t ulp_main_bin_end[]   asm("_binary_ulp_main_bin_end");

static void init_ulp_program()
{
  esp_err_t err = ulptool_load_binary(0, ulp_main_bin_start,
                                  (ulp_main_bin_end - ulp_main_bin_start) / sizeof(uint32_t));
  ESP_ERROR_CHECK(err);

  /* The ADC1 channel 0 input voltage will be reduced to about 1/2 */
  adc1_config_channel_atten(ADC1_CHANNEL_0, ADC_ATTEN_DB_6);
  /* The ADC1 channel 3 input voltage will be reduced to about 1/2 */
  adc1_config_channel_atten(ADC1_CHANNEL_3, ADC_ATTEN_DB_6);
  /* ADC capture 12Bit width */
  adc1_config_width(ADC_WIDTH_BIT_12);
  /* enable adc1 */
  adc1_ulp_enable();

  /* Set ULP wake up period to 3 S */
  ulp_set_wakeup_period(0, 3 * 1000 * 1000);
}

static void print_hall_sensor()
{
  Serial.printf("ulp_hall_sensor:Sens_Vp0:%d,Sens_Vn0:%d,Sens_Vp1:%d,Sens_Vn1:%d\r\n",
         (uint16_t)ulp_Sens_Vp0, (uint16_t)ulp_Sens_Vn0, (uint16_t)ulp_Sens_Vp1, (uint16_t)ulp_Sens_Vn1);
  Serial.printf("offset:%d\r\n",  ((uint16_t)ulp_Sens_Vp0 - (uint16_t)ulp_Sens_Vp1) - ((uint16_t)ulp_Sens_Vn0 - (uint16_t)ulp_Sens_Vn1));
}

void setup() {
  Serial.begin(115200);
  esp_sleep_wakeup_cause_t cause = esp_sleep_get_wakeup_cause();
  if (cause != ESP_SLEEP_WAKEUP_ULP) {
    Serial.printf("Not ULP wakeup, initializing ULP\n");
    init_ulp_program();
  } else {
    Serial.println("--------------------------------------------------------------------------");
    Serial.printf("ULP wakeup, printing hall sensor value\n");
    print_hall_sensor();
  }

  Serial.printf("Entering deep sleep\n\n");
  /* Start the ULP program */
  ESP_ERROR_CHECK( ulp_run(&ulp_entry - RTC_SLOW_MEM) );
  ESP_ERROR_CHECK( esp_sleep_enable_ulp_wakeup() );
  esp_deep_sleep_start();
}

void loop() {
  // not used
}

#include "esp_sleep.h"
#include "driver/rtc_io.h"
#include "driver/adc.h"
#include "esp32/ulp.h"
#include "ulp_main.h"
#include "ulptool.h"
#include "common.h"

extern const uint8_t ulp_main_bin_start[] asm("_binary_ulp_main_bin_start");
extern const uint8_t ulp_main_bin_end[]   asm("_binary_ulp_main_bin_end");

static void init_ulp_program();

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("ULP Light Sleep adc threshold wakeup example");
  delay(100);
  // wake ulp every 10 msec
  init_run_ulp(1000 * 10);
  ESP_ERROR_CHECK( esp_sleep_enable_ulp_wakeup() );
}

void loop() {
  // light sleep until adc thershold is exceeded
  esp_light_sleep_start();
  // check for the ulp is waiting for the main processor to read the adc result
  if (ulp_mutex) {
    Serial.printf("counter: %4i | oversample factor: %3i | adc avg: %i\n",
                  ulp_sample_counter & 0xffff,
                  adc_oversampling_factor,
                  ulp_adc_avg_result & 0xffff
                 );
    Serial.flush();
    // tell ulp we are done reading result
    ulp_mutex = false;
  }
}

static void init_run_ulp(uint32_t usec) {
  adc1_config_channel_atten(ADC1_CHANNEL_6, ADC_ATTEN_DB_0);
  adc1_config_width(ADC_WIDTH_BIT_12);
  adc1_ulp_enable();
  //rtc_gpio_pullup_dis(GPIO_NUM_15);
  //rtc_gpio_hold_en(GPIO_NUM_15);
  ulp_set_wakeup_period(0, usec);
  esp_err_t err = ulptool_load_binary(0, ulp_main_bin_start, (ulp_main_bin_end - ulp_main_bin_start) / sizeof(uint32_t));
  // all shared ulp variables have to be intialized after ulptool_load_binary for the ulp to see it.
  // Set the high threshold reading you want the ulp to trigger a main processor wakeup.
  ulp_threshold = 0x20;
  err = ulp_run((&ulp_entry - RTC_SLOW_MEM) / sizeof(uint32_t));
  if (err) Serial.println("Error Starting ULP Coprocessor");
}

#include "esp32/ulp.h"
// include ulp header you will create
#include "ulp_main.h"
// must include ulptool helper functions also
#include "ulptool.h"

// Unlike the esp-idf always use these binary blob names
extern const uint8_t ulp_main_bin_start[] asm("_binary_ulp_main_bin_start");
extern const uint8_t ulp_main_bin_end[]   asm("_binary_ulp_main_bin_end");

static void init_run_ulp(uint32_t usec);

void setup() {
  Serial.begin(115200);
  delay(1000);
  init_run_ulp(100 * 1000); // 100 msec
}

void loop() {
  // ulp variables are 32-bit but only the bottom 16-bits hold data
  Serial.printf("Count: %i\n", ulp_counter & 0xFFFF);
  delay(100);
}

static void init_run_ulp(uint32_t usec) {
  ulp_set_wakeup_period(0, usec);
  esp_err_t err = ulptool_load_binary(0, ulp_main_bin_start, (ulp_main_bin_end - ulp_main_bin_start) / sizeof(uint32_t));
  err = ulp_run((&ulp_entry - RTC_SLOW_MEM) / sizeof(uint32_t));
  
  if (err) Serial.println("Error Starting ULP Coprocessor");
}

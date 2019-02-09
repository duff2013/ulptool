/*
        ulp_Blink by Vincent STRAGIER (9 february 2019)

        Inpired from the JoBa1 Blink-ULP project (https://github.com/joba-1/Blink-ULP)
        and from duff2013 ulptool repository (https://github.com/duff2013/ulptool)
        Pinout equivalance for RTC GPIO (https://i1.wp.com/randomnerdtutorials.com/wp-content/uploads/2018/08/ESP32-DOIT-DEVKIT-V1-Board-Pinout-36-GPIOs-updated.jpg?ssl=1)
        (See ulp.s comments)
        Useful documentation: https://docs.espressif.com/projects/esp-idf/en/latest/api-guides/ulp.html

*/

#include "esp32/ulp.h"
#include "ulp_main.h"   // include ulp header you will create
#include "esp_sleep.h"  // esp_sleep_enable_ulp_wakeup(), esp_deep_sleep_start()

static void init_run_ulp(void);

void setup() {
  init_run_ulp();
}

void loop() {}

static void init_run_ulp(void) {
  // Initialiaze ULP
  esp_err_t err = ulp_load_binary(0, ulp_main_bin_start, (ulp_main_bin_end - ulp_main_bin_start) / sizeof(uint32_t));

  // ULP coprocessor will run on its own now
  err = ulp_run((&ulp_entry - RTC_SLOW_MEM) / sizeof(uint32_t));

  if (err)  {
    Serial.begin(115200);
    Serial.println("Error Starting ULP Coprocessor");
  }

  ESP_ERROR_CHECK( esp_sleep_enable_ulp_wakeup() );
  esp_deep_sleep_start();
}

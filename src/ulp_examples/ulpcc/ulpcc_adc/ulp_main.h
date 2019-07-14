/*
    Put your ULP globals here you want visibility
    for your sketch. Add "ulp_" to the beginning
    of the variable name and must be size 'uint32_t'
*/
#include "Arduino.h"

extern uint32_t ulp_entry;
extern uint32_t ulp_adc_avg_result;
extern uint32_t ulp_sample_counter;
extern uint32_t ulp_threshold;
extern uint32_t ulp_mutex;

#ifdef _ULPCC_ // do not add code above this line
// must include ulpcc helper functions
#include <ulp_c.h>
#include "common.h"

// ADC1 channel 6, GPIO34
#define adc_channel 6

// threshold of ADC reading. Set by the main program.
unsigned threshold;
/*
 * esp32 main processor can reach this variable.
 * It is used to signal that a result is ready
 * and when the main processor read the value.
 */
unsigned mutex = 0;

// # of samples
unsigned sample_counter = 0;
/*
 * ulp registers are 32 bits but can
 * only hold 16 bits of data. We use
 * sum_hi (upper 16-bits) and sum_lo
 * (lower 16-bits) to hold 32 bits
 * of data. The averaged data is computed
 * from this proto 32-bit number.
 */
unsigned sum_lo = 0;
unsigned sum_hi = 0;
unsigned adc_avg_result = 0;

void entry() {
  unsigned tmp = 0, i = 0;
  sum_hi = 0;
  sum_lo = 0;
  // avg routine
  for (i = 0; i < adc_oversampling_factor; i++) {
    // get adc reading
    tmp = adc(0, adc_channel + 1);
    //check if sum_lo + tmp will overflow
    if (tmp > (0xFFFF - sum_lo)) {
      // update the high 16 bits
      sum_hi += 1;
    }
    // update low 16 bits
    sum_lo += tmp;
  }
  // calculate get average from the proto 32 bit number
  adc_avg_result = (sum_hi << 10) + (sum_lo >> 6);

  // if adc_avg_result is greater than threshold signal main processor
  if (adc_avg_result > threshold) {
    sample_counter++;
    mutex = 1;
    wake();
    // wait until main processor has read the result
    while (mutex);
  }
}
#endif // do not add code after here

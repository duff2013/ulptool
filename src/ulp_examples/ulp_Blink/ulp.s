#include "soc/soc_ulp.h"     // for WRITE_RTC_REG
#include "soc/rtc_io_reg.h"  // for RTC_GPIO_*

/*
 *    GPIO - RTC_GPIO  -  DIRECTION
 *     0        11       Input-Output
 *     2        12       Input-Output
 *     4        10       Input-Output
 *     12       15       Input-Output
 *     13       14       Input-Output
 *     14       16       Input-Output
 *     15       13       Input-Output
 *     25       6        Input-Output
 *     26       7        Input-Output
 *     27       17       Input-Output
 *     32       9        Input-Output
 *     33       8        Input-Output
 *     34       4        Input only
 *     35       5        Input only
 *     36       0        Input only
 *     39       3        Input only
 */
 
/* Define variables, which go into .bss section (zero-initialized data) */
.bss

/* Set gpio */
.set gpio_2, 12

/* Code goes into .text section */
.text
.global entry

/* First instruction adress (entry) */
entry:
  // use digital function, not rtc function
  WRITE_RTC_REG(RTC_IO_TOUCH_PAD2_REG, RTC_IO_TOUCH_PAD2_MUX_SEL_S, 1, 1)

  // gpio_2 shall be output, not input
  WRITE_RTC_REG(RTC_GPIO_OUT_REG, RTC_GPIO_OUT_DATA_S + gpio_2, 1, 1)

on:
  WRITE_RTC_REG(RTC_GPIO_ENABLE_W1TS_REG, RTC_GPIO_ENABLE_W1TS_S + gpio_2, 1, 1)

  move  r1, 1000          // wait in ms
  move  r2, off           // return address
  jump  delay             // call subroutine

off:
  WRITE_RTC_REG(RTC_GPIO_ENABLE_W1TC_REG, RTC_GPIO_ENABLE_W1TC_S + gpio_2, 1, 1)

  move  r1, 1000          // wait in ms
  move  r2, on            // return address
  jump  delay             // call subroutine

delay:
  wait  8000              // wait 8000 clock ticks at 8MHz -> 1ms
  sub   r1, r1, 1         // decrement ms count
  jump  r2, eq            // if ms count is zero then return to caller
  jump  delay             // else continue to wait

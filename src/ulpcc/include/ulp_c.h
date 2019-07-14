/* Header file for pseudo-functions that the compiler will convert to assembler instructions */

/* This simplifies what the following headers pull in */
#define __ASSEMBLER__

#include "soc/rtc_cntl_reg.h"
#include "soc/rtc_io_reg.h"
#include "soc_ulp_c.h"

unsigned adc(unsigned sar_sel, unsigned mux);
void     halt();
void     i2c_rd(unsigned sub_addr, unsigned high, unsigned low, unsigned slave_sel);
unsigned i2c_wr(unsigned sub_addr, unsigned value, unsigned high, unsigned low, unsigned slave_sel);
unsigned reg_rd(unsigned addr, unsigned high, unsigned low);
void     reg_wr(unsigned addr, unsigned high, unsigned low, unsigned data);
void     sleep(unsigned sleep_reg);
unsigned tsens(unsigned wait_delay);
void     wait(unsigned cycles);
void     wake();
#define  wake_when_ready() do {while (0 == (READ_RTC_FIELD(RTC_CNTL_LOW_POWER_ST_REG, RTC_CNTL_RDY_FOR_WAKEUP) & 1)); wake(); halt();} while(0)


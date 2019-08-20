#ifdef _ULPCC_ // do not add code above this line
// must include ulpcc helper functions
#include <ulp_c.h>

// global variable that the main processor can see
unsigned counter = 0;

// all ulpcc programs have have this function
void entry() {
  // increment counter
  counter++;
}
#endif // do not add code after here

/* Define variables, which go into .bss section (zero-initialized data) */
    .data
/* Store count value */
    .global count
count:
    .long 0
/* Code goes into .text section */
    .text
    .global entry
entry:
    move    r3, count
    ld      r0, r3, 0
    add     r0, r0, 1
    st      r0, r3, 0
    halt

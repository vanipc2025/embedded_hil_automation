#ifndef HIL_LED_CONTROL_H
#define HIL_LED_CONTROL_H

#include <stdbool.h>

/*
 * Vendor-independent logical LED interface used by the JSON command handler.
 * Indices are 1-based (LED1 = 1), matching Robot Framework keywords.
 * Return 0 on success, negative errno on failure.
 */
int led_control_init(void);
int led_control_count(void);
int led_control_set(int index, bool on);
int led_control_get(int index, bool *on);

#endif /* HIL_LED_CONTROL_H */

/*
 * Zephyr LED driver: physical pins come from each board's devicetree aliases.
 * Only led0..led3 are considered in Phase 1. A board with fewer aliases builds
 * with fewer LEDs; a board with more needs an intentional extension here.
 *
 * IMPORTANT: gpio_pin_get_dt() did not reliably reflect commanded output in
 * our initial nRF52840 experiment. LED_GET intentionally reports the LAST
 * SUCCESSFULLY COMMANDED state, not an independent electrical measurement.
 */
#include "led_control.h"

#include <errno.h>
#include <stddef.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/sys/util.h>

#define HIL_LED_AVAILABLE(n) \
    (DT_NODE_EXISTS(DT_ALIAS(led##n)) && DT_NODE_HAS_STATUS(DT_ALIAS(led##n), okay))

/* Aliases must be contiguous for 1-based indexing to be intuitive. */
#if !HIL_LED_AVAILABLE(0)
#error "No usable led0 devicetree alias; add board overlay or LED driver"
#endif

static const struct gpio_dt_spec leds[] = {
    GPIO_DT_SPEC_GET(DT_ALIAS(led0), gpios),
#if HIL_LED_AVAILABLE(1)
    GPIO_DT_SPEC_GET(DT_ALIAS(led1), gpios),
#endif
#if HIL_LED_AVAILABLE(2)
    GPIO_DT_SPEC_GET(DT_ALIAS(led2), gpios),
#endif
#if HIL_LED_AVAILABLE(3)
    GPIO_DT_SPEC_GET(DT_ALIAS(led3), gpios),
#endif
};

#define HIL_LED_COUNT ARRAY_SIZE(leds)
static bool led_states[HIL_LED_COUNT];

int led_control_init(void)
{
    for (size_t i = 0; i < HIL_LED_COUNT; ++i) {
        if (!gpio_is_ready_dt(&leds[i])) {
            return -ENODEV;
        }
        int result = gpio_pin_configure_dt(&leds[i], GPIO_OUTPUT_INACTIVE);
        if (result != 0) {
            return result;
        }
        led_states[i] = false;
    }
    return 0;
}

int led_control_count(void)
{
    return (int)HIL_LED_COUNT;
}

int led_control_set(int index, bool on)
{
    if (index < 1 || index > (int)HIL_LED_COUNT) {
        return -EINVAL;
    }
    int result = gpio_pin_set_dt(&leds[index - 1], on ? 1 : 0);
    if (result == 0) {
        led_states[index - 1] = on;
    }
    return result;
}

int led_control_get(int index, bool *on)
{
    if (index < 1 || index > (int)HIL_LED_COUNT || on == NULL) {
        return -EINVAL;
    }
    *on = led_states[index - 1];
    return 0;
}

/*
 * Minimal nRF/Zephyr JSON-lines firmware for Python + Robot Framework HIL.
 * Verified architecture on nRF52840 DK: J-Link CDC UART at 115200 baud.
 *
 * WHY BUSY POLLING? An earlier receive loop used k_msleep(1) while waiting
 * for bytes. At 115200 baud that lost characters and corrupted JSON commands.
 * This phase intentionally uses uart_poll_in() without sleeping. It consumes
 * CPU; migrate to interrupt-driven UART/ring buffer for production firmware.
 *
 * JSON support is intentionally narrow: fixed ASCII keys and scalar values
 * produced by Python json.dumps(). It is NOT a general-purpose JSON parser.
 * Future protocol growth should use a proper parser and input validation.
 */
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/uart.h>

#include "led_control.h"

#ifndef HIL_BOARD_ID
#define HIL_BOARD_ID "unknown_zephyr_board"
#endif

#define RX_LINE_MAX 256
static const struct device *const uart = DEVICE_DT_GET(DT_CHOSEN(zephyr_console));

static void send_line(const char *text)
{
    while (*text != '\0') {
        uart_poll_out(uart, (unsigned char)*text++);
    }
    uart_poll_out(uart, '\n');
}

/* Locate an exact JSON key followed by a colon. Values may contain spaces. */
static const char *value_for_key(const char *json, const char *key)
{
    char needle[40];
    if (snprintf(needle, sizeof(needle), "\"%s\"", key) >= sizeof(needle)) {
        return NULL;
    }
    const char *p = strstr(json, needle);
    if (p == NULL) {
        return NULL;
    }
    p += strlen(needle);
    while (*p == ' ' || *p == '\t') { ++p; }
    if (*p++ != ':') { return NULL; }
    while (*p == ' ' || *p == '\t') { ++p; }
    return p;
}

static bool string_equals(const char *value, const char *expected)
{
    if (value == NULL || *value != '"') { return false; }
    size_t n = strlen(expected);
    return strncmp(value + 1, expected, n) == 0 && value[n + 1] == '"';
}

static bool parse_index(const char *json, int *index)
{
    const char *p = value_for_key(json, "index");
    if (p == NULL || *p < '0' || *p > '9') { return false; }
    char *end;
    long n = strtol(p, &end, 10);
    if (end == p || n < 1 || n > 100) { return false; }
    *index = (int)n;
    return true;
}

static void handle_request(const char *line)
{
    const char *cmd = value_for_key(line, "cmd");
    char reply[128];
    if (string_equals(cmd, "STATUS")) {
        send_line("{\"status\":\"READY\"}");
    } else if (string_equals(cmd, "IDENTITY")) {
        snprintf(reply, sizeof(reply),
                 "{\"board\":\"%s\",\"firmware\":\"hil-serial-v2\",\"backend\":\"serial\"}",
                 HIL_BOARD_ID);
        send_line(reply);
    } else if (string_equals(cmd, "CAPABILITIES")) {
        snprintf(reply, sizeof(reply),
                 "{\"led_count\":%d,\"features\":[\"gpio\"]}",
                 led_control_count());
        send_line(reply);
    } else if (string_equals(cmd, "LED_SET")) {
        int index;
        const char *on = value_for_key(line, "on");
        if (!parse_index(line, &index) || on == NULL ||
            (strncmp(on, "true", 4) != 0 && strncmp(on, "false", 5) != 0)) {
            send_line("{\"error\":\"invalid LED_SET arguments\"}");
            return;
        }
        bool state = strncmp(on, "true", 4) == 0;
        if (led_control_set(index, state) != 0) {
            send_line("{\"error\":\"LED_SET failed or index out of range\"}");
        } else {
            send_line("{\"ok\":true}");
        }
    } else if (string_equals(cmd, "LED_GET")) {
        int index;
        bool on;
        if (!parse_index(line, &index) || led_control_get(index, &on) != 0) {
            send_line("{\"error\":\"LED_GET failed or index out of range\"}");
        } else {
            send_line(on ? "{\"on\":true}" : "{\"on\":false}");
        }
    } else {
        send_line("{\"error\":\"unsupported command\"}");
    }
}

int main(void)
{
    if (!device_is_ready(uart)) { return 1; }
    if (led_control_init() != 0) { return 1; }

    char line[RX_LINE_MAX];
    size_t used = 0;
    unsigned char ch;
    for (;;) {
        if (uart_poll_in(uart, &ch) != 0) {
            continue; /* DO NOT add k_msleep(1): serial bytes were lost. */
        }
        if (ch == '\r') { continue; }
        if (ch == '\n') {
            if (used > 0) {
                line[used] = '\0';
                handle_request(line);
                used = 0;
            }
        } else if (used < sizeof(line) - 1) {
            line[used++] = (char)ch;
        } else {
            /* Drop oversized line; report failure and resync at next newline. */
            used = 0;
            send_line("{\"error\":\"request too long\"}");
        }
    }
    return 0;
}

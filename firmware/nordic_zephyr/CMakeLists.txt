cmake_minimum_required(VERSION 3.20.0)
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(embedded_hil_automation)

# Keep protocol/transport in main.c; LED-specific Zephyr GPIO in led_control.c.
target_sources(app PRIVATE src/main.c src/led_control.c)

# Identity is explicit so Python can reject a mismatched connected board.
# nRF54L15 support is NOT validated yet; add its board-specific settings later.
if(BOARD MATCHES "nrf52840dk")
  target_compile_definitions(app PRIVATE HIL_BOARD_ID=\"nrf52840dk\")
elseif(BOARD MATCHES "nrf54l15dk")
  target_compile_definitions(app PRIVATE HIL_BOARD_ID=\"nrf54l15dk\")
else()
  target_compile_definitions(app PRIVATE HIL_BOARD_ID=\"unknown_zephyr_board\")
endif()

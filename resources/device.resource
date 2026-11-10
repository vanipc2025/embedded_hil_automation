*** Settings ***
# Robot variables can be overridden on the command line, per test run.
Library    ../libraries/DeviceLibrary.py    ${BOARD}    ${BACKEND}    ${PORT}

*** Variables ***
${BOARD}      nrf52840dk
${BACKEND}    sim
${PORT}       ${EMPTY}

*** Keywords ***
Require Device Feature
    [Documentation]    Skip only when feature is not advertised; broken advertised features must FAIL.
    [Arguments]    ${feature}
    ${supported}=    Device Supports    ${feature}
    IF    not ${supported}
        Skip    Feature '${feature}' is not available in this firmware/backend
    END

Require Simulator For Button Injection
    [Documentation]    Hardware buttons cannot be pressed by software without a fixture.
    IF    '${BACKEND}' != 'sim'
        Skip    Button injection requires simulator or an external physical actuator
    END

Require Simulator Backend
    [Documentation]    Protect simulator-only negative tests from physical hardware.
    IF    '${BACKEND}' != 'sim'
        Fail    Simulator-only suite requires BACKEND:sim; do not send these commands to a DK
    END

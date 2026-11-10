*** Settings ***
Documentation    Phase 1: physical nRF52840 DK UART and onboard LED verification.
...              Run with BACKEND:serial and PORT:<actual port>. Do not run against sim.
Resource         ../../resources/device.resource
Suite Setup      Connect To Device
Suite Teardown   Disconnect From Device

*** Test Cases ***
Verify Real Firmware Identity
    [Tags]    hardware    smoke    firmware
    Should Be Equal As Strings    ${BACKEND}    serial
    ${identity}=    Get Firmware Identity
    Should Be Equal As Strings    ${identity}[board]    nrf52840dk
    Should Be Equal As Strings    ${identity}[backend]    serial
    Log    Firmware identity: ${identity}    console=True

Toggle Every Advertised Physical LED
    [Tags]    hardware    smoke    gpio
    Should Be Equal As Strings    ${BACKEND}    serial
    Require Device Feature    gpio
    ${count}=    Get LED Count
    Should Be True    ${count} > 0
    Log    Firmware advertises ${count} LED(s)    console=True
    FOR    ${index}    IN RANGE    1    ${count + 1}
        Set LED State    ${index}    ${True}
        ${on}=    Get LED State    ${index}
        Should Be True    ${on}
        Log    Visually inspect LED${index}: ON for 2 seconds    console=True
        Sleep    2s
        Set LED State    ${index}    ${False}
        ${off}=    Get LED State    ${index}
        Should Not Be True    ${off}
        Sleep    0.3s
    END

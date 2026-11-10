*** Settings ***
Documentation    Common smoke checks; works with simulator and compatible serial firmware.
Resource         ../../resources/device.resource
Suite Setup      Connect To Device
Suite Teardown   Disconnect From Device

*** Test Cases ***
Device Reports Ready
    [Tags]    smoke    firmware    regression
    ${status}=    Get Device Status
    Should Be Equal As Strings    ${status}    READY

Firmware Identity Matches Selected Board
    [Tags]    smoke    firmware    regression
    ${identity}=    Get Firmware Identity
    Should Be Equal As Strings    ${identity}[board]    ${BOARD}

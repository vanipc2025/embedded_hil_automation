*** Settings ***
Documentation    Generic GPIO tests; use firmware-advertised LED count, not a fixed board count.
Resource         ../../resources/device.resource
Suite Setup      Connect To Device
Suite Teardown   Disconnect From Device

*** Test Cases ***
LED Count Is Positive
    [Tags]    gpio    regression    conditional
    Require Device Feature    gpio
    ${count}=    Get LED Count
    Should Be True    ${count} > 0

Toggle All Available LEDs
    [Tags]    gpio    regression    conditional
    Require Device Feature    gpio
    ${count}=    Get LED Count
    FOR    ${index}    IN RANGE    1    ${count + 1}
        Set LED State    ${index}    ${True}
        ${on}=    Get LED State    ${index}
        Should Be True    ${on}
        Set LED State    ${index}    ${False}
        ${off}=    Get LED State    ${index}
        Should Not Be True    ${off}
    END

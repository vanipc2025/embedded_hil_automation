*** Settings ***
Documentation     Educational, simulator-only examples of IF/ELSE, TRY/EXCEPT,
...               FOR, tagging, and recovery after expected invalid requests.
...               These tests do NOT demonstrate physical button or BLE hardware.
Resource          ../../resources/device.resource
Suite Setup       Connect To Device
Suite Teardown    Disconnect From Device
Test Setup        Require Simulator Backend

*** Test Cases ***
Capability Branch Logs Supported Path
    [Documentation]    Explicit IF/ELSE; unknown features must not be treated as supported.
    [Tags]    simulator    conditional    regression
    ${supported}=    Device Supports    gpio
    IF    ${supported}
        Log    GPIO advertised; proceed with tests    console=True
    ELSE
        Fail    Simulator profile unexpectedly lacks GPIO
    END

Capability Branch Logs Unsupported Path
    [Documentation]    ELSE branch is expected for a deliberately absent feature.
    [Tags]    simulator    conditional    regression
    ${supported}=    Device Supports    imaginary_peripheral
    IF    ${supported}
        Fail    Simulator unexpectedly advertised imaginary_peripheral
    ELSE
        Log    Optional imaginary_peripheral absent; ELSE branch exercised    console=True
    END

Simulator Buttons Press And Release
    [Documentation]    Simulate press/release; this does not press a real DK button.
    [Tags]    simulator    buttons    regression
    FOR    ${index}    IN RANGE    1    5
        Inject Button Press    ${index}    ${True}
        ${pressed}=    Get Button State    ${index}
        Should Be True    ${pressed}
        Inject Button Press    ${index}    ${False}
        ${released}=    Get Button State    ${index}
        Should Not Be True    ${released}
    END

BLE Scan Does Not Find Unknown Advertiser
    [Documentation]    Negative BLE simulator test; not a real radio scan.
    [Tags]    simulator    ble    regression
    ${found}=    Find BLE Device    NOT_A_SIM_DEVICE
    Should Not Be True    ${found}

Expected Invalid LED Index Is Caught
    [Documentation]    TRY/EXCEPT catches only a known negative-input error.
    ...                Unexpected error types and successful invalid requests FAIL.
    [Tags]    simulator    gpio    negative    conditional
    ${count}=    Get LED Count
    ${invalid}=    Evaluate    ${count} + 1
    TRY
        Set LED State    ${invalid}    ${True}
    EXCEPT    *outside 1..*    type=GLOB
        Log    Expected invalid-index rejection was received    console=True
    ELSE
        Fail    Invalid LED index was unexpectedly accepted
    END

Device Recovers After Expected Error
    [Documentation]    Expected failure must not prevent later valid operations.
    [Tags]    simulator    gpio    negative    regression
    TRY
        Get LED State    0
    EXCEPT    *outside 1..*    type=GLOB
        Log    Expected invalid index; checking recovery    console=True
    ELSE
        Fail    LED index 0 was unexpectedly accepted
    END
    Set LED State    1    ${True}
    ${on}=    Get LED State    1
    Should Be True    ${on}
    Set LED State    1    ${False}
    ${off}=    Get LED State    1
    Should Not Be True    ${off}

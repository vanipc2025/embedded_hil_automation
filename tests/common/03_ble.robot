*** Settings ***
Documentation    Simulator BLE behavior only until a real BLE firmware backend is implemented.
Resource         ../../resources/device.resource
Suite Setup      Connect To Device
Suite Teardown   Disconnect From Device

*** Test Cases ***
Find Simulated BLE Advertiser
    [Tags]    ble    simulator    regression
    Require Device Feature    ble
    ${found}=    Find BLE Device    HIL_SIM_DEVICE
    Should Be True    ${found}

Read Simulated BLE RSSI
    [Tags]    ble    simulator    regression
    Require Device Feature    ble
    ${rssi}=    Read BLE RSSI
    Should Be True    -127 <= ${rssi} <= 20

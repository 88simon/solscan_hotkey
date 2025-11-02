#Requires AutoHotkey v2.0

; Test script to see what button presses AutoHotkey receives

XButton1::
{
    ToolTip "XButton1 pressed!"
    SetTimer () => ToolTip(), -2000
}

XButton2::
{
    ToolTip "XButton2 pressed!"
    SetTimer () => ToolTip(), -2000
}

~LButton::
{
    ToolTip "Left Mouse Button pressed!"
    SetTimer () => ToolTip(), -2000
}

~RButton::
{
    ToolTip "Right Mouse Button pressed!"
    SetTimer () => ToolTip(), -2000
}

; Show any key press
~*::
{
    ToolTip "Key pressed: " A_ThisHotkey
    SetTimer () => ToolTip(), -2000
}
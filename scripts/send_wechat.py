#!/usr/bin/env python3
"""Send WeChat message - reliable version using UIA + keyboard."""
import sys, time, pyautogui, pyperclip, uiautomation as auto

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3

def send_wechat(contact, message):
    wx = auto.WindowControl(searchDepth=1, Name='\u5fae\u4fe1')
    if not wx.Exists(maxSearchSeconds=2):
        print('WeChat not found'); return False
    wx.SwitchToThisWindow()
    time.sleep(0.8)

    r = wx.BoundingRectangle
    left, top, right, bottom = r.left, r.top, r.right, r.bottom

    # Click search bar
    pyautogui.click(left + 100, top + 40)
    time.sleep(0.4)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)

    # Paste contact name (supports Chinese)
    pyperclip.copy(contact)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.8)

    # Click first result
    pyautogui.click(left + 120, top + 100)
    time.sleep(0.5)

    # Click input area (double click for focus)
    input_x = left + (right-left)//2 + 50
    input_y = bottom - 60
    pyautogui.click(input_x, input_y)
    time.sleep(0.2)
    pyautogui.click(input_x, input_y)
    time.sleep(0.3)

    # Paste message (supports Chinese)
    pyperclip.copy(message)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.3)
    pyautogui.press('enter')

    print(f'Sent to {contact}')
    return True

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python send_wechat.py "contact" "message"')
        sys.exit(1)
    send_wechat(sys.argv[1], sys.argv[2])

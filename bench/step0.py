# Bench test step 0 (docs/firmware/output_driver.md): MicroPython, the 14 outputs sent one
# after another, with the access point up and a phone loading it.
#
# One strip is touched to each pin in turn. Statue 1's pins show T1-T7 in the test colours
# (red, orange, yellow, green, cyan, blue, magenta); statue 2's pins show the same colours on
# every other LED only, so each of the 14 pins looks different.
#
# Run: mpremote cp bench/step0.py :main.py, then reset. Phone: join "bench-step0" (open); the
# page opens by itself as the network's sign-in page (as WLED's does: every DNS name answers
# with this board), or open http://192.168.4.1. Leave it open; it fetches as fast as it can.

import machine
import neopixel
import network
import socket
import time

PINS = [4, 13, 14, 16, 17, 18, 19,  # S1-T1 ... S1-T7
        21, 22, 23, 25, 26, 27, 32]  # S2-T1 ... S2-T7
LEDS = 60
LEVEL = 40  # of 255; one strip at this level stays well under 1 A
COLOURS = [(1, 0, 0), (1, 0.5, 0), (1, 1, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1), (1, 0, 1)]

strips = []
for i, pin in enumerate(PINS):
    np = neopixel.NeoPixel(machine.Pin(pin, machine.Pin.OUT), LEDS)
    r, g, b = COLOURS[i % 7]
    colour = (int(r * LEVEL), int(g * LEVEL), int(b * LEVEL))
    for led in range(LEDS):
        np[led] = colour if i < 7 or led % 2 == 0 else (0, 0, 0)
    strips.append(np)

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="bench-step0", authmode=network.AUTH_OPEN)
ap.ifconfig(("192.168.4.1", "255.255.255.0", "192.168.4.1", "192.168.4.1"))

fps = 0.0
requests = 0
PAGE = (b"HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n"
        b"<!doctype html><meta name=viewport content='width=device-width'>"
        b"<h2 id=s>connecting</h2><script>"
        b"async function go(){for(;;){try{const r=await fetch('/s');"
        b"document.getElementById('s').textContent=(await r.text()).slice(0,60)}catch(e){}}}go()"
        b"</script>")
PADDING = b" " * 4000  # keeps the radio busy, as WLED's live preview does


# Served from the LED loop between frames.
srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("0.0.0.0", 80))
srv.listen(4)
srv.setblocking(False)


dns = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dns.bind(("0.0.0.0", 53))
dns.setblocking(False)


def answer_dns():
    # Every name resolves to this board, so the phone's internet check gets the page and the
    # phone shows it as the sign-in page.
    try:
        q, addr = dns.recvfrom(512)
    except OSError:
        return
    end = 12
    while end < len(q) and q[end]:
        end += q[end] + 1
    end += 5  # zero byte, type, class
    dns.sendto(q[:2] + b"\x81\x80" + q[4:6] + b"\x00\x01\x00\x00\x00\x00" + q[12:end]
               + b"\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04\xc0\xa8\x04\x01", addr)


def serve():
    global requests
    try:
        c, _ = srv.accept()
    except OSError:
        return
    c.settimeout(0.5)
    try:
        if c.recv(512).startswith(b"GET /s"):
            requests += 1
            c.send(b"HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\n")
            c.send(b"%.1f fps, %d requests " % (fps, requests))
            c.send(PADDING)
        else:
            c.send(PAGE)
    except OSError:
        pass
    c.close()


frames = 0
t0 = time.ticks_ms()
while True:
    for np in strips:
        np.write()
    answer_dns()
    serve()
    frames += 1
    if frames % 200 == 0:
        t1 = time.ticks_ms()
        fps = 200000 / time.ticks_diff(t1, t0)
        t0 = t1
        print("%.1f fps, %d requests" % (fps, requests))

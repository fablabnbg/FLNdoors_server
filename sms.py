from serial import Serial
def sms(modem_device,tel,message):
	s=Serial(modem_device)
	s.write('AT+CMGF=1\r\n'.encode('ascii'))
	s.write('AT+CMGS="{}"\r\n'.format(tel).encode('ascii'))
	s.write(message.encode('ascii'))
	s.write(b'\x1a')
	s.close()


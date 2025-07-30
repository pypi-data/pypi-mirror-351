import validators

def is_even(num: int):
	if not isinstance(num, int):
		raise Exception("Invalid num: ", num)
	return num % 2 == 0
		
def is_odd(num: int):
	if not isinstance(num, int):
		raise Exception("Invalid num: ", num)
	return num % 2 != 0
		
		
def is_even_or_odd(num: int):
	if not isinstance(num, int):
		raise Exception("Invalid num: ", num)
	return "Even" if num % 2 == 0 else "Odd"


def is_url_valid(url: int):
	if not isinstance(url, str):
		raise Exception("Invalid input url. Expected a string")
	if not validators.url(url):
		return "Invalid"
	return "Valid"

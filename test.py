import googletrans 
from googletrans import Translator

print(googletrans.LANGUAGES)
translator = Translator()

result = translator.translate('मुंबई कसाकाय मुंबई नमस्कार तुम्ही कसे आहात', dest ='en')
print(result.src)
print(result.dest)
print(result.origin)
print(result.text)
print(result.pronunciation)
a = 10
b = 2

print(a+b)
"""
Esta solução necessita de:
	- conta de serviço do google com autorização para realização de requisições ao google-cloud-speech
	- usuario autenticado com a conta acima (gcloud auth login --key-file=key.json)
	- pacote ffmpeg
	- pacote google-cloud-sdk (gcloud)
	- pacotes python google-cloud, google-cloud-speech, atualizados
"""
# session = r.Session()
#
# session.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36'})
#
# response = session.get("https://processual.trf1.jus.br/consultaProcessual/parte/listarPorCpfCnpj.php?cpf_cnpj=0123456789&secao=AC&mostrarBaixados=S&pg=5&enviar=Pesquisar")
#
# soup=bs(response.text,"html5lib")
#
# soundurl = regex.search("file=(.+?)&",soup.select("#ouvir_codigo")[0]['onclick']).group(1)
#
# response = session.get("https://processual.trf1.jus.br"+soundurl)
#
# with open("sound.mp3",'wb') as soundfile:
# 	for c in response.iter_content(chunk_size=128):
# 		if c:
# 			soundfile.write(c)
#
# # converte mp3 para wav. -> apt install ffmpeg
# subprocess.call(['ffmpeg','-i','sound.mp3','-ac','1','-ar','16000','sound.wav'])
#
# client = speech.SpeechClient()
#
# with open("sound.wav", "rb") as audio_file:
# 	content = audio_file.read()
#
# audio = types.RecognitionAudio(content=content)
#
# config = types.RecognitionConfig(
# 		encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
# 		sample_rate_hertz=16000,
# 		language_code='pt-BR')
#
# resp = client.recognize(config, audio)
#
# alternatives = resp.results[0].alternatives
#
# for alternative in alternatives:
# 	print("Transcript: {}".format(alternative.transcript))

import io
import random
import sys
import time
import requests
import speech_recognition as sr
# Speech Recognition Imports
from pydub import AudioSegment

# Randomization Related
MIN_RAND = 0.64
MAX_RAND = 1.27
LONG_MIN_RAND = 4.78
LONG_MAX_RAND = 11.1

NUMBER_OF_ITERATIONS = 100

HOUNDIFY_CLIENT_ID = "{YOUR_CLIENT_ID}"
HOUNDIFY_CLIENT_KEY = "{YOUR_CLIENT_KEY}"

DIGITS_DICT = {
	"zero": "0",
	"one": "1",
	"two": "2",
	"three": "3",
	"four": "4",
	"five": "5",
	"six": "6",
	"seven": "7",
	"eight": "8",
	"nine": "9",
}

class rebreakcaptcha (object):
	def __init__(self):
		# url = 'https://www.google.com/recaptcha/api2/payload/audio.mp3?p=06AOLTBLS25Z8ptIWA-I_YxMpVoUiswSDqRVKv09RUHPPa6EZhV82yz-Uy2Tx5mwaCnHzd4T7FkSK-FORZ6i4dHQJrdTC3Wukkk-gw-Iw_NIgCfHLvkR5MHc66aiyxjuhRRy0VtZyBSzXDEKWDC2UFDNzO9gLF7ze_Q3nV7XNfMjttC5gMJooxZvU&k=6LcX22AUAAAAABvrd9PDOqsE2Rlj0h3AijenXoft'
		url = 'http://www.tjrs.jus.br/site_php/consulta/human_check/som.php?id=5f67ca5cf146126e685f2c05f1b71aaa'
		self.main(url)

	def main(self, link):
		counter = 0
		for i in range(NUMBER_OF_ITERATIONS):
			if self.solve_audio_challenge(link, current_iteration=i):
				counter += 1

			time.sleep(random.uniform(LONG_MIN_RAND, LONG_MAX_RAND))
			print("Successful breaks: {0}".format(counter))

		print("Total successful breaks: {0}\{1}".format(counter, NUMBER_OF_ITERATIONS))

	# def get_recaptcha_challenge(self):
	# 	while 1:
	# 		# Navigate to a ReCaptcha page
	# 		self.driver.get (RECAPTCHA_PAGE_URL)
	# 		time.sleep (random.uniform (MIN_RAND, MAX_RAND))
    #
	# 		# Get all the iframes on the page
	# 		iframes = self.driver.find_elements_by_tag_name ("iframe")
    #
	# 		# Switch focus to ReCaptcha iframe
	# 		self.driver.switch_to_frame (iframes[0])
	# 		time.sleep (random.uniform (MIN_RAND, MAX_RAND))
    #
	# 		# Verify ReCaptcha checkbox is present
	# 		if not self.is_exists_by_xpath ('//div[@class="recaptcha-checkbox-checkmark" and @role="presentation"]'):
	# 			print ("[{0}] No element in the frame!!".format (self.current_iteration))
	# 			continue
    #
	# 		# Click on ReCaptcha checkbox
	# 		self.driver.find_element_by_xpath ('//*[@id="recaptcha-anchor"]/div[1]').click ()
	# 		time.sleep (random.uniform (LONG_MIN_RAND, LONG_MAX_RAND))
    #
	# 		# Check if the ReCaptcha has no challenge
	# 		if self.is_exists_by_xpath ('//span[@aria-checked="true"]'):
	# 			print ("[{0}] ReCaptcha has no challenge. Trying again!".format (self.current_iteration))
	# 		else:
	# 			return

	# def get_audio_challenge(self, iframes):
	# 	# Switch to the last iframe (the new one)
	# 	self.driver.switch_to_frame (iframes[-1])
    #
	# 	# Check if the audio challenge button is present
	# 	if not self.is_exists_by_xpath ('//button[@id="recaptcha-audio-button"]'):
	# 		print ("[{0}] No element of audio challenge!!".format (self.current_iteration))
	# 		return False
    #
	# 	print ("[{0}] Clicking on audio challenge".format (self.current_iteration))
	# 	# Click on the audio challenge button
	# 	self.driver.find_element_by_xpath ('//*[@id="recaptcha-audio-button"]').click ()
	# 	time.sleep (random.uniform (LONG_MIN_RAND, LONG_MAX_RAND))

	def get_challenge_audio(self, arq_audio):
		# Download the challenge audio and store in memory
		request = requests.get(arq_audio)
		audio_file = io.BytesIO(request.content)
		# Convert the audio to a compatible format in memory
		converted_audio = io.BytesIO()
		# sound = AudioSegment.from_mp3(audio_file)
		sound = AudioSegment.from_wav(audio_file)
		# sound = AudioSegment.from_mp3(audio_file)
		sound.export(converted_audio, format="wav")
		converted_audio.seek(0)

		return converted_audio

	# def string_to_digits(self, recognized_string):
	# 	return ''.join ([DIGITS_DICT.get (word, "") for word in recognized_string.split (" ")])

	def speech_to_text(self, audio_source):
		# Initialize a new recognizer with the audio in memory as source
		recognizer = sr.Recognizer()
		with sr.AudioFile(audio_source) as source:
			audio = recognizer.record(source)  # read the entire audio file

		audio_output = ""
		# recognize speech using Google Speech Recognition
		try:
			audio_output = recognizer.recognize_google(audio_data=audio, key=None, show_all=True)
			print("[{0}] Google Speech Recognition: ".format(self.current_iteration) + audio_output)
		except sr.UnknownValueError:
			print("[{0}] Google Speech Recognition could not understand audio".format(self.current_iteration))
		except sr.RequestError as e:
			print("[{}] Could not request results from Google Speech Recognition service; {}".format(self.current_iteration, e))

		return audio_output

	def solve_audio_challenge(self, arq_audio, current_iteration):
		self.current_iteration = current_iteration + 1
		# # Verify audio challenge download button is present
		# if not self.is_exists_by_xpath ('//a[@class="rc-audiochallenge-download-link"]') and \
		#         not self.is_exists_by_xpath ('//div[@class="rc-text-challenge"]'):
		#     print ("[{0}] No element in audio challenge download link!!".format (self.current_iteration))
		#     return False
		#
		# # If text challenge - reload the challenge
		# while self.is_exists_by_xpath ('//div[@class="rc-text-challenge"]'):
		#     print ("[{0}] Got a text challenge! Reloading!".format (self.current_iteration))
		#     self.driver.find_element_by_id ('recaptcha-reload-button').click ()
		#     time.sleep (random.uniform (MIN_RAND, MAX_RAND))
		#
		# # Get the audio challenge URI from the download link
		# download_object = self.driver.find_element_by_xpath ('//a[@class="rc-audiochallenge-download-link"]')
		# download_link = download_object.get_attribute ('href')

		# Get the challenge audio to send to Google
		converted_audio = self.get_challenge_audio(arq_audio)

		# Send the audio to Google Speech Recognition API and get the output
		audio_output = self.speech_to_text(converted_audio)

		# Enter the audio challenge solution
		# self.driver.find_element_by_id('audio-response').send_keys(audio_output)
		# time.sleep(random.uniform(LONG_MIN_RAND, LONG_MAX_RAND))
        #
		# # Click on verify
		# self.driver.find_element_by_id('recaptcha-verify-button').click()
		# time.sleep(random.uniform(LONG_MIN_RAND, LONG_MAX_RAND))

		return audio_output

	# def solve(self, current_iteration):
	# 	self.current_iteration = current_iteration + 1
    #
	# 	# Get a ReCaptcha Challenge
	# 	# self.get_recaptcha_challenge ()
	# 	self.driver = webdriver.Chrome (executable_path=CHROME_BIN_PATH)
	# 	self.driver.get(url='http://www.tjrs.jus.br/site_php/consulta/verificador.php')
    #
	# 	# Switch to page's main frame
	# 	self.driver.switch_to.default_content()
    #
	# 	# Get all the iframes on the page again- there is a new one with a challenge
	# 	iframes = self.driver.find_element_by_class_name ("texto_geral")
    #
	# 	# Get audio challenge
	# 	self.get_audio_challenge (iframes)
    #
	# 	# Solve the audio challenge
	# 	if not self.solve_audio_challenge():
	# 		return False
    #
	# 	# Check if there is another audio challenge and solve it too
	# 	while self.is_exists_by_xpath ('//div[@class="rc-audiochallenge-error-message"]') and \
	# 			self.is_exists_by_xpath ('//div[contains(text(), "Multiple correct solutions required")]'):
	# 		print ("[{0}] Need to solve more. Let's do this!".format (self.current_iteration))
	# 		self.solve_audio_challenge()
    #
	# 	# Switch to the ReCaptcha iframe to verify it is solved
	# 	self.driver.switch_to.default_content ()
	# 	self.driver.switch_to_frame (iframes[0])
    #
	# 	return self.is_exists_by_xpath ('//span[@aria-checked="true"]')


# def main(link):
# 	# rebreakcaptcha_obj = rebreakcaptcha()
#
# 	counter = 0
# 	for i in range(NUMBER_OF_ITERATIONS):
# 		if rebreakcaptcha_obj.solve_audio_challenge(link, current_iteration=i):
# 			counter += 1
#
# 		time.sleep(random.uniform(LONG_MIN_RAND, LONG_MAX_RAND))
# 		print("Successful breaks: {0}".format(counter))
#
# 	print("Total successful breaks: {0}\{1}".format(counter, NUMBER_OF_ITERATIONS))

if __name__ == '__main__':
	teste = rebreakcaptcha()
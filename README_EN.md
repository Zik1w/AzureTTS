
  

# AzureTTS

  

  

## Description

  

A Text-To-Speech (TTS) tool based on Microsoft Azure Neural TTS algorithm. Generate batch audio files (**.wav** format by default) based on user customizaiton **Excel** files.

  
  

## Usage
  

By running the [AzureTTS.py](AzureTTS.py) script along side two excel files for *configuration* and *script*, user can generate AI voice audio files in various languages with their own Microsoft Azure accounts all in one stop.

  

### Environment

  
Python 3.7 or higher

Wwise 2019.2.14 or higher (optional)


### Configuration


1. Fill the `SUBSCRIPTION_KEY` inside [AzureTTS.py](AzureTTS.py) (`__init__`) function with your Azure Service Keychain \

2. In the same function, fill `SERVER` with the Azure server you plan to use, the default is *eastasia* server.

  
  
  

### Input data files

  

`AzureTTS_Configuration.xlsx`: The configuraiton file for pairing character with specific voice line and other general information.

  
  

* 角色名 (CharacterID, 1st column): Self-defined character name, same as the ones in *script* file.

  

* 音色 (VoiceID, 2nd column): The voice line identification from the Azure speech service, first letter will always be Captialized. For Chinese voice, please refer to the Microsoft document for [Supported Languages](https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support?tabs=tts)

  

* 语速 (Speed, 3rd column): The ratio at which the voice is speaking. Default at 1, and range is *[0,2]*

  

`AzureTTS_Script.xlsx`: The document for the script, each row will generate individual file accordingly. Chinese and English lines are in separate sheet.

  
  

* 角色名 (CharacterID, 1st column)：Self-defined character name, make sure they are the same as the ones in *configuration* file.

  

* 台词 (Line, 2nd column)：The literal line that will be used to generate audio files

  

* 音频文件名 (FileID, 3rd column)：The name for the output audio files

  

* 语速 (Speed, 4th column)：The rate at which the voice will be speaking. If this is empty, the speed for this character in the configuration file will be used by default.

  

### Output AI voice audio files

  
  

#### Path

```

.

├── TTSAudioFiles ## audio files output folder

│ ├── CN ## Chinese AI audio files

│ │ ├── ...XXX_CN.wav

│ │ ├── ...XXX_CN.wav

│ │ ├── ...XXX_CN.wav

│ ├── EN ## Enligsh AI audio files

│ │ ├── ...XXX_EN.wav

│ │ ├── ...XXX_EN.wav

│ │ ├── ...XXX_EN.wav

  

```

  

#### Format

  

##### Audio file


* output format is in 48Khz, 16bit mono .wav(pcm) audio files

* This is mainly to support game audio related demand. If you need to output other format(.mp3, etc.), please switch to other format provided in the `X-Microsoft-OutputFormat` section



##### Wwise import

  * Default to SFX object，Chinese and English voice line will have CN and EN atuomatically added at the end of their name respectfully.

  * Event with same name will also be created automatically and their default path is Events/Default Work Unit

  * The default path for Sound Object is WorkUnit called *VOX_AI*，**If you decide to use this path, manually create it inside your Wwise project before running the procedure**

  * The default output path for raw audio file is SFX/VOX_AI/[CN|EN]

  

## Run

  
  

1.Use AzureTTS.bat

  

Before running it, update`PATHONPATH` to local python.exe path, default is `py`

  

2.Use [AzureTTS.py](AzureTTS.py)

  

````py AzureTTS.py [Lang] [To_Normalize] [To_Wwise]````

  

*  `Lang`: choice of language，options are CN and EN

  

*  `To_Normalize`：choice of whether or not to perform normalization，options are y(yes) or n(no), no by default

  

	* default normalization level is -18dBFS, can be modified inside the file.

  

*  `To_Wwwise`: choice of whether or not to run the wwise importing process, options are y(yes) or n(no), no by default

  

	* turn the WAAPI connection on before use the wwise importing function
  

	* only one wwise project should be opened during this operation

  

	* when the sound objects are created, the line will be added as their notes by default

  

	* change configuraiton inside [AzureTTS.py](AzureTTS.py) `__init__` function to meet your need

  
  
  

### Limitation
  

The current version only support the output of *Chinese* and *English* voice line, one can duplicate the run section and modify the language variable `lang` to meet demand for other languages.

  
  

### Tech support


This tool is for personal use, if you run into any problems, feel free to leave a message~
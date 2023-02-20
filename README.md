
# AzureTTS

  
  

## English Doc

[英文资料](README_EN.md)

  

## 概述

  

一个可自定义多角色的用于批量生成.wav文件的基于微软Azure的文本转语音工具。

  

A TTS tool based on Microsoft Azure Text-to-Speech API that can generate batch **.wav** audio files (by default) based on user customized *configuration* and *script* excel files.

  

## 使用说明

  

### 环境

Python 3.7 以上
Wwise 2019.2.14 以上

 
### 初始化

  

1. 使用前请在 [AzureTTS.py](AzureTTS.py )的初始化函数(`__init__`)中的`SUBSCRIPTION_KEY`变量处填写自己的Azure账号密匙
2. 与`SERVER`处填写选择自己需要使用的服务器，默认使用Azure的eastasia（东亚）服务器


### 输入

  

`AzureTTS_Configuration.xlsx`: 配置文件，将中文(CN) 和 英文 (EN) 划分在对应Sheet

  

* 角色名: 自由定义的角色名，与台词文件中角色名绑定

* 音色: 严格按Azure提供的声线名填写，英文名称首字母大写，中文填对应汉字，与Azure声线库绑定，参考微软官方提供的[人声名称清单](https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support?tabs=tts)

* 语速: 默认为1，范围为0~2之间

  

`AzureTTS_Script.xlsx`: 台词文件，将中文(CN) 和 英文 (EN) 划分在对应Sheet

  

* 角色名：自由定义的角色名，与配置文件中角色名绑定

* 台词：对应的中英文台词

* 音频文件名：输出wav文件时的名称

* 语速：每条文件输出时的语速，如为空则会使用配置文件中该角色默认语速

  

### 输出

  

默认输出双语（中英文）音频资源文件，不运行响度标准化处理，不自动进行Wwise导入

  

#### AI语音wav文件路径

```
.
├── TTSAudioFiles         ## audio files output folder
│   ├── CN                ## Chinese AI audio files
│   │   ├── ...XXX.wav   
│   │   ├── ...XXX.wav
│   │   ├── ...XXX.wav
│   ├── EN				  ## Enligsh AI audio files
│   │   ├── ...XXX.wav   
│   │   ├── ...XXX.wav
│   │   ├── ...XXX.wav

```

#### AI语音wav文件格式

* 输出格式默认为48KHz, 16bit 单声道.wav(pcm) 文件，主要是为了支持游戏相关音频需求，其他输出格式也于AzureTTS.py文档中提供，请自行替换即可

* Wwise导入格式

* 默认为SFX object，中英文最后接CN和EN最后尾缀

* 同时生成一一对应的Play事件

* 默认输出Sound Object路径为VOX_AI的WorkUnit，在使用此工具导入前需**先手动建立**

* 默认输出音频文件路径为SFX/VOX_AI/[CN|EN]，自动生成

* 默认输出Event路径为Default Work Unit

  
  
  

## 运行


1.使用AzureTTS.bat

使用前请务必将本文件中的`PATHONPATH`改为本地python.exe路径！默认为`py`

2.使用 AzureTTS.py 

 ````py AzureTTS.py [Lang] [To_Normalize] [To_Wwise]````

*  `Lang`: 语言选择，选项为CN/EN

*  `To_Normalize`：响度标准化处理选择，选项为y/n

	* 默认为-18dBFS, 可于.py文件中自行修改

*  `To_Wwwise`: 将生成的AI语音文件导入当前开启的Wwise工程，选项为y/n
	*  使用前请确保Waapi连接已开启

	*  要使用导入wwise功能请保持有且只有一个wwise工程处于开启状态

	*  导入同时默认将台词导入生成的Sound Ojbect的Notes

	*  各类参数均可自行在`AzureTTS.py`的初始化(init)函数中设置



### 使用范围

当前版本仅支持中英文双语言AI语音资源输出



### 技术支持

此工具为个人向使用，如遇到问题，欢迎提出~
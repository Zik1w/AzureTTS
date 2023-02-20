# -*- coding: utf-8 -*-

'''
 * Script Name: Microsoft Azure批量AI语音生成和后期处理工具
 * Author: Zik1w
 * Author URI: 
 * Repository: 
 * Repository URI: https: 
 * Licence: GPL v3
 * Version: 1.2
 
 * Changelog:
 * v1.0 (2022-01-12) init
 * v1.1 (2022-01-19) add postprocess module
 * v1.2 (2022-02-05) add WAAPI module

'''

import sys, os
import requests
from xml.etree import ElementTree
import wave
import pandas
from pprint import pprint
from pydub import AudioSegment  ## 用于响度标准化
from waapi import WaapiClient, CannotConnectToWaapiException ## WAAPI连接接口
import waapi_helpers            ## WAAPI接口相关调用函数

 
'''
快速入门：https://docs.microsoft.com/zh-cn/azure/cognitive-services/speech-service/quickstart-python-text-to-speech
官方源码：https://github.com/Azure-Samples/Cognitive-Speech-TTS/blob/master/Samples-Http/Python/TTSSample.py
获取密钥：https://azure.microsoft.com/zh-cn/try/cognitive-services/my-apis/?apiSlug=speech-services&country=China&allowContact=true&fromLogin=True
终结点: https://eastasia.api.cognitive.microsoft.com/sts/v1.0
获取Token接口：https://eastasia.api.cognitive.microsoft.com/sts/v1.0/issueToken
文本转语音接口：https://eastasia.tts.speech.microsoft.com/cognitiveservices/v1
'''


class NeuralVoiceTable(object):

    def __init__(self):

        ## 中文人声库对应关系：https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support?tabs=tts
        self.T = dict()
        self.T["晓辰"] = "Xiaochen"
        self.T["晓涵"] = "Xiaohan"
        # self.T["晓梦"] = "Xiaomeng"
        self.T["晓墨"] = "Xiaomo"
        self.T["晓秋"] = "Xiaoqiu"
        self.T["晓睿"] = "Xiaorui"
        # self.T["晓爽"] = "Xiaoshuang"
        self.T["晓晓"] = "Xiaoxiao"
        self.T["晓萱"] = "Xiaoxuan"
        self.T["晓颜"] = "Xiaoyan"
        # self.T["晓伊"] = "Xiaoyi"
        self.T["晓悠"] = "Xiaoyou"
        # self.T["晓珍"] = "Xiaozhen"
        # self.T["云锋"] = "Yunfeng"
        # self.T["云豪"] = "Yunhao"
        # self.T["云建"] = "Yunjian"
        # self.T["云夏"] = "Yunxia"
        self.T["云希"] = "Yunxi"
        self.T["云扬"] = "Yunyang"
        self.T["云野"] = "Yunye"
        # self.T["云择"] = "Yunze"

class TTSVoice(object):

    def __init__(self, character, voice, speed):
        self.character = character
        self.voice = voice        
        self.speed = speed


class TTSLine(object):

    def __init__(self, character, line, file_name, speed):
        self.character = character
        self.line = line     
        self.file_name = file_name
        self.speed = speed
 

class AzureTextToSpeech(object):

    def __init__(self, lang):
        self.voice_table = NeuralVoiceTable().T ## AzureAPI音色对应表
        self.config_table_cn = dict()           ## 中文设置
        self.config_table_en = dict()           ## 英文设置
        self.script_table_cn = dict()           ## 中文台词
        self.script_table_en = dict()           ## 英文台词
        self.file_list = []                     ## 资源文件名
        self.language = lang
        self.SUBSCRIPTION_KEY = ''                                      ## 个人的Azure密钥，必填！
        self.SERVER = "eastasia"                                        ## 使用的Azure服务器（默认东亚）
        self.CONFIG_PATH = 'AzureTTS_Configuration.xlsx'                ## 设置表路径
        self.SCRIPT_PATH = 'AzureTTS_Script.xlsx'                       ## 台词表路径
        self.NORMALIZE_DBFS = -18.0                                     ## 响度标准化值
        self.WWISE_WORKUNIT_PATH = '\\Actor-Mixer Hierarchy\\VOX_AI'    ## 默认生成Wwise Sound Object的Work Unit路径
        self.WWISE_ACTORMIXER_PATH = '\\<Actor-Mixer>VOX_AI'            ## 默认生成Wwise Sound Object的Actor Mixer路径
        self.WWISE_AUDIOFILE_PATH = 'VOX_AI\\'                          ## 默认导入Wwise音频文件路径
        self.WWISE_EVENT_PATH = '\\Events\\Default Work Unit'           ## 默认生成Wwise Event路径
    

    ## 设置角色和音色对应关系
    def set_config(self):

        config_excel = pandas.ExcelFile(self.CONFIG_PATH)
        for sheetName in config_excel.sheet_names:
            if sheetName == "CN":
                dataFrame = config_excel.parse(sheetName)
                df = dataFrame[["角色名", "音色", "语速"]]
                for _, info in df.iterrows():
                    self.config_table_cn[str(info["角色名"])] = TTSVoice(str(info["角色名"]), str(info["音色"]), str(info["语速"]))
            elif sheetName == "EN":
                dataFrame = config_excel.parse(sheetName)
                df = dataFrame[["角色名", "音色", "语速"]]
                for _, info in df.iterrows():
                    self.config_table_en[str(info["角色名"])] = TTSVoice(str(info["角色名"]), str(info["音色"]), str(info["语速"]))
        

    ## 台词文本预处理
    def pre_process(self):
        script_excel = pandas.ExcelFile(self.SCRIPT_PATH)

        for sheetName in script_excel.sheet_names:
            if sheetName == "CN":
                dataFrame = script_excel.parse(sheetName)
                df = dataFrame[["角色名", "台词", "音频文件名", "语速"]]
                for _, info in df.iterrows():
                    self.script_table_cn[str(info["音频文件名"])] = TTSLine(str(info["角色名"]), str(info["台词"]), str(info["音频文件名"]), str(info["语速"]))
            elif sheetName == "EN":
                dataFrame = script_excel.parse(sheetName)
                df = dataFrame[["角色名", "台词", "音频文件名", "语速"]]
                for _, info in df.iterrows():
                    self.script_table_en[str(info["音频文件名"])] = TTSLine(str(info["角色名"]), str(info["台词"]), str(info["音频文件名"]), str(info["语速"]))


    ### 批处理
    def batch_process(self):

        if not os.path.exists('TTSAudioFiles\\CN'):
            os.makedirs('TTSAudioFiles\\CN')

        if not os.path.exists('TTSAudioFiles\\EN'):
            os.makedirs('TTSAudioFiles\\EN')

        ## 默认东亚服务器
        fetch_token_url = 'https://' + self.SERVER + '.api.cognitive.microsoft.com/sts/v1.0/issueToken'
        headers = {
            'Ocp-Apim-Subscription-Key': self.SUBSCRIPTION_KEY
        }
        response = requests.post(fetch_token_url, headers=headers, verify=True) 
        access_token = str(response.text)
        print(">> 获取 Token：" + access_token)
        constructed_url = 'https://' + self.SERVER + '.tts.speech.microsoft.com/cognitiveservices/v1'
        headers = {
            ## 前面带有单词 Bearer 的授权令牌
            'Authorization': 'Bearer ' + access_token,
 
            ## 指定所提供的文本的内容类型。 接受的值：application/ssml+xml。
            'Content-Type': 'application/ssml+xml',
 
            ## 指定音频输出格式，取值如下：
            # raw-16khz-16bit-mono-pcm
            # raw-8khz-8bit-mono-mulaw
            # riff-8khz-8bit-mono-alaw
            # riff-8khz-8bit-mono-mulaw
            # riff-16khz-16bit-mono-pcm
            # audio-16khz-128kbitrate-mono-mp3
            # audio-16khz-64kbitrate-mono-mp3
            # audio-16khz-32kbitrate-mono-mp3
            # raw-24khz-16bit-mono-pcm
            # raw-48khz-16bit-mono-pcm
            # riff-24khz-16bit-mono-pcm
            # audio-24khz-160kbitrate-mono-mp3
            # audio-24khz-96kbitrate-mono-mp3
            # audio-24khz-48kbitrate-mono-mp3
            'X-Microsoft-OutputFormat': 'raw-48khz-16bit-mono-pcm',
 
            ## 应用程序名称，需少于 255 个字符。
            # Chrome的 User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36
            'User-Agent': 'Chrome/73.0.3683.86'
        }

        ## 中文台词
        cnt_cn_scuess = 0
        cnt_cn_fail = 0
        cnt_en_scuess = 0
        cnt_en_fail = 0

        if self.language == 'CN' or self.language == "ALL":
            for id, info in self.script_table_cn.items():
                lang = 'zh-CN'
                xml_body = ElementTree.Element('speak', version='1.0')
                xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', lang)
                xml_body.set('xmlns', "http://www.w3.org/2001/10/synthesis")
                voice = ElementTree.SubElement(xml_body, 'voice')
                voice.set('name', lang + '-' + self.voice_table[self.config_table_cn[info.character].voice] + 'Neural')
                prosody = ElementTree.SubElement(voice, 'prosody')
                prosody.set('rate', info.speed if info.speed != 'nan' else self.config_table_cn[info.character].speed)
                prosody.text = info.line
                body = ElementTree.tostring(xml_body, encoding='UTF-8')
                body = body.decode('utf-8')
                print(">> 输出XML为：")
                print(body)               

                print(">> 调用接口转换语音中......")
                response = requests.post(constructed_url, headers=headers, data=body.encode('UTF-8'), verify=True)   
                if response.status_code == 200:
                    audio_file_name = info.file_name + '.wav'
                    audio_file_path = os.path.join('TTSAudioFiles\\CN', audio_file_name)
                    with wave.open(audio_file_path, 'wb') as audio:
                        audio.setnchannels(1)
                        audio.setsampwidth(2)   ### Bytes number, not Bits
                        audio.setframerate(48000)
                        audio.writeframes(response.content)
                        self.file_list.append((info.file_name, audio_file_path, 'CN'))
                        cnt_cn_scuess += 1
                        print(">> 文本转语音已完成，生成的音频文件：" + audio_file_name)
                else:
                    cnt_cn_fail += 1
                    print("[失败] response code: " + str(response.status_code)
                            + "\nresponse headers: " + str(response.headers) )
                

        ## 英文台词
        if self.language == 'EN' or self.language == "ALL":
            for id, info in self.script_table_en.items():
                lang = 'en-US'
                xml_body = ElementTree.Element('speak', version='1.0')
                xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', lang)
                xml_body.set('xmlns', "http://www.w3.org/2001/10/synthesis")
                voice = ElementTree.SubElement(xml_body, 'voice')
                voice.set('name', lang + '-' + self.config_table_en[info.character].voice + 'Neural')
                prosody = ElementTree.SubElement(voice, 'prosody')
                prosody.set('rate', info.speed if info.speed != 'nan' else self.config_table_en[info.character].speed)
                prosody.text = info.line
                body = ElementTree.tostring(xml_body)
                print(body)                         
                print(">> 调用接口转换语音中......")
                response = requests.post(constructed_url, headers=headers, data=body, verify=True)   
                if response.status_code == 200:
                    audio_file_name = info.file_name + '.wav'
                    audio_file_path = os.path.join('TTSAudioFiles\\EN', audio_file_name)
                    with wave.open(audio_file_path, 'wb') as audio:
                        audio.setnchannels(1)
                        audio.setsampwidth(2)   ### Bytes number, not Bits
                        audio.setframerate(48000)
                        audio.writeframes(response.content)
                        self.file_list.append((info.file_name, audio_file_path, 'EN'))
                        cnt_en_scuess += 1
                        print(">> 文本转语音已完成，生成的音频文件：" + audio_file_name)
                else:
                    cnt_en_fail += 1
                    print("[失败] response code: " + str(response.status_code)
                            + "\nresponse headers: " + str(response.headers) )
                
        print(">> 语音资源生成已完成")
        print(f">> 中文资源，成功：{cnt_cn_scuess}，失败: {cnt_cn_fail}")
        print(f">> 英文资源，成功：{cnt_en_scuess}，失败: {cnt_en_fail}")
        return


    ## 后期处理
    def post_process(self):

        print(f">> 语音响度标准化处理中......目标响度为 {self.NORMALIZE_DBFS} dBFS")
        for f in self.file_list:
            self.normalize_dBFS(f)
        print(">> 语音响度标准化已完成")
        return


    ## 响度标准化    
    def normalize_dBFS(self, file):
        raw_audio = AudioSegment.from_file(file, format="wav")  
        diff_dBFS = self.NORMALIZE_DBFS - raw_audio.dBFS
        normalized_audio = raw_audio.apply_gain(diff_dBFS)
        normalized_audio.export(file, format="wav")
        return
    
    ## 导入wwise并进行后续处理
    def post_process_wwise(self):
        try:
        # Connecting to Waapi using default URL
            with WaapiClient() as client:                
                
                ## RPC 开始
                print("获取当前连接Wwise项目信息:")
                
                result = client.call("ak.wwise.core.getInfo")
                pprint(result)
                
                print(">> 将音频文件导入Wwise......")

                object_import_args = dict()
                object_import_args['importOperation'] = 'useExisting'
                object_import_args['default'] = dict()
                object_import_args['imports'] = []

                # begin_undo_group(client)

                ## 生成对应Sound Object
                for f_name, f_path, f_lang in self.file_list:
                    object_import_args['imports'].append(
                        {
                        "importLanguage": "SFX",
                        "@Volume": "1",
                        "originalsSubFolder": self.WWISE_AUDIOFILE_PATH + ('CN' if f_lang == 'CN' else 'EN'),
                        "audioFile": os.path.join(os.getcwd(), f_path),
                        "objectPath": self.WWISE_WORKUNIT_PATH + self.WWISE_ACTORMIXER_PATH  + '\\<Sound SFX>' + f_name,
                        "@IsStreamingEnabled": True,
                        "notes": (self.script_table_cn[f_name].line if f_lang == 'CN' else self.script_table_en[f_name].line)   ##将台词导入对应生成的Sound Object的Notes
                    })

                results_import = client.call("ak.wwise.core.audio.import", object_import_args)
                results_import_table = dict() 
                if results_import is not None:
                    if len(results_import['objects']) >= 2:
                        for idx, item in enumerate(results_import['objects']):
                            results_import_table[item['name']] = item['id']
                else:
                    print("WARNING: No new sound is imported!")
                    return
                    
                ## 生成对应Event
                for f_name, f_path, f_lang in self.file_list:
                    if waapi_helpers.object_get(client, from_path=['\\Events'], select_mode=['descendants'], where_name_matches=f_name, where_type_isIn=['Event']) is None:
                        object_createEvent_args = {
                            "parent": self.WWISE_EVENT_PATH,
                            "type": "Event",
                            "name": f_name,
                            "onNameConflict": "fail",
                            "children": [
                                {
                                    "name": "",
                                    "type": "Action",
                                    "@ActionType": 1,
                                    "@Target": results_import_table[f_name]

                                }
                            ]
                        }
                        res_create = client.call("ak.wwise.core.object.create", object_createEvent_args)
                        if res_create is None:
                            raise RuntimeError(f'ERROR: Create event has failed - {f_name}')
                    else:
                        print (f'WARNNING: event already exists - {f_name}')

                # end_undo_group(client, 'Import AI audio files')

        except CannotConnectToWaapiException:
            print("Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?")
        return

if __name__ == "__main__":
    intput_language = 'CN'
    to_normalize = 'n'
    to_wwise = 'y'

    if len(sys.argv) == 2:
        intput_language = sys.argv[1]

    if len(sys.argv) == 3:
        to_normalize = sys.argv[2]
    
    if len(sys.argv) == 4:
        to_wwise = sys.argv[3]

    tts_factory = AzureTextToSpeech(intput_language)
    tts_factory.set_config()
    tts_factory.pre_process()
    tts_factory.batch_process()

    if to_normalize == 'y':
        tts_factory.post_process()        ## 后期处理，例如响度标准化处理等

    if to_wwise == 'y':
        tts_factory.post_process_wwise()  ## WAAPI功能，例如自动化导入等


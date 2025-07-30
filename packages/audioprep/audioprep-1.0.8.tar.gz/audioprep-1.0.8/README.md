### AI 音频预处理工具
#### 功能描述
* 包含常见的AI音频预处理功能，如音频重采样、音频去空白、音频时长获取等。
                 
#### pip安装
```shell
pip install audioprep
```

##### 移除静音
```
    from audioprep import silence
    res = silence.trim_silence("530.mp3", "530_after.mp3")
    print(res)
```

##### 音频重采样
```
    from audioprep import resample
    res = resample.resample_audio("530.mp3", 16000)
    print(res)
```


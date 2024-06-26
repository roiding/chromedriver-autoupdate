
import os
import platform
import re
import shutil
import subprocess
import sys
import zipfile  # 操作.zip文件

import requests
from tqdm import tqdm
from urllib3.exceptions import InsecureRequestWarning
'''
ODO 还有一种方式获取版本
https://sites.google.com/a/chromium.org/chromedriver/downloads/version-selection
'''
# 匹配三位版本号的正则
version_re =re.compile(r'[1-9]\d*\.\d*\.\d*')
'''
driver_path: chrome_driver的路径
'''
def checkAndUpdate(driver_path:str):
    chrome_version=_getChromeVersion()
    platform_name=platform.system()
    if platform_name == "Windows":
        driver=os.path.join(driver_path,"chromedriver.exe")
    else:
        driver=os.path.join(driver_path,"chromedriver")
    if os.path.exists(driver):
        os.chmod(driver,755)
        driver_version = _matchChromeVersion(driver+" --version")
        if chrome_version == driver_version:
            return os.path.realpath(driver)
        # 下载对应版本驱动
        ''' 
            1. 删除原先driver
            2. 下载对应驱动
        '''
        os.unlink(driver)
    _downLoadDriver(chrome_version,driver_path)
    # 赋执行权限
    os.chmod(driver,755)
    # _driverRunableConfig(driver)
    return os.path.realpath(driver)

    

# Chrome浏览器版本
def _getChromeVersion():
    # 判断系统版本
    platform_name=platform.system()
    if platform_name == "Linux":
        chrome_path=('/opt/google/chrome',)
        path=_checkPathExit(chrome_path)
        return _matchChromeVersion(path+" --version")
    elif platform_name == "Darwin":
        chrome_path=('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',)
        path=_checkPathExit(chrome_path).replace(' ','\ ')
        return _matchChromeVersion(path+" --version")
    elif platform_name == "Windows":
        chrome_path=('C:\\\\Program Files\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe','C:\\\\Program Files (x86)\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe');
        path=_checkPathExit(chrome_path)
        return _matchChromeVersion("wmic datafile where name=\"%s\" get Version /value"%(path))
    else:
        raise RuntimeError("该操作系统暂不支持")


def _checkPathExit(tupleList:tuple):
    for path in tupleList:
        if os.path.exists(path):
            return path
    raise RuntimeError("Chrome未安装在默认路径下")


def _matchChromeVersion(command:str):
    process=subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (version_str,stderr)=process.communicate()
    return version_re.findall(version_str.decode('utf-8'))[0]
    


# 淘宝源获取
def _downLoadDriver(version, save_d):
    # 去除SSL不安全警告
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    url ="https://registry.npmmirror.com/-/binary/chromedriver"
    # 访问淘宝镜像首页  
    rep = requests.get(url,verify=False)
    rep.encoding="utf-8"
    # '<a href="/mirrors/chromedriver/84.0.4147.30/">84.0.4147.30/</a>'

    directory = re.compile(version.replace(".","\.")+"\.\d+").findall(rep.text)  # 匹配文件夹（版本号）
    # 判断系统版本
    platform_name=platform.system()
    # 获取期望的文件夹（版本号）
    if len(directory)!=0:
        # 淘宝源有driver
        # https://registry.npmmirror.com/-/binary/chromedriver/83.0.4103.39/chromedriver_win32.zip
        dirUrl = url+"/"+directory[-1]
        if platform_name == "Linux":
            downUrl = dirUrl+'/chromedriver_linux64.zip'
        elif platform_name == "Darwin":
            # intel芯片
            if platform.machine() == 'x86_64':
                downUrl = dirUrl+'/chromedriver_mac64.zip'
            else:
                downUrl = dirUrl+'/chromedriver_mac_arm64.zip'
        elif platform_name == "Windows":
            # intel芯片
            if platform.machine() == 'x86_64':
                downUrl = dirUrl+  '/chromedriver_win32.zip'
            else:
                downUrl = dirUrl+  '/chromedriver_win64.zip'
        else:
            raise RuntimeError("该操作系统暂不支持")
    else:
        # 去google直接下载
        result=requests.get("https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json",verify=False).json().get("versions")
        class BreakLoop(Exception):
            pass
        # 倒序循环results
        try:
            for item in result[::-1]:
                if item.get("version").startswith(version):
                    url_items=item.get("downloads").get("chromedriver")
                    if platform_name == "Linux":
                        _platform = 'linux64'
                    elif platform_name == 'Darwin':
                        if platform.machine() == 'x86_64':
                            _platform = 'mac-arm64'
                        else:
                            _platform = 'mac-x64'
                    elif platform_name == "Windows":
                        if platform.machine() == 'x86_64':
                            _platform = 'win64'
                        else:
                            _platform = 'win32'
                    else:
                        raise RuntimeError("该操作系统暂不支持")
                    for url_item in url_items:
                        if url_item.get("platform") == _platform:
                            downUrl = url_item.get("url")
                            raise BreakLoop
        except BreakLoop:
            pass
                        

    print('将要下载 {}'.format(downUrl))

    # 指定下载的文件名和保存位置
    temp_path=os.path.join(save_d,"driver")
    if not os.path.exists(temp_path):
        os.mkdir(temp_path)
    file = os.path.join(temp_path, os.path.basename(downUrl))

    # 开始下载，并显示下载进度
    response = requests.get(downUrl,stream=True,verify=False)
    total = int(response.headers.get('content-length',0))
    temp_driver_zip=os.path.join(temp_path,"chromedriver.zip")
    with open(temp_driver_zip,'wb') as file,tqdm(
        desc="chromedriver",
        total=total,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    )as bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)
    # 下载完成后解压
    with zipfile.ZipFile(temp_driver_zip, 'r') as zFile:
        for file in zFile.filelist:
            if os.path.basename(file.filename).startswith("chromedriver"):
                # 获取文件的名字，去除路径信息
                filename = os.path.basename(file.filename)
                if filename:  # 确保不是一个空的文件夹条目
                    # 构造目标文件路径
                    dest = os.path.join(save_d, filename)
                    # 提取文件到目标路径
                    with zFile.open(file.filename) as source, open(dest, 'wb') as target:
                        target.write(source.read())
    shutil.rmtree(temp_path)

def _driverRunableConfig(driver_path:str):
    # 苹果电脑
    if platform.system() == "Darwin":
        #  需要过验证
        subprocess.Popen("xattr -d com.apple.quarantine "+driver_path,shell=True)
from time import sleep
import socketio
from loguru import logger
import json
import httpx

sio = socketio.Client()

try:
    with open("awl.json", "r", encoding='UTF-8') as f:
        config = json.load(f)
    secret = config['secret']
except:
    logger.error("读取配置文件失败，请检查配置文件是否存在且格式是否正确")

try:
    whitelistFile = open("whitelist.json", "r", encoding='UTF-8')
    whitelist = json.load(whitelistFile)
    logger.info("读取白名单列表中")
    for i in whitelist:
        logger.info("uuid:" + i['uuid'])
        logger.info("name:" + i['name'])
    logger.info("读取完毕，请确认是否能正确读取")
except:
    logger.error("读取whitelist.json失败，请检查文件是否存在或是否损坏")


@sio.on('connect')
def on_connect():
    logger.info('正在注册，请稍后')
    sleep(2)
    sid = sio.get_sid(namespace='/mission')
    sio.emit('register', {'secret': secret, 'sid': sid})


@sio.on('register')
def isReg(data):
    if data['status'] == "success":
        logger.info("注册成功 ，当前 token 为" + data['token'])
        pass
    elif data['status'] == "failed":
        logger.error("注册失败：secret不存在")
        sleep(1)
        input("按enter键继续")
        assert ()
    else:
        logger.error("注册失败：未知错误")
        sleep(1)
        input("按enter键继续")
        assert ()


@sio.on("newMission", namespace='/mission')
def newMission(data):
    id = data["id"]
    logger.info("新玩家%s已通过入服考试，即将添加白名单" % id)
    respond = httpx.get("https://api.mojang.com/users/profiles/minecraft/" + id)
    if respond.status_code == "204":
        logger.error("白名单添加失败：该玩家不存在")
        return {"status": "failed", "reason": "player not found"}
    elif respond.status_code == "200":
        playerdata = json.loads(respond.read())
        whitelist.insert(playerdata)
        whitelistFile.write(whitelist)

        return {"status": "success"}
    else:
        logger.error("白名单添加失败：无法查询玩家信息，请确保网络畅通")
        return {"status": "failed", "reason": "network error"}


sio.connect('ws://127.0.0.1:8090/')
sio.wait()

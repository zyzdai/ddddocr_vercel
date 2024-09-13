import base64
import json
import ddddocr
import requests
import os
from flask import Flask, request, jsonify, make_response
app = Flask(__name__)

class Server(object):
    def __init__(self, ocr=True, det=False, old=False):
        self.ocr_option = ocr
        self.det_option = det
        self.old_option = old
        self.ocr = None
        self.det = None
        if self.ocr_option:
            if self.old_option:
                self.ocr = ddddocr.DdddOcr(old=True)
            else:
                self.ocr = ddddocr.DdddOcr()
        if self.det_option:
            self.det = ddddocr.DdddOcr(det=True)

    def classification(self, img: bytes):
        if self.ocr_option:
            return self.ocr.classification(img)
        else:
            raise Exception("ocr模块未开启")

    def detection(self, img: bytes):
        if self.det_option:
            return self.det.detection(img)
        else:
            raise Exception("目标检测模块模块未开启")

    def slide(self, target_img: bytes, bg_img: bytes, algo_type: str):
        dddd = self.ocr or self.det or ddddocr.DdddOcr(ocr=False)
        if algo_type == 'match':
            return dddd.slide_match(target_img, bg_img)
        elif algo_type == 'compare':
            return dddd.slide_comparison(target_img, bg_img)
        else:
            raise Exception(f"不支持的滑块算法类型: {algo_type}")

server = Server(det=True, old=False)
def get_img(request, img_type='file', img_name='image'):
    if img_type == 'b64':
        img = base64.b64decode(request.get_data())
        try:
            dic = json.loads(img)
            img = base64.b64decode(dic.get(img_name).encode())
        except Exception as e:  # just base64 of single image
            pass
    if img_type == 'file':
        img = request.files.get(img_name).read()
    if img_type == 'url':
        try:
            img = requests.get(request.get_data()).content
        except Exception as e:  # just base64 of single image
            pass
    return img


def set_ret(result, ret_type='text'):
    if ret_type == 'json':
        if isinstance(result, Exception):
            return json.dumps({"status": 200, "result": "", "msg": str(result)})
        else:
            return json.dumps({"status": 200, "result": result, "msg": ""})
    else:
        if isinstance(result, Exception):
            return ''
        else:
            return str(result).strip()


def get_captcha(url):
    try:
        img = requests.get(url).content
        code = server.classification(img)
        return code
    except Exception as e:  # just base64 of single image
        return ''



@app.route('/')
def index():
    return 'ok'

@app.route('/<opt>/<img_type>', methods=['POST'])
@app.route('/<opt>/<img_type>/<ret_type>', methods=['POST'])
def ocr(opt, img_type='file', ret_type='text'):
    try:
        img = dddd_ocr.get_img(request, img_type)
        if opt == 'ocr':
            result = dddd_ocr.server.classification(img)
        elif opt == 'det':
            result = dddd_ocr.server.detection(img)
        else:
            raise f"<opt={opt}> is invalid"
        return dddd_ocr.set_ret(result, ret_type)
    except Exception as e:
        return dddd_ocr.set_ret(e, ret_type)

@app.route('/slide/<algo_type>/<img_type>', methods=['POST'])
@app.route('/slide/<algo_type>/<img_type>/<ret_type>', methods=['POST'])
def slide(algo_type='compare', img_type='file', ret_type='text'):
    try:
        target_img = dddd_ocr.get_img(request, img_type, 'target_img')
        bg_img = dddd_ocr.get_img(request, img_type, 'bg_img')
        result = dddd_ocr.server.slide(target_img, bg_img, algo_type)
        return dddd_ocr.set_ret(result, ret_type)
    except Exception as e:
        return dddd_ocr.set_ret(e, ret_type)



# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=8000)
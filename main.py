from flask import Flask, session, render_template, request, jsonify, escape
import requests
import json

app = Flask(__name__,
            static_url_path='',
            static_folder='static'
            )


@app.route("/")
@app.route("/kakaopay")
def main():
    return render_template('main.html')




@app.route("/kakaopay/paymethod.ajax", methods=['POST'])
def paymethod():
    if request.method == 'POST':
        URL = 'https://kapi.kakao.com/v1/payment/ready'
        headers = {
            'Authorization': "KakaoAK " + "a4c40ce9330b1686d78b12cb9fc095c1",
            "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
        }
        params = {
            "cid": "TC0ONETIME", 
            "partner_order_id": "1001",  
            "partner_user_id": "testuser",  
            "item_name": "연어초밥", 
            "quantity": 1, 
            "total_amount": 12000, 
            "tax_free_amount": 0,  
            "vat_amount" : 200,
            "approval_url": "http://127.0.0.1:5000/kakaopay/success",
            "cancel_url": "http://127.0.0.1:5000/kakaopay/cancel",
            "fail_url": "http://127.0.0.1:5000/kakaopay/fail",
        }

        res = requests.post(URL, headers=headers, params=params)
        app.tib = res.json()['tid']  # 결제 승인시 사용할 tid를 세션에 저장

        return jsonify({'next_url': res.json()['next_redirect_pc_url']})

    return render_template('main.html')


@app.route("/kakaopay/success", methods=['POST', 'GET'])
def sucess():
    URL = 'https://kapi.kakao.com/v1/payment/approve'
    headers = {
        "Authorization": "KakaoAK " + "a4c40ce9330b1686d78b12cb9fc095c1",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    params = {
        "cid": "TC0ONETIME",  # 테스트용 코드
        "tid": app.tib,  # 결제 요청시 세션에 저장한 tid
        "partner_order_id": "1001",  # 주문번호
        "partner_user_id": "testuser",  # 유저 아이디
        "pg_token": request.args.get("pg_token"),  # 쿼리 스트링으로 받은 pg토큰
    }

    res = requests.post(URL, headers=headers, params=params)
    print(res.text)
    print(res.json())
    print(res.json()['amount'])
    print(res.json()['amount']['total'])
    amount = res.json()['amount']['total']
    res = res.json()
    context = {
        'res': res,
        'amount': amount,
    }
    return render_template('success.html', context=context, res=res)

@app.route("/kakaopay/cancel", methods=['POST', 'GET'])
def cancel():
    URL = "https://kapi.kakao.com/v1/payment/order"
    headers = {
        "Authorization": "KakaoAK " + "a4c40ce9330b1686d78b12cb9fc095c1",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    params = {
        "cid": "TC0ONETIME",  # 가맹점 코드
        "tid": app.tib,  # 결제 고유 코드

    }

    res = requests.post(URL, headers=headers, params=params)
    print(res.text)
    amount = res.json()['cancel_available_amount']['total']

    context = {
        'res': res,
        'cancel_available_amount': amount,
    }
    
    if res.json()['status'] == "QUIT_PAYMENT":
        res = res.json()
        return render_template('cancel.html', params=params, res=res, context=context)


@app.route("/kakaopay/fail", methods=['POST', 'GET'])
def fail():

    return render_template('fail.html')

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(host='127.0.0.1', port=5000, debug=True)

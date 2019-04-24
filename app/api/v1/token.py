# _*_ coding: utf-8 _*_
"""
  Created by Allen7D on 2018/6/13.
"""
from flask import current_app

from app.libs.enums import ClientTypeEnum
from app.libs.error_code import Success
from app.libs.redprint import RedPrint
from app.models.user import User
from app.service.open_token import OpenToken
from app.service.token import Token
from app.validators.forms import ClientValidator, TokenValidator
from app.api_docs import token as api_doc

__author__ = 'Allen7D'

api = RedPrint(name='token', description='登录令牌', api_doc=api_doc)


@api.route('/user', methods=['POST'])
@api.doc()
def get_token():
	'''生成「令牌」'''
	form = ClientValidator().validate_for_api()
	promise = {
		ClientTypeEnum.USER_EMAIL: User.verify_by_email,
		ClientTypeEnum.USER_WX: User.verify_by_wx,
		ClientTypeEnum.USER_WX_OPEN: User.verify_by_wx_open
	}
	# 微信登录则account为code(需要微信小程序调用wx.login接口获取), secret为空
	identity = promise[ClientTypeEnum(form.type.data)](form.account.data, form.secret.data)
	# Token生成
	expiration = current_app.config['TOKEN_EXPIRATION']  # token有效期
	token = Token.generate_auth_token(identity['uid'],
									  form.type.data,
									  identity['scope'],
									  expiration)
	return Success(data=token)


@api.route('/open_auth_url', methods=['GET'])
def get_open_auth_url():
	'''
	微信开发平台授权
	:return: 跳转的链接，用于弹出「微信扫描页面」
	'''
	return Success(data=OpenToken('temporary').authorize_url)


@api.route('/secret', methods=['POST'])
@api.doc()
def get_token_info():
	"""解析「令牌」"""
	token = TokenValidator().validate_for_api().token.data
	result = Token.decrypt(token)
	return Success(data=result)

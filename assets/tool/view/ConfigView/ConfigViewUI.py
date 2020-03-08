# -*- coding: utf-8 -*-
# @Author: Administrator
# @Date:   2020-03-07 23:46:33
# @Last Modified by:   Administrator
# @Last Modified time: 2020-03-07 23:46:33

import wx;

from _Global import _GG;
from function.base import *;

maxLevelCnt = 21;

descriptionConfig = [
	"【生成树状图】会根据遍历层级数来生成输入路径的文件树；",
	"【查找输入框】允许输入正则匹配字符串；",
	"【替换输入框】允许输入占位符“{}”；",
	"【替换示例】输入：查找框“[x-zA-Z]*(\d+)”，替换框“test{}”；结果：“wx123 -> test123”；",
];

class ConfigViewUI(wx.Panel):
	"""docstring for ConfigViewUI"""
	def __init__(self, parent, id = -1, curPath = "", viewCtr = None, params = {}):
		self.initParams(params);
		super(ConfigViewUI, self).__init__(parent, id, pos = self.__params["pos"], size = self.__params["size"], style = self.__params["style"]);
		self._className_ = ConfigViewUI.__name__;
		self._curPath = curPath;
		self.__viewCtr = viewCtr;

	def initParams(self, params):
		# 初始化参数
		self.__params = {
			"pos" : (0,0),
			"size" : (200,-1),
			"style" : wx.BORDER_THEME,
		};
		for k,v in params.items():
			self.__params[k] = v;

	def getCtr(self):
		return self.__viewCtr;

	def initView(self):
		self.createControls(); # 创建控件
		self.initViewLayout(); # 初始化布局

	def createControls(self):
		# self.getCtr().createCtrByKey("key", self._curPath + "***View"); # , parent = self, params = {}
		self.createConfigView();
		self.createDescView();
		pass;
		
	def initViewLayout(self):
		box = wx.BoxSizer(wx.VERTICAL);
		box.Add(self.__config, flag = wx.TOP|wx.BOTTOM, border = 5);
		box.Add(self.__desc, flag = wx.TOP, border = 5);
		self.SetSizer(box);
		pass;

	def updateView(self, data):
		pass;

	def createConfigView(self):
		self.__config = wx.Panel(self, size = (self.GetSize().x, -1), style = wx.BORDER_THEME);
		title = wx.StaticText(self.__config, label = "工具配置");
		title.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD));
		level = self.createLevelCfg(self.__config);
		ignoreCase = self.createIgnoreCase(self.__config);
		box = wx.BoxSizer(wx.VERTICAL);
		box.Add(title, flag = wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border = 10);
		box.Add(level, flag = wx.TOP|wx.BOTTOM, border = 5);
		box.Add(ignoreCase, flag = wx.TOP|wx.BOTTOM, border = 5);
		self.__config.SetSizer(box);

	def createDescView(self):
		self.__desc = wx.Panel(self, size = (self.GetSize().x, -1), style = wx.BORDER_THEME);
		title = wx.StaticText(self.__desc, label = "使用说明");
		title.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD));
		desc = wx.TextCtrl(self.__desc, size = (self.__desc.GetSize().x, 400), style = wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_RICH);
		# desc.SetDefaultStyle(wx.TextAttr(wx.Colour(100, 100, 100), font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)));
		for text in descriptionConfig:
			desc.AppendText(f"*{text}\n");
		box = wx.BoxSizer(wx.VERTICAL);
		box.Add(title, flag = wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border = 5);
		box.Add(desc, flag = wx.TOP, border = 5);
		self.__desc.SetSizer(box);
		
	def createLevelCfg(self, parent):
		level = wx.Panel(parent, size = (parent.GetSize().x, -1));
		title = wx.StaticText(level, label = "遍历层级数：");
		val = wx.StaticText(level, label = str(_GG("CacheManager").getCache("maxLevel", 10)));
		btn = wx.Button(level, label = "更改", size = (40, 20));
		def onChangeBtn(event):
			ned = wx.NumberEntryDialog(parent, "更改遍历层级数", "请输入数字", "更改配置", int(val.GetLabel()), 1, maxLevelCnt);
			if ned.ShowModal() == wx.ID_OK:
				_GG("CacheManager").setCache("maxLevel", int(ned.GetValue()));
				val.SetLabel(str(ned.GetValue()));
		btn.Bind(wx.EVT_BUTTON, onChangeBtn);
		# 布局
		box = wx.BoxSizer(wx.HORIZONTAL);
		box.Add(title, flag = wx.ALIGN_CENTER|wx.LEFT, border = 5);
		box.Add(val, flag = wx.ALIGN_CENTER|wx.RIGHT, border = 5);
		box.Add(btn, flag = wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border = 5);
		level.SetSizerAndFit(box);
		return level;

	def createIgnoreCase(self, parent):
		ignoreCase = wx.Panel(parent, size = (parent.GetSize().x, -1));
		title = wx.StaticText(ignoreCase, label = "忽略大小写：");
		cb = wx.CheckBox(ignoreCase, label = "", style = wx.ALIGN_RIGHT);
		cb.SetValue(_GG("CacheManager").getCache("ignoreCase", False));
		def onCheckBox(event):
			_GG("CacheManager").setCache("ignoreCase", cb.GetValue());
		cb.Bind(wx.EVT_CHECKBOX, onCheckBox);
		# 布局
		box = wx.BoxSizer(wx.HORIZONTAL);
		box.Add(title, flag = wx.ALIGN_CENTER|wx.LEFT, border = 5);
		box.Add(cb, flag = wx.ALIGN_CENTER|wx.RIGHT, border = 5);
		ignoreCase.SetSizerAndFit(box);
		return ignoreCase;
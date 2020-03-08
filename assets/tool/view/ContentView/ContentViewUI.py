# -*- coding: utf-8 -*-
# @Author: Administrator
# @Date:   2020-03-07 23:46:11
# @Last Modified by:   Administrator
# @Last Modified time: 2020-03-07 23:46:11

import wx;

from _Global import _GG;
from function.base import *;

from ui import DirInputView;

class ContentViewUI(wx.Panel):
	"""docstring for ContentViewUI"""
	def __init__(self, parent, id = -1, curPath = "", viewCtr = None, params = {}):
		self.initParams(params);
		super(ContentViewUI, self).__init__(parent, id, pos = self.__params["pos"], size = self.__params["size"], style = self.__params["style"]);
		self._className_ = ContentViewUI.__name__;
		self._curPath = curPath;
		self.__viewCtr = viewCtr;
		self.__replaceCache = []; # 替换缓存
		self.__farCtx = None; # 结果显示区
		self.__undoReplaceBtn = None; # 撤销替换按钮

	def initParams(self, params):
		# 初始化参数
		self.__params = {
			"pos" : (0,0),
			"size" : (640,-1),
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
		self.createTitle();
		self.createDirPath();
		self.createContent();
		pass;
		
	def initViewLayout(self):
		box = wx.BoxSizer(wx.VERTICAL);
		box.Add(self.__title, flag = wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border = 10);
		box.Add(self.__dirPath, flag = wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border = 10);
		box.Add(self.__content, flag = wx.ALIGN_CENTER|wx.TOP, border = 10);
		self.SetSizerAndFit(box);
		pass;

	def updateView(self, data):
		pass;

	def createTitle(self):
		self.__title = wx.StaticText(self, label = "文件名称批量查找与替换");
		self.__title.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD));
		
	def createDirPath(self):
		self.__dirPath = wx.Panel(self, size = (self.GetSize().x, -1));
		tips = wx.StaticText(self.__dirPath, label = "- 请输入文件夹路径 -");
		tips.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL));
		tips.SetForegroundColour("gray");
		def onInput(value, callback = None):
			ret, label = self.checkDirPath(value);
			if ret:
				_GG("CacheManager").setCache("selectedDirPath", value);
				tips.SetLabel("");
				tips.SetForegroundColour("gray");
			else:
				tips.SetLabel("- "+ label +" -");
				tips.SetForegroundColour(wx.Colour(255,36,36));
			if callable(callback):
				return callback(value);
			pass;
		div = DirInputView(self.__dirPath, params = {
			"inputSize" : (self.GetSize().x - 60, 30),
			"inputValue" : _GG("CacheManager").getCache("selectedDirPath", ""),
			"buttonSize" : (60, 30),
			"buttonLabel" : "选择目录",
			"onInput" : onInput,
		});
		onInput(_GG("CacheManager").getCache("selectedDirPath", ""));
		# 布局
		box = wx.BoxSizer(wx.VERTICAL);
		box.Add(div, flag = wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM|wx.EXPAND, border = 5);
		box.Add(tips, flag = wx.ALIGN_CENTER|wx.BOTTOM, border = 5);
		self.__dirPath.SetSizerAndFit(box);

	def createContent(self):
		self.__content = wx.Panel(self, size = (self.GetSize().x, -1));
		dirTrees = self.createDirTrees(self.__content);
		far = self.createFindAndReplace(self.__content);
		# 布局
		box = wx.BoxSizer(wx.HORIZONTAL);
		box.Add(dirTrees);
		box.Add(far);
		self.__content.SetSizerAndFit(box);

	def createDirTrees(self, parent):
		dirTrees = wx.Panel(parent, size = (240, -1), style = wx.BORDER_THEME);
		btn = wx.Button(dirTrees, label = "生成树状图");
		tc = wx.TreeCtrl(dirTrees, size = (dirTrees.GetSize().x, 440), style = wx.TR_HIDE_ROOT|wx.TR_LINES_AT_ROOT|wx.TR_HAS_BUTTONS);
		tc.AddRoot("root");
		# 布局
		box = wx.BoxSizer(wx.VERTICAL);
		box.Add(btn, flag = wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border = 5);
		box.Add(tc, flag = wx.ALIGN_CENTER|wx.TOP|wx.EXPAND, border = 5);
		dirTrees.SetSizerAndFit(box);
		# 响应按钮事件
		def onClick(event):
			root = tc.GetRootItem();
			tc.DeleteChildren(root);
			self.updateDirTree(tc, root, _GG("CacheManager").getCache("selectedDirPath", ""), maxLevel = _GG("CacheManager").getCache("maxLevel", 10));
		btn.Bind(wx.EVT_BUTTON, onClick);
		return dirTrees;

	def createFindAndReplace(self, parent):
		far = wx.Panel(parent, size = (parent.GetSize().x - 240, -1), style = wx.BORDER_THEME);
		findIb = self.createInputBtn(far, label = "查找");
		replaceIb = self.createInputBtn(far, label = "替换");
		ext = self.createReplaceExtend(far);
		ctx = wx.TextCtrl(far, size = (far.GetSize().x, 400), value = "- 结果显示区 -", style = wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_RICH);
		# 布局
		box = wx.BoxSizer(wx.VERTICAL);
		box.Add(findIb, flag = wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border = 5);
		box.Add(replaceIb, flag = wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border = 5);
		box.Add(ext, flag = wx.ALIGN_CENTER);
		box.Add(ctx, flag = wx.ALIGN_CENTER|wx.TOP|wx.EXPAND, border = 5);
		far.SetSizerAndFit(box);
		# 响应按钮事件
		def onClickFindIB(textCtrl):
			ctx.SetValue("");
			ret, label = self.checkDirPath(_GG("CacheManager").getCache("selectedDirPath", ""));
			if not ret:
				self.appendRichTextTo(ctx, "Warning:"+ label +"！\n", style = "warning");
				return;
			if not textCtrl.GetValue():
				self.appendRichTextTo(ctx, "Warning:查找输入框不能为空！\n", style = "warning");
				return;
			self.appendRichTextTo(ctx, "---- 开始查找 ---- \n", style = "normal");
			ignoreCase, maxLevel = _GG("CacheManager").getCache("ignoreCase", False), _GG("CacheManager").getCache("maxLevel", 10);
			self.findByDirPath(ctx, _GG("CacheManager").getCache("selectedDirPath", ""), findStr = textCtrl.GetValue(), ignoreCase = ignoreCase, maxLevel = maxLevel);
			self.appendRichTextTo(ctx, "---- 查找结束 ---- \n", style = "normal");
		def onClickReplaceIB(textCtrl):
			ctx.SetValue("");
			ret, label = self.checkDirPath(_GG("CacheManager").getCache("selectedDirPath", ""));
			if not ret:
				self.appendRichTextTo(ctx, "Warning:"+ label +"！\n", style = "warning");
				return;
			if not findIb._input.GetValue():
				self.appendRichTextTo(ctx, "Warning:查找输入框不能为空！\n", style = "warning");
				return;
			self.appendRichTextTo(ctx, "---- 开始替换 ---- \n", style = "normal");
			ignoreCase, maxLevel = _GG("CacheManager").getCache("ignoreCase", False), _GG("CacheManager").getCache("maxLevel", 10);
			self.replaceByDirPath(ctx, _GG("CacheManager").getCache("selectedDirPath", ""), findStr = findIb._input.GetValue(), replaceStr = textCtrl.GetValue(), ignoreCase = ignoreCase, maxLevel = maxLevel);
			self.appendRichTextTo(ctx, "---- 替换结束 ---- \n", style = "normal");
			# 更新替换撤销按钮
			if self.__replaceCache:
				self.__undoReplaceBtn.Enable(True);
		findIb.onClickBtn = onClickFindIB;
		replaceIb.onClickBtn = onClickReplaceIB;
		# 缓存结果显示区
		self.__farCtx = ctx;
		return far;

	# 创建替换的扩展
	def createReplaceExtend(self, parent):
		ext = wx.Panel(parent, size = (parent.GetSize().x, -1), style = wx.BORDER_THEME);
		undo = wx.Button(ext, label = "撤销上一步有效替换");
		undo.Bind(wx.EVT_BUTTON, self.undoReplace); # 设置撤销替换事件
		undo.Enable(False);
		# 布局
		box = wx.BoxSizer(wx.HORIZONTAL);
		box.Add(undo, flag = wx.ALIGN_CENTER|wx.ALL, border = 5);
		ext.SetSizerAndFit(box);
		# 缓存相关按钮
		self.__undoReplaceBtn = undo;
		return ext;

	def createInputBtn(self, parent, label = "按钮文本", onClickBtn = None):
		inputBtn = wx.Panel(parent);
		inputBtn.onClickBtn = onClickBtn;
		textCtrl = wx.TextCtrl(inputBtn, size = (parent.GetSize().x - inputBtn.GetSize().x, -1));
		btn = wx.Button(inputBtn, label = label);
		# 布局
		box = wx.BoxSizer(wx.HORIZONTAL);
		box.Add(textCtrl, flag = wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT|wx.EXPAND, border = 5);
		box.Add(btn, flag = wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border = 5);
		inputBtn.SetSizerAndFit(box);
		# 设置点击事件
		def clickCallback(event):
			if callable(inputBtn.onClickBtn):
				inputBtn.onClickBtn(textCtrl);
			pass;
		btn.Bind(wx.EVT_BUTTON, clickCallback);
		inputBtn._input = textCtrl;
		return inputBtn;

	def updateDirTree(self, dirTree, parentItem, dirPath, level = 1, maxLevel = 1):
		if os.path.exists(dirPath) and os.path.isdir(dirPath):
			for file in os.listdir(dirPath):
				item = dirTree.AppendItem(parentItem, file);
				if os.path.isdir(os.path.join(dirPath, file)) and level <= maxLevel:
					self.updateDirTree(dirTree, item, os.path.join(dirPath, file), level = level + 1, maxLevel = maxLevel);
		pass;

	def appendRichTextTo(self, textCtrl, text, style = ""):
		if not text:
			return;
		attr = None;
		if style == "normal":
			attr = wx.TextAttr(wx.Colour(100, 100, 100), font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL));
		elif style == "bold":
			attr = wx.TextAttr(wx.Colour(0, 0, 0), font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD));
		elif style == "error":
			attr = wx.TextAttr(wx.Colour(255, 0, 0), font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD));
		elif style == "warning":
			attr = wx.TextAttr(wx.Colour(218,165,32), font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD));
		# 添加富文本
		if attr:
			default = textCtrl.GetDefaultStyle();
			textCtrl.SetDefaultStyle(attr);
			textCtrl.AppendText(text);
			textCtrl.SetDefaultStyle(default);
		else:
			textCtrl.AppendText(text);
		pass;

	def findByDirPath(self, textCtrl, dirPath, srcPath = "", findStr = "", level = 1, ignoreCase = False, maxLevel = 1):
		if findStr and os.path.exists(dirPath) and os.path.isdir(dirPath):
			if not srcPath:
				srcPath = dirPath;
			for file in os.listdir(dirPath):
				# 正则匹配进行查找
				flags = 0;
				if ignoreCase:
					flags = re.I;
				mt = re.match("(.*)("+ findStr +")(.*)", file, flags = flags);
				if mt:
					g1, g2, *sg, g3 = mt.groups();
					g1 = os.path.join(dirPath.replace(srcPath, ""), g1);
					if g1 and (g1[0] == "\\" or g1[0] == "/"):
						g1 = g1[1:];
					self.appendRichTextTo(textCtrl, f"* {g1}", style = "normal");
					self.appendRichTextTo(textCtrl, g2, style = "bold");
					self.appendRichTextTo(textCtrl, g3 + "\n", style = "normal");
				# 递归进行查找
				if os.path.isdir(os.path.join(dirPath, file)) and level <= maxLevel:
					self.findByDirPath(textCtrl, os.path.join(dirPath, file), srcPath = srcPath, findStr = findStr, level = level + 1, ignoreCase = ignoreCase, maxLevel = maxLevel);
		pass;

	def replaceByDirPath(self, textCtrl, dirPath, srcPath = "", findStr = "", replaceStr = "", level = 1, ignoreCase = False, maxLevel = 1):
		if findStr and os.path.exists(dirPath) and os.path.isdir(dirPath):
			if level == 1:
				self.__replaceCache = []; # 清除缓存
			if not srcPath:
				srcPath = dirPath;
			for file in os.listdir(dirPath):
				# 递归进行替换
				if os.path.isdir(os.path.join(dirPath, file)) and level <= maxLevel:
					self.replaceByDirPath(textCtrl, os.path.join(dirPath, file), srcPath = srcPath, findStr = findStr, replaceStr = replaceStr, level = level + 1, ignoreCase = ignoreCase, maxLevel = maxLevel);
				# 正则匹配进行查找
				flags = 0;
				if ignoreCase:
					flags = re.I;
				mt = re.match("(.*)("+ findStr +")(.*)", file, flags = flags);
				if mt:
					g1, g2, *sg, g3 = mt.groups();
					g1 = os.path.join(dirPath.replace(srcPath, ""), g1);
					if g1 and (g1[0] == "\\" or g1[0] == "/"):
						g1 = g1[1:];
					self.appendRichTextTo(textCtrl, f"* {g1}", style = "normal");
					self.appendRichTextTo(textCtrl, g2, style = "bold");
					self.appendRichTextTo(textCtrl, g3 + " -> ", style = "normal");
					try:
						diff = replaceStr.count("{}") - len(sg); # 获取占位符与参数差值
						if diff > 0:
							sg.extend([""]*diff);
						replaceStr = replaceStr.format(*sg); # 填充占位符
						srcFilePath, targetFilePath = os.path.join(dirPath, file), os.path.join(srcPath, g1 + replaceStr + g3);
						# 重命名
						os.rename(srcFilePath, targetFilePath);
						# 添加缓存
						self.__replaceCache.append((srcPath, g1, (g2, replaceStr), g3));
						# 添加重命名结果
						self.appendRichTextTo(textCtrl, g1, style = "normal");
						self.appendRichTextTo(textCtrl, replaceStr, style = "bold");
						self.appendRichTextTo(textCtrl, g3, style = "normal");
					except Exception as e:
						self.appendRichTextTo(textCtrl, f"替换失败！Error: {e}.", style = "error");
					self.appendRichTextTo(textCtrl, "\n", style = "normal");
		pass;

	def checkDirPath(self, dirPath):
		if not dirPath:
			return False, "输入路径不能为空";
		elif not os.path.exists(dirPath):
			return False, "输入路径不存在";
		elif not os.path.isdir(dirPath):
			return False, "输入路径不是文件夹";
		return True, "";

	def undoReplace(self, event = None):
		if not self.__farCtx:
			return;
		self.__farCtx.SetValue("");
		self.appendRichTextTo(self.__farCtx, "---- 开始撤销替换 ---- \n", style = "normal");
		for i in range(len(self.__replaceCache)-1, -1, -1):
			try:
				srcPath, g1, g2, g3 = self.__replaceCache[i];
				findStr, replaceStr = g2;
				# 设置结果内容
				self.appendRichTextTo(self.__farCtx, f"* {g1}", style = "normal");
				self.appendRichTextTo(self.__farCtx, replaceStr, style = "bold");
				self.appendRichTextTo(self.__farCtx, f"{g3} -> ", style = "normal");
				# 校验目录
				srcFilePath, targetFilePath = os.path.join(srcPath, g1 + replaceStr + g3), os.path.join(srcPath, g1 + findStr + g3);
				if os.path.exists(srcFilePath):
					os.rename(srcFilePath, targetFilePath); # 重命名
					# 设置结果内容
					self.appendRichTextTo(self.__farCtx, g1, style = "normal");
					self.appendRichTextTo(self.__farCtx, findStr, style = "bold");
					self.appendRichTextTo(self.__farCtx, g3, style = "normal");
				else:
					self.appendRichTextTo(self.__farCtx, f"所要替换的文件（夹）不存在！", style = "error");
			except Exception as e:
				self.appendRichTextTo(self.__farCtx, f"替换失败！Error: {e}.", style = "error");
			self.appendRichTextTo(self.__farCtx, "\n", style = "normal");
		self.appendRichTextTo(self.__farCtx, "---- 撤销替换结束 ---- \n", style = "normal");
		self.__replaceCache = []; # 重置替换缓存
		self.__undoReplaceBtn.Enable(False); # 重置撤销替换按钮
